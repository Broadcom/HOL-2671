import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import base64
# import paramiko
import ssl
import time
import functions.core_functions as core

debug = False
sslVerify = False
vSanTimeout = 2700

### Fleet Management Functions

def getEncodedToken(username, password):
    if debug:
        print(f"getEncodedToken")
    
    credentials = f"{username}:{password}"
    bytesCredentials = credentials.encode('utf-8')
    base64BytesCredentials = base64.b64encode(bytesCredentials)
    base64Cred = base64BytesCredentials.decode('utf-8')

    return base64Cred

def getProductsInEnvironments(inFqdn, token, verify):
    if debug:
        print(f"In: getAllEnvironments")

    try:
        url = f"https://{inFqdn}/lcm/lcops/api/v2/environments"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + token,
            'Accept': 'application/json'
        }

        payload = {}

        response = requests.get(url=url, data=payload, headers=headers, verify=verify )       
        response.raise_for_status
        jResponse = response.json()
        

        if not (response.status_code < 200 or response.status_code >= 300):
            for environment in jResponse:
                print(f'{environment["environmentName"]}')
                products = environment['products']
                for product in products:
                    print(f'{product["id"]}')

        else:
            print(f"INFO: Response Code: {str(response.status_code)}")
            print(json.dumps(jResponse, indent=4))
            return response.status_code
    
    except requests.exceptions.HTTPError as e:
        print(f"HTTP_ERROR: {e}")
    except requests.exceptions.ConnectionError as e:
        print(f"CONNECT_ERROR: {e}")
    except requests.exceptions.Timeout:
        print(f"TIMEOUT_ERROR: {e}")
    except requests.exceptions.RequestException as e:
        print(f"REQUEST_ERROR: {e}")

def getAllEnvironments(inFqdn, token, verify):
    if debug:
        print(f"In: getAllEnvironments")

    try:
        url = f"https://{inFqdn}/lcm/lcops/api/v2/environments"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + token,
            'Accept': 'application/json'
        }

        payload = {}

        response = requests.get(url=url, data=payload, headers=headers, verify=verify )       
        response.raise_for_status
        jResponse = response.json()
        

        if not (response.status_code < 200 or response.status_code >= 300):
            result = {}
            for environment in jResponse:
                env = environment["environmentName"]
                product_ids =[product['id'] for product in environment['products']]
                
                result[env] ={"products": product_ids}               
                
            return result
        else:
            print(f"INFO: Response Code: {str(response.status_code)}")
            print(json.dumps(jResponse, indent=4))
            return response.status_code
    
    except requests.exceptions.HTTPError as e:
        print(f"HTTP_ERROR: {e}")
    except requests.exceptions.ConnectionError as e:
        print(f"CONNECT_ERROR: {e}")
    except requests.exceptions.Timeout:
        print(f"TIMEOUT_ERROR: {e}")
    except requests.exceptions.RequestException as e:
        print(f"REQUEST_ERROR: {e}")

def getEnvironmentVmidByName(inFqdn, token, verify, envName):
    if debug:
        print(f"In: getEnvironmentVmidByName")

    try:
        url = f"https://{inFqdn}/lcm/lcops/api/v2/environments"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + token,
            'Accept': 'application/json'
        }

        payload = {}

        response = requests.get(url=url, data=payload, headers=headers, verify=verify )       
        response.raise_for_status
        jResponse = response.json()
        
        if not (response.status_code < 200 or response.status_code >= 300):
            for environment in jResponse:
                if environment["environmentName"] == envName:
                    return environment["environmentId"]
        else:
            print(f"INFO: Response Code: {str(response.status_code)}")
            print(jResponse)
            return response.status_code
    
    except requests.exceptions.HTTPError as e:
        print(f"HTTP_ERROR: {e}")
    except requests.exceptions.ConnectionError as e:
        print(f"CONNECT_ERROR: {e}")
    except requests.exceptions.Timeout:
        print(f"TIMEOUT_ERROR: {e}")
    except requests.exceptions.RequestException as e:
        print(f"REQUEST_ERROR: {e}")

def getCertificateVmidByAlias(inFqdn, token, verify, alias):
    
    if debug:
        print(f"In: getCertificateVmidByAlias")
    
    url = f"https://{inFqdn}/lcm/locker/api/certificates"
        
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Basic ' + token,
        'Accept': 'application/json'
    }
        
    try:
        print(f"TASK: Checking for Certificate (by Alias): {alias}")
        response = requests.get(url=url, headers=headers, verify=False )
        jResponse = response.json()
        
        if response.status_code < 200 or response.status_code >= 300:
            print(f"INFO: Response Code: {str(response.status_code)}")
            print(jResponse)
            response.raise_for_status
            return response.status_code
        else:
            print(json.dumps(jResponse, indent=4))
            for cert in jResponse:
                if (cert["alias"] == alias):
                    print(f"INFO: Certificate: {alias} found")
                    return cert["vmid"]
                else:
                    print(f"INFO: Certificate: {alias} not found")
                    return None

    except requests.exceptions.HTTPError as e:
        print(f"HTTP_ERROR: {e}")
    except requests.exceptions.ConnectionError as e:
        print(f"CONNECT_ERROR: {e}")
    except requests.exceptions.Timeout:
        print(f"TIMEOUT_ERROR: {e}")
    except requests.exceptions.RequestException as e:
        print(f"REQUEST_ERROR: {e}")

