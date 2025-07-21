import os
import requests
import re
import subprocess
import functions.file_functions as file

debug = False

   
def createSANCertCfgFile(cfgFile, fqdn, shortname, altNames, replace):

    cfg = file.checkFile(cfgFile)

    if not (cfg) or replace:

        file.createFile(f'{cfgFile}', ' ')
    
        with open(f'{cfgFile}', 'a') as f:
            f.write(f'[ req ]\n')
            f.write(f'default_md = sha512\n')
            f.write(f'default_bits = 2048\n')
            f.write(f'default_keyfile = rui.key\n')
            f.write(f'distinguished_name = req_distinguished_name\n')
            f.write(f'encrypt_key = no\n')
            f.write(f'prompt = no\n')
            f.write(f'string_mask = nombstr\n')
            f.write(f'req_extensions = v3_req\n')
            f.write('\n')
            f.write(f'[ v3_req ]\n')
            f.write(f'basicConstraints = CA:false\n')
            f.write(f'keyUsage = digitalSignature, keyEncipherment, dataEncipherment\n')
            f.write(f'extendedKeyUsage = serverAuth, clientAuth\n')
            f.write(f'subjectAltName = @alt_names\n')
            f.write('\n')
            f.write('[ alt_names ]\n')
            for i in range(len(altNames)):
                f.write(f'DNS.{i} = {altNames[i]}\n')  
            f.write('\n')      
            f.write(f'[ req_distinguished_name ]\n')
            f.write(f'countryName = US\n')
            f.write(f'stateOrProvinceName = California\n')
            f.write(f'localityName = Palo Alto\n')
            f.write(f'0.organizationName = VMware\n')
            f.write(f'organizationalUnitName = Hands-on Labs\n')
            f.write(f'commonName = {fqdn}\n')
            f.write(f'emailAddress = administrator@vcf.lab\n')
        
        f.close()

    else:
        raise Exception(f'SSL Certificate : SSL Config File Exists : {cfgFile}')
    
def createCertCfgFile(cfgFile, fqdn, shortname, altNames, replace):

    cfg = file.checkFile(cfgFile)

    if not (cfg) or replace:

        file.createFile(f'{cfgFile}', ' ')
    
        with open(f'{cfgFile}', 'a') as f:
            f.write(f'[ req ]\n')
            f.write(f'default_md = sha512\n')
            f.write(f'default_bits = 2048\n')
            f.write(f'default_keyfile = rui.key\n')
            f.write(f'distinguished_name = req_distinguished_name\n')
            f.write(f'encrypt_key = no\n')
            f.write(f'prompt = no\n')
            f.write(f'string_mask = nombstr\n')
            f.write(f'req_extensions = v3_req\n')
            f.write('\n')
            f.write(f'[ v3_req ]\n')
            f.write(f'basicConstraints = CA:false\n')
            f.write(f'keyUsage = digitalSignature, keyEncipherment, dataEncipherment\n')
            f.write(f'extendedKeyUsage = serverAuth, clientAuth\n')
            f.write(f'subjectAltName = @alt_names\n')
            f.write('\n')
            f.write('[ alt_names ]\n')
            for i in range(len(altNames)):
                f.write(f'DNS.{i} = {altNames[i]}\n')  
            f.write('\n')      
            f.write(f'[ req_distinguished_name ]\n')
            f.write(f'countryName = US\n')
            f.write(f'stateOrProvinceName = California\n')
            f.write(f'localityName = Palo Alto\n')
            f.write(f'0.organizationName = VMware\n')
            f.write(f'organizationalUnitName = Hands-on Labs\n')
            f.write(f'commonName = {fqdn}\n')
            f.write(f'emailAddress = administrator@vcf.lab\n')
        
        f.close()

    else:
        raise Exception(f'SSL Certificate : SSL Config File Exists : {cfgFile}')
    
def createCsrFileFromCfg (sslExec, csrFile, cfgFile, keyFile, alias, replace):
    
    cfg = file.checkFile(cfgFile)
    csr = file.checkFile(csrFile)

    if not (csr) or replace:
        if (cfg):
            certFolder = os.path.dirname(cfgFile)
            os.chdir(certFolder)
            
            print(f'TASK: Create CSR for \'{alias}\' at {os.path.splitext(os.path.basename(cfgFile))[0]}')

            subprocess.check_call([sslExec,'req','-new', '-nodes', '-out', csrFile, '-key', keyFile, '-config', cfgFile])
        
    with open(csrFile) as csr:
        return csr.read()
    

      
def createRSAKey (sslExec, keyFile, keyLength, alias, replace):
    
    key = file.checkFile(keyFile)

    if not (key) or replace:
        sslFolder = os.path.dirname(sslExec)
        certFolder = os.path.dirname(keyFile)
        os.chdir(sslFolder)
        
        print(f'TASK: Create RSA KEY for \'{alias}\' at {os.path.splitext(os.path.basename(keyFile))[0]}')

        subprocess.check_call([f'{sslExec}','genrsa', '-out', keyFile, keyLength])
    
    with open(keyFile) as key:
        return key.read()

def getPrivateKeyFromCsr(file, csr, shortname,):
    
    try:
        pattern = r'([\-]*BEGIN\sPRIVATE\sKEY[\-]+.+[-]+END\sPRIVATE\sKEY[-]+)'
        match = re.search(pattern, csr, re.DOTALL)
    
        if match:
            key = match.group(1)
        else:
            print(f'INFO: No Private Key data found.')

        if file:
            rootFolder = f'C:\\hol\\'
            certFolder = f'{rootFolder}SSL\\host\\{shortname}\\'
            file.createFolder(certFolder)
        
            keyFile = f'{certFolder}{shortname}.key'
        
            file.createFile(keyFile, key)
    
        return key

    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

def createCertFromCsr(sslExec, csrFile, certFile, caCert, caKey, caPass, replace):
    
    cer = file.checkFile(certFile)
    
    if not (cer) or replace:
       
        certFolder = os.path.dirname(certFile)

        os.chdir(certFolder)

        print(f'SSL Certificates : Create SSL CER from  CSR: {os.path.splitext(os.path.basename(csrFile))[0]}')
       
        subprocess.check_call([sslExec, 'x509', '-req', '-in', csrFile, '-CAkey', caKey, '-CA', caCert, '-out', certFile, '-passin', f'pass:{caPass}'])

    with open(certFile) as cert:
        return cert.read()

def createPemFile(cer,key,csr,ca, pemFile, replace):

    pem = file.checkFile(pemFile)

    print(f'TASK: SSL Certificate : Creating PEM : {os.path.splitext(os.path.basename(pemFile))[0]}')

    if not (pem) or replace:
    
        file.deleteFile(pemFile)

        with open(pemFile, 'w') as pem:
            pem.write(cer)
            pem.write(key)
            pem.write('\n')
            pem.write(ca)
            # with open(caFile, 'r') as ca_cert:
            #     pem.writelines(ca_cert.read())

#########################################