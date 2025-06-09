import json
import os

from avi.sdk.avi_api import ApiSession

from requests.packages import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

Controller_Version = "20.1.6"

demo_env= {
    'name' : 'RegionA',
    'controller_username': "admin",
    'controller_password': "VMware123!",
    'controller_ip': "avicon-01a.vcf.sddc.lab",
    'tenant': "admin",
    'api_version': Controller_Version,
    'zap_proxy': "http://avitools.vcf.sddc.lab:8080",
    'zap_apikey': "avi123",
    'cloud': "Default-Cloud",
    'proxies': {
            # Only needed for VMware Lab Testbeds
            },
    'headers': {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:66.0) Gecko/20100101 Firefox/66.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'X-AVI-VERSION': Controller_Version
            },
    'vses': {
        'Hackazon' : {
            'pool_servers' : {
                'server1' : {
                    'pool_server_ip': "192.168.120.11",
                    'pool_server_port': "30080"
                },
                'server2' : {
                    'pool_server_ip': "192.168.120.12",
                    'pool_server_port': "30080"
                },
            },
            'vip_ip': "192.168.130.131",
            'vs_name': "WAF-Hackazon-VS",
            'fqdn': "hackazon.region01a.vcf.sddc.lab",
            'pool_name': "Hackazon-Pool",
            'waf_profile_name': "HackazonProfile",
            'waf_policy_name': "HackazonPolicy",
            'error_page_profile_name': "HackazonErrorPage",
            'learning_group_name': 'Hackazon_Learning_Group_Demo'
        }
    }
}