def importCertificateToAriaLifecycle(inFqdn,token, verify, alias, cer, key, ca):

    if debug:
        print(f"In: importCertificateToAriaLifecycle")

    url = f"https://{inFqdn}/lcm/locker/api/v2/certificates/import"
        
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Basic ' + token,
        'Accept': 'application/json'
    }

    caChain = f"{cer}{ca}"

    payload = json.dumps({
        "alias": alias,
        "certificateChain": caChain,
        "passcode": "",
        "privateKey": key
    }) 

    try:
        print(f"TASK: Importing Certificate {alias} into Locker")
        response = requests.post(url=url, data=payload, headers=headers, verify=verify )
        jResponse = response.json()

        if response.status_code < 200 or response.status_code >= 300:
            print(f"INFO: Response Code: {str(response.status_code)}")
            print(jResponse)
            response.raise_for_status()
            return response.status_code

    except requests.exceptions.HTTPError as e:
        print(f"ERROR_HTTP: {e}")
    except requests.exceptions.ConnectionError as e:
        print(f"ERROR_CONNECT: {e}")
    except requests.exceptions.Timeout:
        print(f"ERROR_TIMEOUT: {e}")
    except requests.exceptions.RequestException as e:
        print(f"ERROR_REQUEST: {e}")


def synchInventoryByEnvironmentId(inFqdn,token, verify, environmentId):

    if debug:
        print(f"In: updateProductSupportPack")

    url = f"https://{inFqdn}/lcm/lcops/api/v2/environments/{environmentId}/inventory-sync"
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Basic ' + token,
        'Accept': 'application/json'
    }

    payload = {}

    try:
        response = requests.post(url=url, data=payload, headers=headers, verify=verify )       
        response.raise_for_status
        jResponse = response.json()
        
        if not (response.status_code < 200 or response.status_code >= 300):
            return jResponse
        else:
            print(f"INFO: Response Code: {str(response.status_code)}")
            print(jResponse)

            return response.status_code


    except requests.exceptions.HTTPError as e:
        print(f"ERROR_HTTP: {e}")
    except requests.exceptions.ConnectionError as e:
        print(f"ERROR_CONNECT: {e}")
    except requests.exceptions.Timeout:
        print(f"ERROR_TIMEOUT: {e}")
    except requests.exceptions.RequestException as e:
        print(f"ERROR_REQUEST: {e}")
   
## Inventory Sync a Product in a single environment

def synchInventoryProductByEnvironmentId(inFqdn, token, verify, environmentId, productId):

    if debug:
        print(f"In: updateProductSupportPack")

    url = f"https://{inFqdn}/lcm/lcops/api/v2/environments/{environmentId}/products/{productId}/inventory-sync"
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Basic ' + token,
        'Accept': 'application/json'
    }

    payload = {}

    try:
        response = requests.post(url=url, data=payload, headers=headers, verify=verify )       
        jResponse = response.json()

        if response.status_code < 200 or response.status_code >= 300:
            print(f"INFO: Response Code: {str(response.status_code)}")
            print(jResponse)
            response.raise_for_status
            return response.status_code
        else:
            return jResponse["requestId"]

    except requests.exceptions.HTTPError as e:
        print(f"ERROR_HTTP: {e}")
    except requests.exceptions.ConnectionError as e:
        print(f"ERROR_CONNECT: {e}")
    except requests.exceptions.Timeout:
        print(f"ERROR_TIMEOUT: {e}")
    except requests.exceptions.RequestException as e:
        print(f"ERROR_REQUEST: {e}")
   

## Power On a Product in a single environment

def powerStateProductByEnvironmentId(inFqdn, token, verify, environmentId, productId, powerState):

    if debug:
        print(f"In: updateProductSupportPack")

    url = f"https://{inFqdn}/lcm/lcops/api/v2/environments/{environmentId}/products/{productId}/{powerState}"
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Basic ' + token,
        'Accept': 'application/json'
    }

    payload = {}

    try:
        response = requests.post(url=url, data=payload, headers=headers, verify=verify )       
        jResponse = response.json()

        if response.status_code < 200 or response.status_code >= 300:
            print(f"INFO: Response Code: {str(response.status_code)}")
            print(jResponse)
            response.raise_for_status
            return response.status_code
        else:
            return jResponse["requestId"]

    except requests.exceptions.HTTPError as e:
        print(f"ERROR_HTTP: {e}")
    except requests.exceptions.ConnectionError as e:
        print(f"ERROR_CONNECT: {e}")
    except requests.exceptions.Timeout:
        print(f"ERROR_TIMEOUT: {e}")
    except requests.exceptions.RequestException as e:
        print(f"ERROR_REQUEST: {e}")
   

