data avi_healthmonitor system-http {
  name = "System-HTTP"
}

data avi_applicationprofile system-http {
  name = "System-HTTP"
}

data avi_cloud nsx-cloud {
  name = "SiteA_nsx_cloud"
}
data avi_tenant admin {
  name = "admin"
}
data avi_vrfcontext t1-gw-sitea {
  name = "t1-gw-sitea"
}
data avi_network vm-segment {
  name = "ls-vmnet-a"
}
data avi_networkprofile system-tcp-proxy {
  name = "System-TCP-Proxy"
}
data avi_sslprofile system-standard {
    name = "System-Standard"
}
data avi_sslkeyandcertificate wildcard-rsa {
    name = "HandsOnLabs_Appcert"
}
data avi_sslkeyandcertificate default-ecc {
    name = "System-Default-Cert-EC"
}