def testbed_setup(testbed):
    print(f"Data for Testbed {testbed['name'].capitalize()}")
    print(f"Controller IP: {testbed['controller_ip']}")
    api = ApiSession.get_session(
        controller_ip=testbed['controller_ip'],
        username=testbed['controller_username'],
        password=testbed['controller_password'],
        tenant=testbed['tenant'],
        api_version=testbed['api_version']
        )

    for name, vs in testbed['vses'].items():
        print(f"{name} VIP: {vs['vip_ip']}")
        # get cloud uuid
        cloud = api.get_object_by_name('cloud', testbed['cloud'])
        cloud_ref = api.get_obj_ref(cloud)        
        
        #create pool obj
        print("Setting up Demo VS:" + name)
        pool_obj = {
            "lb_algorithm": 'LB_ALGORITHM_LEAST_CONNECTIONS',
            "default_server_port": 80,
            "name": vs['pool_name'],
            'cloud_ref': cloud_ref,
            "servers": [],
            "health_monitor_refs": ['/api/healthmonitor?name=System-TCP'],
        }
        for member_name, pool_member in vs['pool_servers'].items():
            server = { 'hostname' : member_name, 'ip' : { 'addr' : pool_member['pool_server_ip'], 'type' : 'V4'}, 'port' : pool_member['pool_server_port']}
            pool_obj['servers'].append(server)
        #print(pool_obj)
        resp = api.post('pool', data=json.dumps(pool_obj))
        print('- Create Pool', resp, resp.reason)

        #gather ref of new pool
        get_pool_obj = api.get_object_by_name('pool', vs['pool_name'])
        pool_ref = api.get_obj_ref(get_pool_obj)

        # Copy system WAF profile into new WAF profile for demo tweaking
        get_waf_profile = api.get_object_by_name('wafprofile', 'System-WAF-Profile')
        get_waf_profile['name'] = vs['waf_profile_name']
        resp = api.post('wafprofile', get_waf_profile)
        print("- Create new WAF profile", resp, resp.reason)
        get_profile_obj = api.get_object_by_name('wafprofile', vs['waf_profile_name'])
        profile = api.get_obj_ref(get_profile_obj)

        #get system WAF policy
        get_waf_obj = api.get_object_by_name('wafpolicy', 'System-WAF-Policy')
        get_waf_obj['name'] = vs['waf_policy_name']
        get_waf_obj['waf_profile_ref'] = profile

        #post copied WAF policy
        resp = api.post('wafpolicy', get_waf_obj)
        print("- Create new WAF Policy", resp, resp.reason)
        get_waf_obj = api.get_object_by_name('wafpolicy', vs['waf_policy_name'])
        waf_ref = api.get_obj_ref(get_waf_obj)
        # print "WAF", waf_ref

        # add backup passphrase if not present
        backupconf = api.get_object_by_name('backupconfiguration', 'Backup-Configuration')
        if backupconf['backup_passphrase'] == "":
            backupconf['backup_passphrase'] = 'notpresenttoavoiderror'
            resp = api.put('backupconfiguration/%s' %backupconf['uuid'], backupconf)
            print("Change Backup Configuration defaults", resp.text)

        #add custom error page
        error_page_body = api.get_object_by_name('errorpagebody', 'Custom-Error-Page')
        error_page_body_ref = api.get_obj_ref(error_page_body)

        error_page_profile = {
            'error_pages': [{
                'enable': True,
                'error_page_body_ref': error_page_body_ref,
                'index': 0,
                'match': {'match_criteria': 'IS_IN', 'status_codes': [403]}}],
            'name': vs['error_page_profile_name'],
        }

        resp = api.post('errorpageprofile', error_page_profile)
        print("- Create new Error Page Profile", resp, resp.reason)

        error_page_profile = api.get_object_by_name('errorpageprofile', vs['error_page_profile_name'])
        error_page_profile_ref = api.get_obj_ref(error_page_profile)


        # Add Datascript for Request-ID response Header
        dsname = "Request-ID-Header-%s" %vs['waf_policy_name']
        dsobject = {
           "evt" :  "VS_DATASCRIPT_EVT_HTTP_RESP",
           "script" : """r = avi.http.get_request_id()
                         if r == nil then
                           r = "none"
                         end
                         avi.http.add_header( "X-Request-Id", r )""",
           "name" : dsname,

        }
        dssetname = "DS-SET-Request-ID-Header-%s" %vs['waf_policy_name']
        dssetobject = {
            'datascript' : [
                dsobject,
            ],
            'name' : dssetname
        }
        resp = api.post('vsdatascriptset', data=json.dumps(dssetobject))
        print("- Create new Response Data Script", resp, resp.reason)

        ds = api.get_object_by_name('vsdatascriptset', dssetname)
        ds_ref = api.get_obj_ref(ds)

        #creating VSVIP
        vsvip_name = f"{name}_vsvip"
        vsvip_obj = {
            'cloud_ref': cloud_ref,
            'name': vsvip_name,
            'vip' : [
                {
                    'vip_id' : 0,
                    'ip_address': {
                        'addr': vs['vip_ip'],
                        'type': 'V4',
                    }
                },
            ],
            'dns_info' : [
                {
                    'fqdn': vs['fqdn'],
                    'ttl': 30,
                    'type': "DNS_RECORD_A",
                    'algorithm': 'DNS_RECORD_RESPONSE_CONSISTENT_HASH'
                    
                }
            ]
        }

        resp = api.post('vsvip', data=json.dumps(vsvip_obj))
        print("- Create VSVIP object", resp, resp.reason) #, resp.text

        #gather VSVIP ref
        get_vsvip_obj = api.get_object_by_name('vsvip', vsvip_name)
        vsvip_ref = api.get_obj_ref(get_vsvip_obj)

        # Creating VS
        services_obj = [{'port': 80, 'enable_ssl': False},{'port': 443, 'enable_ssl': True}]
        vs_obj = {
            'name': vs['vs_name'],
            'type': 'VS_TYPE_NORMAL',
            'vsvip_ref': vsvip_ref,
            'enabled': True,
            'services': services_obj,
            'application_profile_name': 'System-HTTP',
            'error_page_profile_ref': error_page_profile_ref,
            'pool_ref': pool_ref,
            'cloud_ref': cloud_ref,
            'waf_policy_ref' : waf_ref,
            'vs_datascripts' : [
                { 
                    'index' : 1,
                    'vs_datascript_set_ref' : ds_ref
                }
            ],
            'analytics_policy': {
                'udf_log_throttle': 10,
                'full_client_logs': {
                    'duration': 0,
                    'throttle': 10,
                    'enabled': True
                },
                'metrics_realtime_update': {
                    'duration': 0,
                    'enabled': True
                },
                'significant_log_throttle': 10,
                'client_insights': 'NO_INSIGHTS',
                'all_headers': True
            }
        }

        resp = api.post('virtualservice', data=json.dumps(vs_obj))
        print("- Create VS with new WAF Policy", resp, resp.reason) #, resp.text

    print('Setup done.')

def change_policy_mode(api, demo_env, vs, mode):
    wafpolicy_object = api.get_object_by_name('wafpolicy', demo_env['vses'][vs]['waf_policy_name'])
    wafpolicy_object['mode'] = mode
    resp = api.put_by_name('wafpolicy', demo_env['vses'][vs]['waf_policy_name'], wafpolicy_object)
    return (resp, resp.reason)

hackazon_vip = demo_env['vses']['Hackazon']['vip_ip']
#demo_env['controller_ip'] = "10.79.110.253"

### Import python packages to setup Demo environment.

### Test Connection to Controller
#The api object will serve as the interface to the Controller.

api = ApiSession.get_session(
    controller_ip=demo_env['controller_ip'],
    username=demo_env['controller_username'],
    password=demo_env['controller_password'],
    tenant=demo_env['tenant'],
    api_version=demo_env['api_version']
    )
print('Successful. Session ID:' + api.session_id)

tb = testbed_setup(demo_env)
change_policy_mode(api, demo_env, "Hackazon", "WAF_MODE_ENFORCEMENT")