def triggerPowerEvent(inFqdn, token, verify, environment, productId, powerState):
    try:

        print(f"TASK: Checking '{inFqdn}' for '{environment}' environment.")
        envId = getEnvironmentVmidByName(inFqdn, token, verify, environment)
        print(f"INFO: Environment '{environment}' has an ID of '{envId}'")
            
        if (envId):    
            requestId = powerStateProductByEnvironmentId(inFqdn, token, verify, envId, productId, powerState)
            print(f"TASK: Triggering Power Event - '{powerState}' for {productId} - (Request Id: {requestId})")
            requestStatus = getRequestStatus(inFqdn, token, verify, requestId)
            while not requestStatus == "COMPLETED":
            
                if requestStatus == "IN_PROGRESS" or "INPROGRESS":
                    print(f"INFO_REQUEST State: {requestStatus}")
                    core.countdown(45,1)
                elif requestStatus =="FAILED":
                    print(f"ERROR_REQUEST State: {requestStatus}") 
                else:
                    print(f"INFO_REQUEST State: {requestStatus}") 
                
                requestStatus = getRequestStatus(inFqdn, token, verify, requestId)
        else:
            print(f"ERROR: Environment '{environment}' does not exist.")

    except requests.exceptions.HTTPError as e:
        print(f"ERROR_HTTP: {e}")
    except requests.exceptions.ConnectionError as e:
        print(f"ERROR_CONNECT: {e}")
    except requests.exceptions.Timeout:
        print(f"ERROR_TIMEOUT: {e}")
    except requests.exceptions.RequestException as e:
        print(f"ERROR_REQUEST: {e}")
   

def triggerInventorySynch(inFqdn, token, verify, environment, productIds):

    try:
        print(f"TASK: Checking for {environment}")
        envId = getEnvironmentVmidByName(inFqdn, token, verify, environment)
        print(f"INFO: Environment '{environment}' has an ID of '{envId}'")
        if (envId):
            for productId in productIds:

                requestId = synchInventoryProductByEnvironmentId(inFqdn, token, sslVerify, envId, productId )

                print(f"TASK: Triggering inventory sync for {productId} (Request Id: {requestId})")
            
                requestStatus = getRequestStatus(inFqdn, token, verify, requestId)

                while not requestStatus == "COMPLETED":
                    
                    if requestStatus == "IN_PROGRESS" or "INPROGRESS":
                        print(f"INFO:  Request State: {requestStatus}") 
                        core.countdown(15,1)
                    elif requestStatus == "FAILED":
                        print(f"INFO:  Request State: {requestStatus}") 
                        raise SystemExit(requestStatus)
                    else:
                        print(f"INFO:  Request State: {requestStatus}") 
                    
                    requestStatus = getRequestStatus(inFqdn, token, verify, requestId)
        else:
            print(f"ERROR: Environment '{environment}' does not exist.")

    except requests.exceptions.HTTPError as e:
        print(f"ERROR_HTTP: {e}")
    except requests.exceptions.ConnectionError as e:
        print(f"ERROR_CONNECT: {e}")
    except requests.exceptions.Timeout:
        print(f"ERROR_TIMEOUT: {e}")
    except requests.exceptions.RequestException as e:
        print(f"ERROR_REQUEST: {e}")
   
    finally:
        requestStatus = ""
        envId = ""

def getRequestStatus(inFqdn, token, verify, requestId):
    
    if debug:
        print(f"In: getRequestStatus")

    url = f"https://{inFqdn}/lcm/request/api/v2/requests/{str(requestId)}"
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Basic ' + token,
        'Accept': 'application/json'
    }

    payload = {}

    try:

        response = requests.get(url=url, data=payload, headers=headers, verify=verify )    
        jResponse = response.json()

        if not (response.status_code < 200 or response.status_code >= 300):
            response.raise_for_status 
            return jResponse["state"]
        else:
            print(f"INFO: Response Code: {str(response.status_code)}")
            print(jResponse)
            response.raise_for_status        
            return "FAILED"

    except requests.exceptions.HTTPError as e:
        print(f"ERROR_HTTP: {e}")
    except requests.exceptions.ConnectionError as e:
        print(f"ERROR_CONNECT: {e}")
    except requests.exceptions.Timeout:
        print(f"ERROR_TIMEOUT: {e}")
    except requests.exceptions.RequestException as e:
        print(f"ERROR_REQUEST: {e}")