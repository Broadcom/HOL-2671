import json
import requests

def handler(context, inputs):
    base_url = f"https://{inputs['controller']}"
    login_url = f"{base_url}/login"
    auth = {'username' : inputs['username'] , 'password': inputs['password']}
    api = requests.session()
    api.verify = False
    resp = api.post(login_url, json=auth)

    #build header dict
    hdr = {'X-Avi-Version': resp.json()['version']['Version']}
    hdr['X-CSRFToken'] = resp.cookies['csrftoken']
    hdr['Referer'] = base_url
    hdr['X-Avi-Tenant'] = inputs['tenant']
    hdr['Content-Type'] = "application/json"
    headers = hdr

    #query_params = {"name": args.pool}
    resp = api.get(f"{base_url}/api/healthmonitor", headers=headers).json()['results']
    hm_list = []
    for i in resp:
        hm_list.append(i['name'])
    jsonOut=json.dumps(inputs, separators=(',', ':'))
    print(hm_list)
    print("Inputs were {0}".format(jsonOut))

    return hm_list