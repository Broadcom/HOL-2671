import copy
import json
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from urllib.parse import urlparse
import pyparsing as pp
import yaml
import re

root_dir = os.path.dirname(os.path.abspath(__file__))

irule_name = "irule_name"

# Constants to get the avi supported field from the irule field
constants = {
    "secure": "secure_cookie_enabled",
    "x_forwarded_proto": "x_forwarded_proto_enabled",
    "httponly": "httponly_enabled",
}

# To get the avi supported type based on the Irule config.
irule_type = {
    "app_profile": ["secure", "httponly", "x_forwarded_proto"],
    "persistence_profile": [],
}

variable_map = {}


def setup_logger():
    # Get the name of the current script file
    script_name = os.path.splitext(os.path.basename(__file__))[0]

    # Create a logger with the script name
    logger = logging.getLogger(script_name)
    logger.setLevel(logging.DEBUG)

    # Create a rotating file handler
    log_file = script_name + ".log"
    file_handler = RotatingFileHandler(
        log_file, maxBytes=1024 * 1024, backupCount=5
    )  # 1 MB max size, keep up to 5 backup files
    file_handler.setLevel(logging.DEBUG)

    # Create a console handler
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setLevel(logging.INFO)

    # Create a formatter for both handlers
    formatter = logging.Formatter(
        "%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s "
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add both handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger


logger = setup_logger()


def fill_template(template_path, values):
    with open(template_path, "r") as f:
        content = f.read()
        for key, value in values.items():
            content = content.replace(f"{{{{ {key} }}}}", str(value))
    return content


def parse_filled_yaml(filled_yaml_str):
    return yaml.safe_load(filled_yaml_str)


def process_rule(toks):
    logger.debug(f"process_rule: {toks.dump()}")
    logger.debug(f"process_rule: {toks.as_dict()}")
    ret = {"irule_custom_config": [], "irule_native_config": []}
    for avi_config in toks.when.asList():
        logger.debug(f"toks.when: {toks.when}")
        if avi_config == "event":
            data = {"rule_name": irule_name, "avi_config": {}, "type": "HTTPPolicySet"}
            ret["irule_custom_config"].append(data)
            return ret
        if avi_config.get("native_rules"):
            data = {"rule_name": irule_name, "avi_config": {}, "type": None}
            for rule in avi_config["native_rules"]:
                data["avi_config"].update(rule["rule"])
                data["type"] = rule["avi_type"]
            ret["irule_native_config"].append(data)
        if avi_config.get("rules"):
            for rule in avi_config["rules"]:
                if rule.get("match") and rule["match"].get("country_list"):
                    cl = rule["match"].pop("country_list")
                    data = {
                        "name": "%s-country-codes" % (irule_name),
                        "country_list": cl,
                        "tenant": "/api/tenant/?name=admin",
                        "rule_name": irule_name
                    }
                    
                    filled_yaml_str = fill_template(root_dir + "/templates/ipaddr_group.yml", data)
                    data = parse_filled_yaml(filled_yaml_str)
                    ret['irule_custom_config'].append(data)
            data = {
                "rules": avi_config["rules"],
                "name": irule_name,
                "scenario": avi_config["scenario"],
            }
            if avi_config["scenario"] == "network_security_policy":
                filled_yaml_str = fill_template(
                    root_dir + "/templates/process_network_policy_rule.yml", data
                )
            else:
                filled_yaml_str = fill_template(
                    root_dir + "/templates/process_rule.yml", data
                )
            data = parse_filled_yaml(filled_yaml_str)
            ret["irule_custom_config"].append(data)
    return ret


def _try_joining_header_op(actions):
    logger.debug(f"len(actions): {len(actions)}")
    logger.debug(f"actions: {actions}")
    if len(actions) == 1:
        return actions
    i = 0
    hdr_actions = [action for action in actions if "hdr_action" in action]
    ret = [action for action in actions if "hdr_action" not in action]
    while i < len(hdr_actions) - 1:
        cur_hdr_action = hdr_actions[i]["hdr_action"][0]
        next_hdr_action = hdr_actions[i + 1]["hdr_action"][0]
        if "match" in hdr_actions[i] or "match" in hdr_actions[i + 1]:
            ret.append(hdr_actions[i])
            ret.append(hdr_actions[i + 1])
            i += 2
        elif (
            cur_hdr_action["action"] == "HTTP_REMOVE_HDR"
            and next_hdr_action["action"] == "HTTP_ADD_HDR"
            and cur_hdr_action["hdr"]["name"] == next_hdr_action["hdr"]["name"]
        ):
            ret.append(hdr_actions[i + 1])
            ret[-1]["hdr_action"][0]["action"] = "HTTP_REPLACE_HDR"
            i += 2
        else:
            ret.append(hdr_actions[i])
            ret[-1]["hdr_action"].append(next_hdr_action)
            i += 2
    # updating header index
    for action in ret:
        ind = 1
        if "hdr_action" in action:
            for hdr_act in action.get("hdr_action"):
                hdr_act["hdr_index"] = ind
                ind += 1
    logger.debug(f"joining header op ret: {ret}")
    return ret


def process_when(toks):
    """
    Process the parse result for when block. Returns scenario and rules.
    If rules are presenting in toks, then it's returned from switch/if block
    Otherwise we need to create {'rules': list(rules)} at this level
    """
    logger.debug(f"process_when: {toks.dump()}")
    if 'event' in toks.statements.asList():
        return  toks.statements
    statements = _try_joining_header_op(toks.statements)
    security_rules = [statement for statement in statements if "action" in statement]
    for r in security_rules:
        act_dict = r["action"]
        if toks.scenario == "network_security_policy" and act_dict["action"] == "HTTP_SECURITY_ACTION_CLOSE_CONN":
            r["action"] = "NETWORK_SECURITY_POLICY_ACTION_TYPE_DENY"
    req_resp_rules = [
        statement
        for statement in statements
        if "action" not in statement and not statement.get("type", "") == "native" and
           any(re.compile(r'action$').search(key) for key in statement.keys())
    ]
    native_rules = [
        statement for statement in statements if statement.get("type", "") == "native"
    ]
    logger.debug(
        f"security_rules: {security_rules}, req_resp_rules: {req_resp_rules}, native_rules: {native_rules}"
    )
    ret = []
    i = 1
    for scenario, rules in [
        (toks.scenario if toks.scenario == 'network_security_policy' else 'http_security_policy', security_rules),
        (toks.scenario, req_resp_rules),
    ]:
        if len(rules) == 0:
            continue
        ret_rules = []
        for rule in rules:
            res = {
                "enable": True,
                "index": i,
                "name": irule_name + (f"_{i}" if i > 1 else ""),
            }
            if scenario == "network_security_policy":
                res["age"] = 0
                res["log"] = False
            logger.debug(f"adding rule {rule}")
            for k, v in rule.items():
                if k == "index":
                    continue
                res[k] = v
            i += 1
            ret_rules.append(res)
        ret.append({"scenario": scenario, "rules": ret_rules})
    ret.append({"native_rules": native_rules})
    return ret


def process_uri_rewrite(toks):
    logger.debug(f"process_uri_rewrite: {toks.dump()}")
    logger.debug(f"process uri rewrite toks: {toks}")
    logger.debug(f"process uri rewrite toks.uri: {toks.uri}")
    ret = {
        "rewrite_url_action": {
            "path": {
                "tokens": [{"str_value": toks.uri[0], "type": "URI_TOKEN_TYPE_STRING"}],
                "type": "URI_PARAM_TYPE_TOKENIZED",
            }
        }
    }
    if toks.query:
        ret["rewrite_url_action"]["query"] = {"keep_query": True}
    return ret


def process_respond_statement(toks):
    logger.debug(f"process_respond_statement: {toks.dump()}")
    logger.debug(f"process respond statement toks: {toks.as_dict()}")
    logger.debug(f"process respond statement toks.respond_body: {toks.respond_body}")
    if toks.respond_body.respond_code == "301":
        data = {"name": irule_name, "status_code": "HTTP_REDIRECT_STATUS_CODE_301"}
        filled_yaml_str = fill_template(root_dir + "/templates/redirect_rule.yml", data)
        data = parse_filled_yaml(filled_yaml_str)
        if toks.respond_body.get('port'):
            data['redirect_action']['port'] = int(toks.respond_body.port[-1])
        return data
    elif toks.respond_body.respond_code in ["302", "307"]:
        data = {"name": irule_name, "status_code": "HTTP_REDIRECT_STATUS_CODE_302"}
        filled_yaml_str = fill_template(root_dir + "/templates/redirect_rule.yml", data)
        data = parse_filled_yaml(filled_yaml_str)
        if toks.respond_body.get('port'):
            data['redirect_action']['port'] = int(toks.respond_body.port[-1])
        return data
    elif toks.respond_body.respond_code == "403":
        return {
            "action": {
                "action": "HTTP_SECURITY_ACTION_SEND_RESPONSE",
                "status_code": "HTTP_LOCAL_RESPONSE_STATUS_CODE_403",
            },
            "enable": True,
            "index": 1,
        }
    else:
        raise NotImplementedError


def process_redirect(toks):
    logger.debug(f"process_redirect {toks.dump()}")
    redirect_url = toks.redirect_url
    logger.debug(
        f"type of redirect_url: {type(redirect_url)}, len(redirect_url): {len(redirect_url)}"
    )
    logger.debug(f"redirect_url: {redirect_url}")
    ret = {
        "redirect_action": {
            "keep_query": True,
            "port": 443,
            "protocol": "HTTPS",
            "status_code": "HTTP_REDIRECT_STATUS_CODE_302",
        }
    }
    if len(redirect_url) == 3:
        if (
            redirect_url[0] == "https://"
            and "".join(redirect_url[1]) == "HTTP::host"
            and "".join(redirect_url[2]) == "HTTP::uri"
        ):
            return ret
        if redirect_url[0] == "https://":
            ret["redirect_action"]["protocol"] = "HTTPS"
            ret["redirect_action"]["port"] = 443
        elif redirect_url[0] == "http://":
            ret["redirect_action"]["protocol"] = "HTTP"
            ret["redirect_action"]["port"] = 80
        else:
            raise NotImplementedError
        if redirect_url[1] == "HTTP::host":
            ret["redirect_action"]["path"] = {
                "tokens": [
                    {"str_value": redirect_url[2], "type": "URI_TOKEN_TYPE_STRING"}
                ],
                "type": "URI_PARAM_TYPE_TOKENIZED",
            }
            return ret
        elif redirect_url[2] == "HTTP::uri":
            ret["redirect_action"]["host"] = {
                "tokens": [
                    {"str_value": redirect_url[1], "type": "URI_TOKEN_TYPE_STRING"}
                ],
                "type": "URI_PARAM_TYPE_TOKENIZED",
            }
            return ret
        else:
            raise NotImplementedError
    elif len(redirect_url) == 1:
        parsed_url = urlparse(redirect_url[0])
        if parsed_url.scheme == "http":
            ret["redirect_action"]["protocol"] = "HTTP"
            ret["redirect_action"]["port"] = 80
        host = parsed_url.netloc
        host, port = get_redirect_host_and_port(host)
        if port :
            ret["redirect_action"]["port"] = int(port)
        uri = parsed_url.path
        if parsed_url.query:
            uri = parsed_url.path + "?" + parsed_url.query
        ret["redirect_action"]["host"] = {
            "tokens": [{"str_value": host, "type": "URI_TOKEN_TYPE_STRING"}],
            "type": "URI_PARAM_TYPE_TOKENIZED",
        }
        if uri:
            ret["redirect_action"]["path"] = {
                "tokens": [{"str_value": uri, "type": "URI_TOKEN_TYPE_STRING"}],
                "type": "URI_PARAM_TYPE_TOKENIZED",
            }
        return ret
    elif len(redirect_url) == 2:
        logger.debug(f"redirect_url: {redirect_url}")
        if "".join(redirect_url[1]) == "HTTP::uri":
            parsed_url = urlparse(redirect_url[0])
            host = parsed_url.netloc
            host, port = get_redirect_host_and_port(host)
            if port:
                ret["redirect_action"]["port"] = int(port)
            ret["redirect_action"]["host"] = {
                "tokens": [{"str_value": host, "type": "URI_TOKEN_TYPE_STRING"}],
                "type": "URI_PARAM_TYPE_TOKENIZED",
            }
            return ret
        else:
            raise NotImplementedError
    elif len(redirect_url) == 5:
        if toks.get('port'):
            if redirect_url[0] == "https://":
                ret["redirect_action"]["protocol"] = "HTTPS"
                ret["redirect_action"]["port"] = int(toks.port.asList()[1])
            elif redirect_url[0] == "http://":
                ret["redirect_action"]["protocol"] = "HTTP"
                ret["redirect_action"]["port"] = int(toks.port.asList()[1])
        else:
            ret["redirect_action"]["host"] = {
                "tokens": [
                    {"end_index": 65535, "start_index": 0, "type": "URI_TOKEN_TYPE_HOST"},
                    {"str_value": redirect_url[3], "type": "URI_TOKEN_TYPE_STRING"},
                ],
                "type": "URI_PARAM_TYPE_TOKENIZED",
            }
        return ret

    else:
        raise NotImplementedError

def get_redirect_host_and_port(host):
    port = None
    if ":" in host:
        port = host.split(":")[-1]
        host = host.split(":")[0]
    return host , port

def process_name(toks):
    global irule_name
    irule_name = toks[0].split("/")[-1]
    return irule_name


def funct_mapping(toks):
    with open(root_dir + "/templates/function_mapping.json", "r") as f:

        function_map = json.load(f)

        for map in function_map:
            if toks == map["function"]:
                return map["mapping"]


def request_condition_mapping(toks):
    with open(root_dir + "/templates/request_condition_mapping.json", "r") as f:
        function_map = json.load(f)
        for m in function_map:
            if toks == m["condition"]:
                return m["mapping"]


def process_switch_case(toks):
    """
    Process parsed result for switch case
    :param toks: parsing result
    :return: a dict of switch_rule.yml template
    """
    logger.debug(f"process_switch_case {toks.dump()}")
    logger.debug(f"toks.match_str is {toks.match_str}")
    logger.debug(f"toks.switch_action {toks.switch_action}")
    actions = {}
    if not toks.switch_action:
        return toks

    for action in toks.switch_action:
        for k, v in action.items():
            actions[k] = v

    return {"match_str": list(toks.match_str), "actions": actions}


def process_switch_condition(toks):
    logger.debug(f"process_switch_condition: {toks.dump()}")
    check_fields = toks[0].check_fields if toks[0].check_fields else toks[0]
    logger.debug(f"switch condition check_fields: {check_fields}")
    toks = [tok for tok in toks[0]] if not isinstance(toks[0], str) else [toks[0]]
    ret = {"match": {}}
    if (
        check_fields == "HTTP::uri"
        or check_fields == "HTTP::path"
        or "HTTP::path" in check_fields.as_list()
        or "HTTP::uri" in check_fields.as_list()
    ):
        ret["match"]["path"] = {"match_case": "INSENSITIVE", "match_criteria": "EQUALS"}
    if check_fields == "HTTP::host" or "HTTP::host" in check_fields.as_list():
        ret["match"]["host_hdr"] = {
            "match_case": "INSENSITIVE",
            "match_criteria": "HDR_EQUALS",
        }
    if check_fields == 'IP::client_addr' or 'IP::client_addr' in check_fields.as_list():
        if "country" in toks:
            ret["match"]["country_list"] = []
            ret['match']['client_ip'] = {
                "match_criteria": "IS_IN",
                "group_refs": ["/api/ipaddrgroup/?name=%s-country-codes" % irule_name]
            }
    if not ret["match"]:
        raise NotImplementedError
    return ret


def _parse_full_url(fullurl):
    if "/" not in fullurl:
        return fullurl, ""
    if not fullurl.startswith(("http://", "https://")):
        fullurl = "http://" + fullurl
    logger.debug(f"parsing full url {fullurl}")
    parsed_url = urlparse(fullurl)
    host = parsed_url.netloc
    uri = parsed_url.path
    logger.debug(f"parsed host: {host}, parsed uri {uri}")
    return host, uri


def process_switch(toks):
    """
    Process parsed result for switch block
    :param toks: parsing result
    :return: a dict of http_request_policy
    """
    logger.debug(f"process_switch: {toks.dump()}")
    logger.debug(
        f"toks.switch_cases and type: { {str(x): type(x) for x in toks.switch_cases} }"
    )
    logger.debug(f"toks.switch_conditions: {toks.switch_condition}")
    rules = []
    idx, ind = 1, 1
    path_match_list = []
    hdr_value_list = []
    switch_condition = toks.switch_condition
    default_match = {"host_hdr": {"value": []}, "path": {"match_str": []}}
    set_default_match = True
    while idx <= len(toks.switch_cases):
        switch_case = toks.switch_cases[idx - 1]
        logger.debug(f"switch_case: {switch_case}. Type: {type(switch_case)}")
        if isinstance(switch_case, str):
            host, uri = _parse_full_url(switch_case)
            if uri:
                if uri.startswith("*") and uri.endswith("*"):
                    criteria = "CONTAINS"
                elif uri.startswith("*"):
                    criteria = "ENDS_WITH"
                elif uri.endswith("*"):
                    criteria = "BEGINS_WITH"
                else:
                    criteria = "EQUALS"
                path_match_list.append("".join([c for c in uri if c != "*"]))
            if host:
                if host.startswith("*") and host.endswith("*"):
                    criteria = "HDR_CONTAINS"
                elif host.startswith("*"):
                    criteria = "HDR_ENDS_WITH"
                elif host.endswith("*"):
                    criteria = "HDR_BEGINS_WITH"
                else:
                    criteria = "HDR_EQUALS"
                hdr_value_list.append("".join([c for c in host if c != "*"]))
            idx += 1

            continue
        for match in switch_case['match_str']:
            host, uri = _parse_full_url(match)
            if uri:
                path_match_list.append("".join([c for c in uri if c != "*"]))
            if host:
                hdr_value_list.append("".join([c for c in host if c != "*"]))
                if "country_list" in switch_condition["match"]:
                    switch_condition["match"]["country_list"].append(hdr_value_list[0])
                    hdr_value_list = []

        rule = {"enable": True, "index": ind}
        logger.debug(f"creating rule with path match list {path_match_list}")
        logger.debug(f"creating rule with hdr value list {hdr_value_list}")
        for k, v in switch_case["actions"].items():
            rule[k] = v
        if switch_case["match_str"][0] != "default":
            for k, v in switch_condition.items():
                rule[k] = v
            if "path" in rule["match"]:
                set_default_match = False
                if uri.startswith("*") and uri.endswith("*"):
                    rule["match"]["path"]["match_criteria"] = "CONTAINS"
                elif uri.startswith("*"):
                    rule["match"]["path"]["match_criteria"] = "ENDS_WITH"
                elif uri.endswith("*"):
                    rule["match"]["path"]["match_criteria"] = "BEGINS_WITH"
                else:
                    rule["match"]["path"]["match_criteria"] = "EQUALS"
                rule["match"]["path"]["match_str"] = []
                rule["match"]["path"]["match_str"].extend([x for x in path_match_list])
                default_match["path"]["match_str"].extend([x for x in path_match_list])
            if "host_hdr" in rule["match"]:
                set_default_match = False
                if host.startswith("*") and host.endswith("*"):
                    rule["match"]["host_hdr"]["match_criteria"] = "HDR_CONTAINS"
                elif host.startswith("*"):
                    rule["match"]["host_hdr"]["match_criteria"] = "HDR_ENDS_WITH"
                elif host.endswith("*"):
                    rule["match"]["host_hdr"]["match_criteria"] = "HDR_BEGINS_WITH"
                else:
                    rule["match"]["host_hdr"]["match_criteria"] = "HDR_EQUALS"

                rule["match"]["host_hdr"]["value"] = []
                rule["match"]["host_hdr"]["value"].extend([x for x in hdr_value_list])
                default_match["host_hdr"]["value"].extend([x for x in hdr_value_list])
        else:
            if set_default_match:
                for k, v in switch_condition.items():
                    rule[k] = v
                logger.debug("Setting default match")
                if "path" in rule["match"]:
                    set_default_match = False
                    rule["match"]["path"]["match_str"] = []
                    rule["match"]["path"]["match_str"].extend(
                        [x for x in path_match_list]
                    )
                    with open(root_dir + "/templates/not_mapping.json", "r") as f:
                        content = f.read()
                        m = json.loads(content)
                        rule["match"]["path"]["match_criteria"] = m["path"][criteria]
                if "host_hdr" in rule["match"]:
                    set_default_match = False
                    rule["match"]["host_hdr"]["value"] = []
                    rule["match"]["host_hdr"]["value"].extend(
                        [x for x in hdr_value_list]
                    )
                    with open(root_dir + "/templates/not_mapping.json", "r") as f:
                        content = f.read()
                        m = json.loads(content)
                        rule["match"]["host_hdr"]["match_criteria"] = m["host_hdr"][
                            criteria
                        ]
        rule["name"] = irule_name + f"_{ind}"
        logger.debug(f"current rule is {rule}")
        path_match_list.clear()
        hdr_value_list.clear()
        rules.append(copy.deepcopy(rule))
        idx += 1
        ind += 1
    return rules


def process_header_statement(toks):
    logger.debug(f"process_header_statement {toks}")

    if toks["header_op"]["hdr"]["name"].lower() in irule_type["app_profile"]:
        rule = {}
        if toks.header_op["action"] == "HTTP_ADD_HDR":
            rule = {constants[toks["header_op"]["hdr"]["name"].lower()]: True}
        if toks.header_op["action"] == "HTTP_REMOVE_HDR":
            rule = {constants[toks["header_op"]["hdr"]["name"].lower()]: False}
        return {"type": "native", "rule": rule, "avi_type": "ApplicationProfile"}
    return {"hdr_action": [toks["header_op"]]}


def process_header_op(toks):
    logger.debug(f"process_string_map {toks}")
    logger.debug(toks.dump())
    data = {"header_name": toks.header_name[0], "header_op": toks.op}
    filled_yaml_str = fill_template(root_dir + "/templates/header_op.yml", data)
    data = parse_filled_yaml(filled_yaml_str)
    if data["action"] == "remove":
        data["action"] = "HTTP_REMOVE_HDR"
    elif data["action"] == "insert":
        data["action"] = "HTTP_ADD_HDR"
    elif data["action"] == "replace":
        data["action"] = "HTTP_REPLACE_HDR"
    else:
        raise NotImplementedError

    if "header_val" in toks:
        header_val = ""
        value_var = False
        if isinstance(toks["header_val"][0], str) and toks["header_val"][0].startswith('['):
            toks["header_val"] = [[item.strip('[]')] for item in toks["header_val"]]
        if "::" in toks["header_val"][0][0]:
            if len(toks["header_val"][0]) == 1:
                header_val = funct_mapping(toks["header_val"][0][0])
                value_var = True
            elif len(toks["header_val"][0]) == 2:
                header_val = toks["header_val"][0][1]
            else:
                raise NotImplementedError
        else:
            header_val = toks.header_val[0]

        data["hdr"]["value"] = {}
        if not value_var:
            data["hdr"]["value"]["val"] = header_val
        else:
            data["hdr"]["value"]["var"] = header_val
    return data


def process_if_block(toks):
    logger.debug(f"processing if block toks: {toks.dump()}")
    statement = {k: v for list_item in toks[0] for (k, v) in list_item.items()}
    return statement


def process_whole_if_block(toks):
    idx = 1
    rules = []
    for i in range(len(toks)):
        rule = toks[i]
        rule["enable"] = True
        rule["index"] = idx
        idx += 1
        rules.append(rule)
    return rules


def process_class_match(toks):
    logger.debug(f"processing class match : {toks.dump()}")
    cm = {}
    value = "".join(toks[0].val)
    if value == "IP::client_addr":
        if "client_ip" not in cm:
            cm["client_ip"]= {"group_refs": []}
        kws = "/api/ipaddrgroup/?name={}".format(toks[0].kw)
        cm["client_ip"]["group_refs"].append(kws)
    else:
        raise NotImplementedError
    return cm


def process_ipaddr_check(toks):
    logger.debug(f"processing ip addr check : {toks.dump()}")
    ic = {}
    value = "".join(toks[0].val)
    if value == "IP::client_addr":
        ip, mask = toks[0].ipmask.split("/")
        prefixes = {"ip_addr": {"addr": ip, "type": "V4"}, "mask": int(mask)}
        ic["client_ip"] = {"match_criteria": "IS_IN",
                           "prefixes": [prefixes]}
    else:
        raise NotImplementedError
    return ic


def process_string_map(toks):
    logger.debug(f"process_string_map {toks}")
    if (
        "".join(toks.action_function) == "HTTP::path"
        and "".join(toks.action_source[0]) == "HTTP::path"
    ):

        source_path = toks.action_map[0][0].split("/")
        source_path = list(filter(('"').__ne__, source_path))
        new_path = toks.action_map[0][1].split("/")
        new_path = list(filter(('"').__ne__, new_path))

        path_token_list = []
        path_token_dict = {"path": {"tokens": []}}
        for src_index, src_value in enumerate(source_path):
            final_src_index = src_index
            for new_index, new_value in enumerate(new_path):
                path_token = {
                    "end_index": 0,
                    "start_index": 0,
                    "type": "URI_TOKEN_TYPE_PATH",
                }
                if new_value == src_value:
                    path_token["end_index"] = src_index
                    path_token["start_index"] = src_index
                    path_token_list.append(path_token)

        path_token["end_index"] = final_src_index + 1
        path_token["start_index"] = 65535
        path_token_list.append(path_token)
        path_token_dict["path"]["tokens"] = path_token_list

        data = {
            "path_token_dict": yaml.dump(path_token_dict, indent=8, default_style="")
        }

        filled_yaml_str = fill_template(
            root_dir + "/templates/rewrite_url_action_path.yml", data
        )
        data = parse_filled_yaml(filled_yaml_str)
        return data

    if (
        "".join(toks.action_function) == "HTTP::uri"
        and "".join(toks.action_source[0]) == "HTTP::uri"
    ):
        path_token_list = []
        path_token = {}
        path_token_dict = {"path": {"tokens": []}}

        path_token["str_value"] = toks.action_map[0][1].replace('"', "")
        path_token["type"] = "URI_TOKEN_TYPE_STRING"

        path_token_list.append(path_token)

        path_token_dict["path"]["tokens"] = path_token_list

        data = {
            "path_token_dict": yaml.dump(path_token_dict, indent=8, default_style="")
        }

        filled_yaml_str = fill_template(
            root_dir + "/templates/rewrite_url_action_path.yml", data
        )
        data = parse_filled_yaml(filled_yaml_str)
        return data


def process_node(toks):
    """
    Get pool with associated ip address
    """
    logger.debug(f"process_node {toks}")
    data = {
        "pool_name": "temp_pool",  # need to retrieve pool name from lookup process to retrieve pool with node IP address
        "server_hostname": "server1",  # need to retrieve server hostname from lookup process to retrieve pool with node IP address
        "server_ip": toks.action_node[1],
    }

    filled_yaml_str = fill_template(
        root_dir + "/templates/switch_server_pool_lookup.yml", data
    )
    data = parse_filled_yaml(filled_yaml_str)
    return data


def process_pool(toks):
    if any("member" in index for index in toks.pool_selection):
        data = {
            "pool_name": toks.pool_selection[0],
            "server_ip": toks.pool_selection[2],
        }

        filled_yaml_str = fill_template(
            root_dir + "/templates/switch_server_pool_lookup.yml", data
        )
        data = parse_filled_yaml(filled_yaml_str)
        return data

    else:
        data = {"pool_name": toks.pool_selection[0]}

        filled_yaml_str = fill_template(root_dir + "/templates/switch_pool.yml", data)
        data = parse_filled_yaml(filled_yaml_str)
        return data


def process_reject_action():
    return [{"action": {"action": "HTTP_SECURITY_ACTION_CLOSE_CONN"}}]


def process_header_check(toks):
    logger.debug(f"process header check {toks}")
    ret = {
        "hdrs": [
            {
                "hdr": toks.header_name,
                "match_case": "INSENSITIVE",
                "match_criteria": "HDR_EXISTS",
            }
        ]
    }
    return ret


def process_general_check(toks):
    logger.debug(f"process general check {toks}")
    logger.debug(f"process general check check_field {toks.check_field.dump()}")
    logger.debug(
        f"process general check check_field.check_fields {toks.check_field.check_fields}"
    )
    op = toks.binary_op
    check_field = (
        toks.check_field[0]
        if not toks.check_field.check_fields
        else toks.check_field.check_fields
    )
    if isinstance(check_field, str):
        check_field = [check_field]
    elif not check_field.header_field and not check_field.cookie_name:
        check_field = check_field.as_list()
    check_value = toks.check_value
    if toks.check_field.string_op == "tolower":
        check_value = check_value.lower()
        check_field = toks.check_field.check_fields.as_list()
    logger.debug(f"type of check_field: {type(check_field)}")
    logger.debug(f"checking field {check_field} with value {check_value}")
    if "HTTP::uri" in check_field or "HTTP::path" in check_field:
        ret = {
            "path": {
                "match_str": [toks.check_value],
                "match_case": "INSENSITIVE",
                "match_criteria": request_condition_mapping(toks.binary_op),
            }
        }
    elif "HTTP::status" in check_field:
        if op == "==":
            ret = {
                "status": {
                    "match_criteria": "IS_IN",
                    "status_codes": [int(toks.check_value)],
                }
            }
        elif op == "!=":
            ret = {
                "status": {
                    "match_criteria": "IS_NOT_IN",
                    "status_codes": [int(toks.check_value)],
                }
            }
        else:
            raise NotImplementedError
    elif "HTTP::host" in check_field:
        ret = {
            "host_hdr": {
                "match_case": "INSENSITIVE",
                "match_criteria": f"HDR_{request_condition_mapping(toks.binary_op)}",
                "value": [toks.check_value],
            }
        }
    elif check_field.cookie_name:
        ret = {
            "cookie": {
                "match_case": "INSENSITIVE",
                "match_criteria": f"HDR_{request_condition_mapping(toks.binary_op)}",
                "name": check_field.cookie_name,
                "value": [check_value],
            }
        }
    elif check_field.header_field:
        logger.debug("header field check")
        ret = {
            "hdrs": [
                {
                    "hdr": check_field.header_field,
                    "match_case": "INSENSITIVE",
                    "match_criteria": f"HDR_{request_condition_mapping(toks.binary_op)}",
                    "value": [check_value],
                }
            ]
        }
    else:
        raise NotImplementedError
    return ret


def process_string_value_getter(toks):
    logger.debug(f"string value getter toks {toks.dump()}")
    logger.debug(f"string value getter check fields {toks[0].check_fields}")
    return toks[0]


def load_not_mapping():
    with open(root_dir + "/templates/not_mapping.json", "r") as f:
        content = f.read()
        m = json.loads(content)
    return m


def process_cm_cond(toks):
    logger.debug(f"process class match cond toks.unary_op: {toks.unary_op}, toks.cm_conds: {toks.cm_conds}")
    m = load_not_mapping()
    op = m["status"]["IS_NOT_IN"]
    if toks.unary_op == "not" or toks.unary_op == "!":
        op = m["status"]["IS_IN"]
    if len(toks.cm_conds) == 1:
        toks.cm_conds[0]["client_ip"]["match_criteria"] = op
        return toks.cm_conds
    cms = {}
    gr = []
    logic_op = ""
    for cm in toks.cm_conds:
        if type(cm) == dict and "client_ip" in cm:
            if "client_ip" not in cms:
                cms["client_ip"] = {"group_refs": []}
            gr.extend(cm["client_ip"]["group_refs"])
        if type(cm) == str:
            if cm in ["or", "||"]:
                logic_op = "or"
            else:
                raise NotImplementedError
    if logic_op == "or":
        cms["client_ip"]["group_refs"] = gr
        cms["client_ip"]["match_criteria"] = op
    return cms


def process_unary_condition(toks):
    logger.debug(
        f"process unary condition toks.unary_op: {toks.unary_op}, toks.unary_cond: {toks.unary_cond}"
    )
    if toks.unary_op == "not" or toks.unary_op[0] == "!":
        m = load_not_mapping()
        for k, v in toks.unary_cond[0].items():
            if isinstance(v, list):
                v = v[0]
            if "match_criteria" in v:
                v["match_criteria"] = m[k][v["match_criteria"]]
        return toks.unary_cond[0]
    else:
        raise NotImplementedError


def process_binary_condition(toks):
    logger.debug(
        f"processing binary condition, first cond: {toks.first_cond}, second cond: {toks.second_cond}"
    )
    if toks.logic_op == "and" or toks.logic_op == "&&":
        ret = {}
        for k, v in toks.first_cond[0].items():
            ret[k] = v
        for k, v in toks.second_cond.items():
            ret[k] = v
    elif toks.logic_op == "or" or toks.logic_op == "||":
        ret = {}
        for k, v in toks.first_cond[0].items():
            ret[k] = v
        for k, v in toks.second_cond.items():
            if k in ret:
                if 'match_str' in ret[k]:
                    ret[k]['match_str'].extend(v.get('match_str'))
    else:
        raise NotImplementedError
    return ret


def process_if_case(toks):
    logger.debug(f"process if_case, if_condition: {toks.if_condition}")
    return {"match": toks.if_condition}


def process_scenario(toks):
    if toks[0] == "HTTP_REQUEST":
        return "http_request_policy"
    elif toks[0] == "HTTP_RESPONSE":
        return "http_response_policy"
    elif toks[0] == "CLIENT_ACCEPTED" or toks[0] == "FLOW_INIT":
        return "network_security_policy"
    else:
        raise NotImplementedError


def process_full_url(toks):
    toks = toks[0]
    logger.debug(f"full url toks {toks}")
    if (
        "HTTP::host" not in toks.asList()
        and "HTTP::uri" not in toks.asList()
        and "HTTP::path" not in toks.asList()
    ):
        return "".join(toks.asList())
    return toks


def process_respond_content(toks: pp.ParseResults):
    logger.debug(f"process respond url toks {toks}")
    if len(toks[0]) > 1:
        return " ".join(toks[0].asList())
    else:
        return toks


def process_set_statement(toks):
    variable_map[toks.variable_name] = toks.variable_value


def process_variable(toks):
    logger.debug(f"process variable toks {toks}")
    # slice the string to remove the $ sign
    label = toks[0][1:]
    if label in variable_map:
        return variable_map[label]
    else:
        return label


def process_cookie_statement(toks):
    logger.debug(f"process_cookie_statement: {toks.as_dict()}")
    config = {
        "type": "native",
        "rule": {
            constants[toks.cookie_type.lower()]: (
                True if toks.status == "enable" else False
            )
        },
        "avi_type": None,
    }
    if toks.cookie_type in irule_type["app_profile"]:
        config["avi_type"] = "ApplicationProfile"
    if toks.cookie_type in irule_type["persistence_profile"]:
        config["avi_type"] = "ApplicationPersistenceProfile"
    return config


def process_foreach_block(toks):
    logger.debug(f"process_foreach_block: {toks}")
    return toks[0]

def process_event_block(toks):
    return toks[0]

# Basic Definitions
Keyword = pp.Word(pp.alphanums + "_-")
Variable = pp.Combine(pp.Literal("$") + pp.Word(pp.alphanums + "_")).set_parse_action(
    process_variable
)
FunctionNamespace = Keyword + pp.Literal("::")
FunctionContent = pp.Forward()
Scenario = pp.Literal("HTTP_REQUEST") | pp.Literal("HTTP_RESPONSE") | pp.Literal("CLIENT_ACCEPTED") | pp.Literal("FLOW_INIT")


FunctionCallForward = pp.Forward()
FunctionCall = pp.nestedExpr("[", "]", content=FunctionContent)

Value = pp.Forward()

SimpleString = (
    pp.Literal('"').suppress()
    + pp.Word(pp.alphanums + "_/.-:*")
    + pp.Literal('"').suppress()
)


BinaryOperator = (
    pp.Literal("equals")
    | pp.Literal("starts_with")
    | pp.Literal("ends_with")
    | pp.Literal("eq")
    | pp.Literal("contains")
    | pp.Literal("exists")
    | pp.Literal("==")
    | pp.Literal("=")
    | pp.Literal("!=")
)("biop")

# Now, to handle the recursive nature, update the FunctionContent
FunctionContent << (
    (FunctionCall | FunctionNamespace) + BinaryOperator + (Keyword | SimpleString)
    | (FunctionNamespace + Keyword + Keyword)
    | (FunctionNamespace + Keyword)
    | Keyword + Keyword + Value
    | Keyword + Value + Keyword
)

simple_value_getter = (
    pp.Literal("[").suppress()
    + pp.Combine(Keyword + pp.Literal("::") + Keyword)
    + pp.Literal("]").suppress()
)
cookie_value_getter = pp.Group(
    pp.Literal("[").suppress()
    + pp.Literal("HTTP::cookie")
    + Keyword("cookie_name")
    + pp.Literal("]").suppress()
)
header_value_getter = pp.Group(
    pp.Literal("[").suppress()
    + pp.Literal("HTTP::header")
    + Keyword("header_field")
    + pp.Literal("]").suppress()
)
StringOp = pp.Literal("tolower")
value_getter = pp.Group(
    cookie_value_getter
    | header_value_getter
    | pp.Group(
        pp.Literal("[").suppress()
        + pp.Literal("string")
        + StringOp("string_op")
        + pp.OneOrMore(simple_value_getter)("check_fields")
        + pp.Literal("]").suppress()
    ).set_parse_action(process_string_value_getter)
    | pp.Group(
        pp.Literal("[").suppress()
        + pp.Literal("whereis")
        + pp.OneOrMore(simple_value_getter)('check_fields')
        + pp.Literal('country')
        + pp.Literal(']').suppress()
    ).set_parse_action(process_string_value_getter)
    | simple_value_getter
)

UnaryOperator = pp.Literal("not") | pp.Literal("!")
LogicOperator = (
    pp.Literal("and") | pp.Literal("or") | pp.Literal("||") | pp.Literal("&&")
)

OpenParen = pp.Literal("(").suppress()
CloseParen = pp.Literal(")").suppress()
OpenBrace = pp.Literal("{").suppress()
CloseBrace = pp.Literal("}").suppress()
If_then = pp.Literal("then").suppress()
If_command = pp.Literal("if").suppress()
ElseIf_command = pp.Literal("elseif").suppress()
Else_command = pp.Literal("else").suppress()
Foreach_command = pp.Literal("foreach").suppress()

StringPart = (
    (~UnaryOperator + pp.Word(pp.alphanums + "_/.-:*")) | Variable | FunctionCall
)
String = pp.QuotedString(quoteChar='"', escChar="\\")
Value << (StringPart | String)
RuleName = pp.Combine(pp.Char("/") + pp.Word(pp.alphanums + "_-./")).set_parse_action(
    process_name
)
Number = pp.Word(pp.nums)
IpField = pp.Word(pp.nums, max=3)
Mask = pp.Word(pp.nums, max=3)
IpAddr = pp.Combine(IpField + "." + IpField + "." + IpField + "." + IpField)
IpV4AddrMask = pp.Combine(IpField + "." + IpField + "." + IpField + "." + IpField + "/" + Mask)

header_op = pp.Literal("exists")

header_check = (
    pp.Literal("[").suppress()
    + pp.Literal("HTTP::header")
    + header_op("header_op")
    + Value("header_name")
    + pp.Literal("]").suppress()
).set_parse_action(process_header_check)

general_check = (
    value_getter("check_field") + BinaryOperator("binary_op") + Value("check_value")
).set_parse_action(process_general_check)

class_match_check = pp.nested_expr(
    "[", "]", content=pp.Literal("class match") + Value("val") + BinaryOperator + Keyword("kw")
).set_parse_action(process_class_match)

ipaddr_check = pp.nested_expr(
    "[", "]", content=pp.Literal("IP::addr") + Value("val") + BinaryOperator + IpV4AddrMask("ipmask")
).set_parse_action(process_ipaddr_check)

base_condition = general_check | header_check

Condition = pp.Forward()

nested_condition = OpenParen + Condition + CloseParen

unary_condition = (
    UnaryOperator("unary_op") + nested_condition("unary_cond")
).set_parse_action(process_unary_condition)

cm_cond = (
    pp.ZeroOrMore(OpenParen)
    + pp.Optional(UnaryOperator)("unary_op")
    + pp.ZeroOrMore(OpenParen)
    + pp.Group(
        class_match_check
        + pp.ZeroOrMore(
            pp.ZeroOrMore(CloseParen)
            + LogicOperator
            + pp.ZeroOrMore(OpenParen)
            + class_match_check
        )
    )("cm_conds")
    + pp.ZeroOrMore(CloseParen)
).set_parse_action(process_cm_cond)

binary_condition = (
    (nested_condition | unary_condition | base_condition)("first_cond")
    + LogicOperator("logic_op")
    + Condition("second_cond")
).set_parse_action(process_binary_condition)

Condition << (unary_condition | binary_condition | nested_condition | base_condition | cm_cond | ipaddr_check)

Priority = pp.Literal("priority") + Number
Comment = (pp.Literal("#") + pp.restOfLine).suppress()
AppService = (pp.Literal("app-service") + pp.restOfLine).suppress()

ComplexString = String | pp.Combine(String + Variable + String)
Expression = pp.Or([ComplexString, String, Variable, FunctionCall, LogicOperator])

funct_map_value = pp.Literal(" ")
with open(root_dir + "/templates/function_mapping.json", "r") as f:
    content = f.read()
    function_mapping = json.loads(content)
    for item in function_mapping:
        funct_map_value = funct_map_value | pp.Literal(item["function"])
    funct_map_value = funct_map_value | (pp.Literal("IP::") + IpAddr)

funct_map = pp.nestedExpr("[", "]", content=funct_map_value)

Statement = pp.Forward()

SwitchCondition = value_getter.set_parse_action(process_switch_condition)

# Switch case statement
SwitchCase = (
    pp.ZeroOrMore((StringPart | String | Keyword) + pp.Optional(pp.Suppress("-")))("match_str") +
    (OpenBrace + pp.ZeroOrMore(Statement)("switch_action") + CloseBrace)
).set_parse_action(process_switch_case)

Switch = (
    pp.Literal("switch")
    + pp.Optional(pp.Literal("-glob"))
    + pp.Optional(pp.Literal('"'))
    + SwitchCondition("switch_condition")
    + pp.Optional(pp.Literal('"'))
    + pp.Literal("{")
    + pp.OneOrMore(SwitchCase | Comment)("switch_cases")
    + pp.Literal("}")
).set_parse_action(process_switch)

dq = pp.Literal('"').suppress()

CookieStatement = (
    pp.Literal("HTTP::cookie")
    + pp.oneOf("secure httponly")("cookie_type")
    + pp.Word(pp.alphanums + "$")
    + pp.oneOf("enable disable")("status")
).set_parse_action(process_cookie_statement)

# If Block Statement
IfCase = (
    pp.Optional(OpenBrace)
    + Condition("if_condition")
    + pp.Optional(CloseBrace)
    + pp.Optional(If_then)
).set_parse_action(process_if_case)

IfBody =  OpenBrace + pp.ZeroOrMore(Comment) + pp.ZeroOrMore(Statement)("switch_actions") + CloseBrace

IfBlock = pp.Group(
    If_command + IfCase("if_cases") + IfBody("actions")
).set_parse_action(process_if_block)

forBody = OpenBrace + pp.ZeroOrMore(CookieStatement) + CloseBrace

ForEachBlock = pp.Group(Foreach_command + pp.SkipTo("{").suppress() + forBody)

ElseIfBlock = pp.ZeroOrMore(Comment) + pp.Group(
    ElseIf_command + IfCase("if_cases") + IfBody("actions")
).set_parse_action(process_if_block)

ElseBlock = pp.ZeroOrMore(Comment) + pp.Group(Else_command + IfBody("actions")).set_parse_action(
    process_if_block
)

# String Map Statement
String_map = (
    pp.Group(FunctionContent)("action_function")
    + pp.Literal("[")
    + pp.Literal("string map")
    + pp.nestedExpr("{", "}", content=pp.OneOrMore(Statement))("action_map")
    + FunctionCall("action_source")
    + pp.Literal("]")
)("string_map").set_parse_action(process_string_map)

# Node Switch
Node = (pp.Literal("node") + IpAddr + pp.OneOrMore(":" | Number))(
    "action_node"
).set_parse_action(process_node)

# Pool Switch
Pool = (
    pp.Literal("pool")
    + (
        StringPart
        + pp.Optional(pp.Literal("member") + IpAddr + pp.OneOrMore(":" | Number))
    )("pool_selection")
)("action_pool").set_parse_action(process_pool)

HeaderOp = (
    pp.Literal("remove")("op") + (String | StringPart)("header_name")
    | (pp.Literal("insert") | pp.Literal("replace"))("op")
    + (String | StringPart)("header_name")
    + (String | funct_map)("header_val")
).set_parse_action(process_header_op)

HeaderStatement = (pp.Literal("HTTP::header") + HeaderOp("header_op")).set_parse_action(
    process_header_statement
)

# Define the basic components of a domain
l1 = pp.Word(pp.alphas + pp.nums + '!.', pp.alphas + pp.nums + '-_!.')
label = pp.Word(pp.alphas + pp.nums + '!', pp.alphas + pp.nums + '-_?!')
tld = pp.Word(pp.alphas)

# Combine the components into a domain pattern
# A domain is one or more labels, followed by a dot, then a TLD
dot = pp.Literal(".")
slash = pp.Literal("/")
ques = pp.Literal("?")

domain = pp.Combine(pp.OneOrMore(label + dot) + tld)
path = pp.Combine(pp.OneOrMore(slash + pp.Optional(label)) + pp.Optional(dot + label))
p1 = pp.Combine(pp.OneOrMore(slash + pp.Optional(l1)) + pp.Optional(dot + l1))

Host = (
    Variable
    | (
        pp.OneOrMore(pp.Literal("[").suppress())
        + pp.Literal("HTTP::host")
        + pp.Literal("]").suppress()
    )
    + pp.Optional(dot + domain)
    | domain
    | label
)

Uri = (
    pp.Literal("[").suppress()
    + (pp.Literal("HTTP::uri") | pp.Literal("HTTP::path"))
    + pp.Literal("]").suppress()
) | path

U1 = (
    pp.Literal("[").suppress()
    + (pp.Literal("HTTP::uri") | pp.Literal("HTTP::path"))
    + pp.Literal("]").suppress()
) | p1

exp = Keyword + BinaryOperator + Keyword
Query = (
    ques
    + (exp | Keyword)
    + pp.Optional(pp.OneOrMore(pp.Literal("&") | pp.Literal(":") | (exp | Keyword)))
)

FU1 = (
    pp.Combine((pp.Literal("https") | pp.Literal("http")) + pp.Literal("://"))
    + Host("host")
    + pp.Optional(Uri)("path")
    + pp.Optional(pp.Combine(":") + Number)("port")
)

FU2 = (
    pp.Combine((pp.Literal("https") | pp.Literal("http")) + pp.Literal("://"))
    + Host("host")
    + pp.Optional(pp.Literal('"')).suppress()
    + pp.Optional(pp.Combine(":") + pp.Optional(pp.Literal('"')).suppress() + Number)("port")
    + pp.Optional(pp.Literal(']')).suppress()
    + pp.Optional(U1)("path")
    + pp.Optional(Query)("query")
)

FullUrl = pp.Group(FU2 | FU1).set_parse_action(process_full_url)

RespondContent = String | pp.nestedExpr("{", "}").set_parse_action(
    process_respond_content
)
RespondUrl = pp.Optional(dq) + FullUrl + pp.Optional(dq)

RespondBody = pp.Group(
    (pp.Literal("503")("respond_code"))
    | (
        pp.Combine(pp.Literal("30") + pp.Word(pp.nums, exact=1))("respond_code")
        + pp.Optional(pp.Literal("noserver"))
        + pp.Optional(dq)
        + pp.Literal("Location")
        + pp.Optional(dq)
        + RespondUrl("respond_url")
    )
    | (
        Number("respond_code")
        + pp.Literal("content")
        + RespondContent("respond_content")
    )
    | (
        Number("respond_code")
    )
)

RespondStatement = (
    pp.Literal("HTTP::respond") + RespondBody("respond_body")
).set_parse_action(process_respond_statement)

RedirectStatement = (
    pp.Literal("HTTP::redirect")
    + (
        pp.Optional(pp.Literal('"')).suppress()
        + FullUrl
        + pp.Optional(pp.Literal('"')).suppress()
    )("redirect_url")
).set_parse_action(process_redirect)

UriRewrite = (
    pp.OneOrMore(pp.Literal("HTTP::uri")| pp.Literal("HTTP::path"))
    + Uri("uri")
    + pp.Optional(pp.Literal("[HTTP::query]"))("query")
).set_parse_action(process_uri_rewrite)

RuleStatement = (
    RespondStatement
    | RedirectStatement
    | HeaderStatement
    | UriRewrite
    | CookieStatement
)

# Statements inside a when block
SetStatement = (pp.Group(pp.Literal("set") + Keyword + FunctionCall)).suppress()

Log = (pp.Literal("log") + pp.Optional(StringPart) + String).suppress()

SetStatement = (
    (pp.Literal("set") + label("variable_name") + Value("variable_value"))
    .set_parse_action(process_set_statement)
    .suppress()
)

IfStatement = (
    IfBlock + pp.Optional(ElseIfBlock) + pp.Optional(ElseBlock)
).set_parse_action(process_whole_if_block)

Event = (pp.Literal("event")
        + (pp.Literal("enable")
        | pp.Literal("disable"))
        + pp.Literal("all")
        + pp.Optional(";")).set_parse_action(process_event_block)
# IN THIS VERSION WE DO NOT DO ANYTHING WITH THE SET LINES, SO WE NEED TO SUPPRESS IT

Statement << (
    RuleStatement
    | SetStatement
    | IfStatement
    | ForEachBlock.set_parse_action(process_foreach_block)
    | Switch
    | Comment
    | Pool
    | Event
    # | Node
    | pp.Literal("drop").set_parse_action(process_reject_action)
    | pp.Literal("discard")
    | pp.Literal("return")
    | (pp.Literal("reject") | pp.Literal("LB::detach")).set_parse_action(
        process_reject_action
    )
    | RespondStatement.set_parse_action(process_respond_statement)
    | pp.Literal("persist") + pp.Literal("none")
    | Log
    | String_map
    | SetStatement
    | pp.Group(Variable + Expression)
    | pp.Group(Variable + Number + Keyword + Expression)
)

# Main when block
WhenBlock = (
    pp.Optional(Priority)
    + pp.Literal("when")
    + Scenario("scenario").set_parse_action(process_scenario)
    + pp.Optional(Priority)
    + pp.Literal("{")
    + pp.OneOrMore(Statement)("statements")
    + pp.Literal("}")
).set_parse_action(process_when)

# Rule definition
Rule = (
    pp.Literal("ltm")
    + pp.Literal("rule")
    + RuleName("rule_name")
    + pp.Literal("{")
    + pp.ZeroOrMore(AppService)
    + pp.ZeroOrMore(Comment)
    + pp.OneOrMore(WhenBlock)("when")
    + pp.Literal("}")
).set_parse_action(process_rule)


# Parsing the input
def parse_input(input_string):
    try:
        parsed_result = Rule.parseString(input_string)
        return parsed_result
    except NotImplementedError as e:
        logger.debug(
            "error in parsing irule %s --> %s"
            % (input_string, "not implemented syntax")
        )
        return {}
    except Exception as e:
        logger.debug("error in parsing irule %s --> %s" % (input_string, e))
        return {}


def parse_irule_for_f5_conv(f5_irule_data):
    irule_custom_config = []
    # Maintaining separate list for native config because native + custom config is supported for 1 irule.
    irule_native_config = []
    rule_to_f5_conf = {}
    for data in f5_irule_data:
        parsed_rule = parse_input(data)
        rule_to_f5_conf[irule_name] = data
        if parsed_rule and "ParseResults" in str(parsed_rule[0]):
            continue
        if parsed_rule and type(parsed_rule[0]) == dict:
            mig_irule = parsed_rule[0].get("irule_custom_config")
            if mig_irule:
                for rule in mig_irule:
                    irule_custom_config.append(rule)
            native_irule = parsed_rule[0].get("irule_native_config")
            if native_irule:
                irule_native_config.append(native_irule[0])
    return {
        "irule_custom_config": irule_custom_config,
        "irule_native_config": irule_native_config,
    }, rule_to_f5_conf


if __name__ == "__main__":
    file_path = root_dir + "/tests/bigip.conf"
    with open(file_path, "r") as file:
        f5_conf_details = file.read()
    logger.debug(
        "--------Starting the parsing for file %s --> %s" % (file_path, f5_conf_details)
    )
    result = parse_input(f5_conf_details)
    if result:
        yaml.dump(result[0], open(root_dir + "/output.yml", "w"))