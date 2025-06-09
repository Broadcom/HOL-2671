resource avi_pool template-pool {
      name =  "${var.deployment-name}-pool" #Pool name
      cloud_ref = data.avi_cloud.nsx-cloud.id #Cloud pool will be created in
      default_server_port = 80 #Default listening port for Pool
      health_monitor_refs = [ #List of Health Monitors assigned to pool
      data.avi_healthmonitor.system-http.id
      ]
      servers  {
        enabled = true #Server enabled 
        ip  {
          addr = "172.16.110.11" #Server IP address
          type = "V4" #IP version
        }
        port = 30001 #Server listening port
      }
      servers  {
        enabled = true #Server enabled 
        ip  {
          addr = "172.16.110.12" #Server IP address
          type = "V4" #IP version
        }
        port = 30001 #Server enabled 
        }
      tenant_ref = data.avi_tenant.admin.id #Tenant pool with be created in
      tier1_lr = "/infra/tier-1s/t1-gw-sitea" #Tier 1 router the pool will be attached to
}

resource avi_vsvip template-vsvip {
      cloud_ref = data.avi_cloud.nsx-cloud.id #Cloud VsVIP will be created in
      dns_info { #DNS configuration
        algorithm = "DNS_RECORD_RESPONSE_CONSISTENT_HASH"
        fqdn = "${var.deployment-name}.region01a.vcf.sddc.lab" #VsVIP fqdn
        ttl = 30 #Time To Live in seconds
        type = "DNS_RECORD_A" #DNS record type
      }
      name = "${var.deployment-name}-VsVip" #Name of VsVIP
      tenant_ref = data.avi_tenant.admin.id #Tenant VsVIP will be created in
      tier1_lr = "/infra/tier-1s/t1-gw-sitea" #Tier 1 router VsVIP will be attached to
      vip {
        auto_allocate_ip = true #Autoallocate IP address
        auto_allocate_ip_type = "V4_ONLY" #Autoallocate an IPv4 IP address
        enabled = true #Enable VsVIP
        ipam_network_subnet  {
          network_ref = data.avi_network.vm-segment.id # NSX-T segment to use for VIP
          ######
          # This subnet block is defining the auto-allocation IPAM subnet to pull an IP from.  It can be left out
          # but terraform will detect a change when the API adds it to the configuration
          subnet {   
            mask = "24"
            ip_addr {
              addr = "172.16.110.0"
              type = "V4"
              }
            }
          ######
          }
        vip_id = 1
        }
      vrf_context_ref=  data.avi_vrfcontext.t1-gw-sitea.id #VRF VsVIP will be created in
      }


resource avi_virtualservice template-vs {    
      application_profile_ref =  data.avi_applicationprofile.system-http.id #Application profile attached to virtual service
      cloud_ref = data.avi_cloud.nsx-cloud.id #Cloud virtual service will be created in
      cloud_type = "CLOUD_NSXT" 
      scaleout_ecmp = "true"  # Tells Avi that a scaleout will be Layer 3 using ECMP from T1 router
      enabled = true #Enables virtual service
      name = "${var.deployment-name}-vs" #name of virtual service
      network_profile_ref = data.avi_networkprofile.system-tcp-proxy.id #Network profile attached to virtual service
      pool_ref = avi_pool.template-pool.id #Pool attached to virtual service
      services { 
        enable_ssl = false #SSL disable
        port = 80 #Virtual service listening port
        port_range_end = 80  # End port of listener range, only using a single port for cleartext
      }
      services {
        enable_ssl= true # #SSL enable
        port= 443 #Virtual service listening port
        port_range_end = 443  # End port of listener range, only using a single port for encrypted
      }

      ssl_key_and_certificate_refs = [ #List of SSL Certificates attached to virtual service
       data.avi_sslkeyandcertificate.wildcard-rsa.id,
       data.avi_sslkeyandcertificate.default-ecc.id
      ]
      ssl_profile_ref = data.avi_sslprofile.system-standard.id #SSL Profile attached to virtual service
      tenant_ref = data.avi_tenant.admin.id #Tenant virtual service will be attached to
      vrf_context_ref = data.avi_vrfcontext.t1-gw-sitea.id #VRF virtual service will be created in
      vsvip_ref = avi_vsvip.template-vsvip.id #VsVIP virtual service will use
}

