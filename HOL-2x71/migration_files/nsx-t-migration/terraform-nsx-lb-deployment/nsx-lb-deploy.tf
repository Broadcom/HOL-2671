resource "nsxt_policy_lb_http_application_profile" "http-to-https" {
  display_name = "http-to-https"
  http_redirect_to_https = "true"
  x_forwarded_for = "INSERT"
}

resource "nsxt_policy_lb_service" "site_a_load_balancer_1" { 
    display_name      = var.site_a_load_balancer_1
    description       = "Site A Load Balancer 1"
    connectivity_path = data.nsxt_policy_tier1_gateway.tier1_router.path
    size              = "SMALL"
    enabled           = true
    error_log_level   = "ERROR"
}

resource "nsxt_policy_group" "backend-servers" {
  display_name = "backend-servers"
  description  = "NS Groups containing backend servers"

  criteria {
    ipaddress_expression {
      ip_addresses = [var.site_a_pool_member_1_ip, var.site_a_pool_member_2_ip]
    }
  }
}


resource "nsxt_policy_group" "student-desktop" {
  display_name = "student-desktop"
  description  = "NS Groups containing backend servers"

  criteria {
    ipaddress_expression {
      ip_addresses = [var.student_desktop]
    }
  }
}

resource "nsxt_policy_lb_pool" "pool-01" { 
    display_name        = "pool-01"
    description         = "Server pool for web (HTTP) traffic"
    algorithm           = "ROUND_ROBIN"
    active_monitor_paths = [data.nsxt_policy_lb_monitor.http-30001.path]
    passive_monitor_path = "/infra/lb-monitor-profiles/default-passive-lb-monitor"
    member {
        admin_state                = "ENABLED"
        backup_member              = false
        display_name               = var.site_a_pool_member_1_name
        ip_address                 = var.site_a_pool_member_1_ip
        max_concurrent_connections = 12
        port                       = "30001"
        weight                     = 1
    }
    member {
        admin_state                = "ENABLED"
        backup_member              = false
        display_name               = var.site_a_pool_member_2_name
        ip_address                 = var.site_a_pool_member_2_ip
        max_concurrent_connections = 12
        port                       = "30001"
        weight                     = 1
    }
    snat {
        type = "AUTOMAP"
    }
    tcp_multiplexing_enabled = false
}

resource "nsxt_policy_lb_pool" "pool-02" {
    display_name        = "pool-02"
    description         = "Server pool for web (HTTP) traffic"
    algorithm           = "WEIGHTED_ROUND_ROBIN"
    active_monitor_paths = [data.nsxt_policy_lb_monitor.http-30001.path]
    passive_monitor_path = "/infra/lb-monitor-profiles/default-passive-lb-monitor"
    member {
        admin_state                = "ENABLED"
        backup_member              = false
        display_name               = var.site_a_pool_member_1_name
        ip_address                 = var.site_a_pool_member_1_ip
        max_concurrent_connections = 12
        port                       = "30001"
        weight                     = 1
    }
    member {
        admin_state                = "ENABLED"
        backup_member              = false
        display_name               = var.site_a_pool_member_2_name
        ip_address                 = var.site_a_pool_member_2_ip
        max_concurrent_connections = 12
        port                       = "30001"
        weight                     = 1
    }
    snat {
        type = "AUTOMAP"
    }
    tcp_multiplexing_enabled = true
}

resource "nsxt_policy_lb_pool" "pool-03" {
    display_name        = "pool-03"
    description         = "Server pool for web (HTTP) traffic"
    algorithm           = "LEAST_CONNECTION"
    active_monitor_paths = [data.nsxt_policy_lb_monitor.http-30001.path]
    passive_monitor_path = "/infra/lb-monitor-profiles/default-passive-lb-monitor"
    member {
        admin_state                = "ENABLED"
        backup_member              = false
        display_name               = var.site_a_pool_member_1_name
        ip_address                 = var.site_a_pool_member_1_ip
        max_concurrent_connections = 12
        port                       = "30001"
        weight                     = 1
    }
    member {
        admin_state                = "ENABLED"
        backup_member              = false
        display_name               = var.site_a_pool_member_2_name
        ip_address                 = var.site_a_pool_member_2_ip
        max_concurrent_connections = 12
        port                       = "30001"
        weight                     = 1
    }
    snat {
        type = "AUTOMAP"
    }
    tcp_multiplexing_enabled = false
}

# resource "nsxt_policy_lb_pool" "pool-04" {
#     display_name        = "pool-04"
#     description         = "Server pool for web (HTTP) traffic"
#     algorithm           = "WEIGHTED_LEAST_CONNECTION"
#     active_monitor_paths = ["/infra/lb-monitor-profiles/default-tcp-lb-monitor"]
#     passive_monitor_path = "/infra/lb-monitor-profiles/default-passive-lb-monitor"
#     member {
#         admin_state                = "ENABLED"
#         backup_member              = false
#         display_name               = var.site_a_pool_member_1_name
#         ip_address                 = var.site_a_pool_member_1_ip
#         max_concurrent_connections = 12
#         port                       = "30001"
#         weight                     = 1
#     }
#     member {
#         admin_state                = "ENABLED"
#         backup_member              = false
#         display_name               = var.site_a_pool_member_2_name
#         ip_address                 = var.site_a_pool_member_2_ip
#         max_concurrent_connections = 12
#         port                       = "30001"
#         weight                     = 1
#     }
#     snat {
#         type = "AUTOMAP"
#     }
#     tcp_multiplexing_enabled = true
# }

resource "nsxt_policy_lb_pool" "pool-05" {
    display_name        = "pool-05"
    description         = "Server pool for web (HTTP) traffic"
    algorithm           = "IP_HASH"
        active_monitor_paths = [
      "/infra/lb-monitor-profiles/default-icmp-lb-monitor"
    ]
    passive_monitor_path = "/infra/lb-monitor-profiles/default-passive-lb-monitor"
    member {
        admin_state                = "ENABLED"
        backup_member              = false
        display_name               = var.site_a_pool_member_1_name
        ip_address                 = var.site_a_pool_member_1_ip
        max_concurrent_connections = 12
        port                       = "30001"
        weight                     = 1
    }
    member {
        admin_state                = "ENABLED"
        backup_member              = false
        display_name               = var.site_a_pool_member_2_name
        ip_address                 = var.site_a_pool_member_2_ip
        max_concurrent_connections = 12
        port                       = "30001"
        weight                     = 1
    }
    snat {
        type = "AUTOMAP"
    }
    tcp_multiplexing_enabled = false
}

resource "nsxt_policy_lb_pool" "pool-06" {
    display_name        = "pool-06"
    description         = "Server pool for web (HTTP) traffic"
    algorithm           = "ROUND_ROBIN"
    active_monitor_paths = [data.nsxt_policy_lb_monitor.http-30001.path]
    passive_monitor_path = "/infra/lb-monitor-profiles/default-passive-lb-monitor"
    member {
        admin_state                = "ENABLED"
        backup_member              = false
        display_name               = var.site_a_pool_member_1_name
        ip_address                 = var.site_a_pool_member_1_ip
        max_concurrent_connections = 12
        port                       = "30001"
        weight                     = 1
    }
    member {
        admin_state                = "ENABLED"
        backup_member              = false
        display_name               = var.site_a_pool_member_2_name
        ip_address                 = var.site_a_pool_member_2_ip
        max_concurrent_connections = 12
        port                       = "30001"
        weight                     = 1
    }
    snat {
        type = "AUTOMAP"
    }
    tcp_multiplexing_enabled = true
}

# resource "nsxt_policy_lb_pool" "pool-07" {
#     display_name        = "pool-07"
#     description         = "Server pool for web (HTTP) traffic"
#     algorithm           = "WEIGHTED_ROUND_ROBIN"
#     active_monitor_paths = [data.nsxt_policy_lb_monitor.http-30001.path]
#     passive_monitor_path = "/infra/lb-monitor-profiles/default-passive-lb-monitor"
#     member {
#         admin_state                = "ENABLED"
#         backup_member              = false
#         display_name               = var.site_a_pool_member_1_name
#         ip_address                 = var.site_a_pool_member_1_ip
#         max_concurrent_connections = 12
#         port                       = "30001"
#         weight                     = 1
#     }
#     member {
#         admin_state                = "ENABLED"
#         backup_member              = false
#         display_name               = var.site_a_pool_member_2_name
#         ip_address                 = var.site_a_pool_member_2_ip
#         max_concurrent_connections = 12
#         port                       = "30001"
#         weight                     = 1
#     }
#     snat {
#         type = "AUTOMAP"
#     }
#     tcp_multiplexing_enabled = false
# }

# resource "nsxt_policy_lb_pool" "pool-08" {
#     display_name        = "pool-08"
#     description         = "Server pool for web (HTTP) traffic"
#     algorithm           = "LEAST_CONNECTION"
#     active_monitor_paths = ["/infra/lb-monitor-profiles/default-tcp-lb-monitor"]
#     passive_monitor_path = "/infra/lb-monitor-profiles/default-passive-lb-monitor"
#     member {
#         admin_state                = "ENABLED"
#         backup_member              = false
#         display_name               = var.site_a_pool_member_1_name
#         ip_address                 = var.site_a_pool_member_1_ip
#         max_concurrent_connections = 12
#         port                       = "30001"
#         weight                     = 1
#     }
#     member {
#         admin_state                = "ENABLED"
#         backup_member              = false
#         display_name               = var.site_a_pool_member_2_name
#         ip_address                 = var.site_a_pool_member_2_ip
#         max_concurrent_connections = 12
#         port                       = "30001"
#         weight                     = 1
#     }
#     snat {
#         type = "AUTOMAP"
#     }
#     tcp_multiplexing_enabled = true
# }

# resource "nsxt_policy_lb_pool" "pool-09" {
#     display_name        = "pool-09"
#     description         = "Server pool for web (HTTP) traffic"
#     algorithm           = "WEIGHTED_LEAST_CONNECTION"
#     active_monitor_paths = ["/infra/lb-monitor-profiles/default-icmp-lb-monitor"]
#     passive_monitor_path = "/infra/lb-monitor-profiles/default-passive-lb-monitor"
#     member {
#         admin_state                = "ENABLED"
#         backup_member              = false
#         display_name               = var.site_a_pool_member_1_name
#         ip_address                 = var.site_a_pool_member_1_ip
#         max_concurrent_connections = 12
#         port                       = "30001"
#         weight                     = 1
#     }
#     member {
#         admin_state                = "ENABLED"
#         backup_member              = false
#         display_name               = var.site_a_pool_member_2_name
#         ip_address                 = var.site_a_pool_member_2_ip
#         max_concurrent_connections = 12
#         port                       = "30001"
#         weight                     = 1
#     }
#     snat {
#         type = "AUTOMAP"
#     }
#     tcp_multiplexing_enabled = false
# }

resource "nsxt_policy_lb_pool" "pool-10" {
    display_name        = "pool-10"
    description         = "Server pool for web (HTTP) traffic"
    algorithm           = "IP_HASH"
    active_monitor_paths = [data.nsxt_policy_lb_monitor.http-30001.path]
    passive_monitor_path = "/infra/lb-monitor-profiles/default-passive-lb-monitor"
    member {
        admin_state                = "ENABLED"
        backup_member              = false
        display_name               = var.site_a_pool_member_1_name
        ip_address                 = var.site_a_pool_member_1_ip
        max_concurrent_connections = 12
        port                       = "30001"
        weight                     = 1
    }
    member {
        admin_state                = "ENABLED"
        backup_member              = false
        display_name               = var.site_a_pool_member_2_name
        ip_address                 = var.site_a_pool_member_2_ip
        max_concurrent_connections = 12
        port                       = "30001"
        weight                     = 1
    }
    snat {
        type = "AUTOMAP"
    }
    tcp_multiplexing_enabled = true
}

resource "nsxt_policy_lb_pool" "pool-11" {
    display_name        = "pool-11"
    description         = "Server pool for web (HTTP) traffic"
    algorithm           = "ROUND_ROBIN"
    active_monitor_paths = [data.nsxt_policy_lb_monitor.http-30001.path]
    passive_monitor_path = "/infra/lb-monitor-profiles/default-passive-lb-monitor"
    member {
        admin_state                = "ENABLED"
        backup_member              = false
        display_name               = var.site_a_pool_member_1_name
        ip_address                 = var.site_a_pool_member_1_ip
        max_concurrent_connections = 12
        port                       = "30001"
        weight                     = 1
    }
    member {
        admin_state                = "ENABLED"
        backup_member              = false
        display_name               = var.site_a_pool_member_2_name
        ip_address                 = var.site_a_pool_member_2_ip
        max_concurrent_connections = 12
        port                       = "30001"
        weight                     = 1
    }
    snat {
        type = "AUTOMAP"
    }
    tcp_multiplexing_enabled = false
}

# resource "nsxt_policy_lb_pool" "pool-12" {
#     display_name        = "pool-12"
#     description         = "Server pool for web (HTTP) traffic"
#     algorithm           = "WEIGHTED_ROUND_ROBIN"
#     active_monitor_paths = ["/infra/lb-monitor-profiles/default-tcp-lb-monitor"]
#     passive_monitor_path = "/infra/lb-monitor-profiles/default-passive-lb-monitor"
#     member {
#         admin_state                = "ENABLED"
#         backup_member              = false
#         display_name               = var.site_a_pool_member_1_name
#         ip_address                 = var.site_a_pool_member_1_ip
#         max_concurrent_connections = 12
#         port                       = "30001"
#         weight                     = 1
#     }
#     member {
#         admin_state                = "ENABLED"
#         backup_member              = false
#         display_name               = var.site_a_pool_member_2_name
#         ip_address                 = var.site_a_pool_member_2_ip
#         max_concurrent_connections = 12
#         port                       = "30001"
#         weight                     = 1
#     }
#     snat {
#         type = "AUTOMAP"
#     }
#     tcp_multiplexing_enabled = true
# }

# resource "nsxt_policy_lb_pool" "pool-13" {
#     display_name        = "pool-13"
#     description         = "Server pool for web (HTTP) traffic"
#     algorithm           = "LEAST_CONNECTION"
#     active_monitor_paths = ["/infra/lb-monitor-profiles/default-icmp-lb-monitor"]
#     passive_monitor_path = "/infra/lb-monitor-profiles/default-passive-lb-monitor"
#     member {
#         admin_state                = "ENABLED"
#         backup_member              = false
#         display_name               = var.site_a_pool_member_1_name
#         ip_address                 = var.site_a_pool_member_1_ip
#         max_concurrent_connections = 12
#         port                       = "30001"
#         weight                     = 1
#     }
#     member {
#         admin_state                = "ENABLED"
#         backup_member              = false
#         display_name               = var.site_a_pool_member_2_name
#         ip_address                 = var.site_a_pool_member_2_ip
#         max_concurrent_connections = 12
#         port                       = "30001"
#         weight                     = 1
#     }
#     snat {
#         type = "AUTOMAP"
#     }
#     tcp_multiplexing_enabled = false
# }

resource "nsxt_policy_lb_pool" "pool-14" {
    display_name        = "pool-14"
    description         = "Server pool for web (HTTP) traffic"
    algorithm           = "WEIGHTED_LEAST_CONNECTION"
    active_monitor_paths = [data.nsxt_policy_lb_monitor.http-30001.path]
    passive_monitor_path = "/infra/lb-monitor-profiles/default-passive-lb-monitor"
    member {
        admin_state                = "ENABLED"
        backup_member              = false
        display_name               = var.site_a_pool_member_1_name
        ip_address                 = var.site_a_pool_member_1_ip
        max_concurrent_connections = 12
        port                       = "30001"
        weight                     = 1
    }
    member {
        admin_state                = "ENABLED"
        backup_member              = false
        display_name               = var.site_a_pool_member_2_name
        ip_address                 = var.site_a_pool_member_2_ip
        max_concurrent_connections = 12
        port                       = "30001"
        weight                     = 1
    }
    snat {
        type = "AUTOMAP"
    }
    tcp_multiplexing_enabled = true
}

resource "nsxt_policy_lb_pool" "pool-15" {
    display_name        = "pool-15"
    description         = "Server pool for web (HTTP) traffic"
    algorithm           = "IP_HASH"
    active_monitor_paths = [data.nsxt_policy_lb_monitor.http-30001.path]
    passive_monitor_path = "/infra/lb-monitor-profiles/default-passive-lb-monitor"
    member {
        admin_state                = "ENABLED"
        backup_member              = false
        display_name               = var.site_a_pool_member_1_name
        ip_address                 = var.site_a_pool_member_1_ip
        max_concurrent_connections = 12
        port                       = "30001"
        weight                     = 1
    }
    member {
        admin_state                = "ENABLED"
        backup_member              = false
        display_name               = var.site_a_pool_member_2_name
        ip_address                 = var.site_a_pool_member_2_ip
        max_concurrent_connections = 12
        port                       = "30001"
        weight                     = 1
    }
    snat {
        type = "AUTOMAP"
    }
    tcp_multiplexing_enabled = false
}

# resource "nsxt_policy_lb_pool" "pool-16" {
#     display_name        = "pool-16"
#     description         = "Server pool for web (HTTP) traffic"
#     algorithm           = "ROUND_ROBIN"
#     active_monitor_paths = ["/infra/lb-monitor-profiles/default-tcp-lb-monitor"]
#     passive_monitor_path = "/infra/lb-monitor-profiles/default-passive-lb-monitor"
#     member {
#         admin_state                = "ENABLED"
#         backup_member              = false
#         display_name               = var.site_a_pool_member_1_name
#         ip_address                 = var.site_a_pool_member_1_ip
#         max_concurrent_connections = 12
#         port                       = "30001"
#         weight                     = 1
#     }
#     member {
#         admin_state                = "ENABLED"
#         backup_member              = false
#         display_name               = var.site_a_pool_member_2_name
#         ip_address                 = var.site_a_pool_member_2_ip
#         max_concurrent_connections = 12
#         port                       = "30001"
#         weight                     = 1
#     }
#     snat {
#         type = "AUTOMAP"
#     }
#     tcp_multiplexing_enabled = true
# }

# resource "nsxt_policy_lb_pool" "pool-17" {
#     display_name        = "pool-17"
#     description         = "Server pool for web (HTTP) traffic"
#     algorithm           = "WEIGHTED_ROUND_ROBIN"
#     active_monitor_paths = ["/infra/lb-monitor-profiles/default-tcp-lb-monitor"]
#     passive_monitor_path = "/infra/lb-monitor-profiles/default-passive-lb-monitor"
#     member {
#         admin_state                = "ENABLED"
#         backup_member              = false
#         display_name               = var.site_a_pool_member_1_name
#         ip_address                 = var.site_a_pool_member_1_ip
#         max_concurrent_connections = 12
#         port                       = "30001"
#         weight                     = 1
#     }
#     member {
#         admin_state                = "ENABLED"
#         backup_member              = false
#         display_name               = var.site_a_pool_member_2_name
#         ip_address                 = var.site_a_pool_member_2_ip
#         max_concurrent_connections = 12
#         port                       = "30001"
#         weight                     = 1
#     }
#     snat {
#         type = "AUTOMAP"
#     }
#     tcp_multiplexing_enabled = false
# }

# resource "nsxt_policy_lb_pool" "pool-18" {
#     display_name        = "pool-18"
#     description         = "Server pool for web (HTTP) traffic"
#     algorithm           = "LEAST_CONNECTION"
#     active_monitor_paths = ["/infra/lb-monitor-profiles/default-icmp-lb-monitor"]
#     passive_monitor_path = "/infra/lb-monitor-profiles/default-passive-lb-monitor"
#     member {
#         admin_state                = "ENABLED"
#         backup_member              = false
#         display_name               = var.site_a_pool_member_1_name
#         ip_address                 = var.site_a_pool_member_1_ip
#         max_concurrent_connections = 12
#         port                       = "30001"
#         weight                     = 1
#     }
#     member {
#         admin_state                = "ENABLED"
#         backup_member              = false
#         display_name               = var.site_a_pool_member_2_name
#         ip_address                 = var.site_a_pool_member_2_ip
#         max_concurrent_connections = 12
#         port                       = "30001"
#         weight                     = 1
#     }
#     snat {
#         type = "AUTOMAP"
#     }
#     tcp_multiplexing_enabled = true
# }

# resource "nsxt_policy_lb_pool" "pool-19" {
#     display_name        = "pool-19"
#     description         = "Server pool for web (HTTP) traffic"
#     algorithm           = "WEIGHTED_LEAST_CONNECTION"
#     active_monitor_paths = ["/infra/lb-monitor-profiles/default-icmp-lb-monitor"]
#     passive_monitor_path = "/infra/lb-monitor-profiles/default-passive-lb-monitor"
#     member {
#         admin_state                = "ENABLED"
#         backup_member              = false
#         display_name               = var.site_a_pool_member_1_name
#         ip_address                 = var.site_a_pool_member_1_ip
#         max_concurrent_connections = 12
#         port                       = "30001"
#         weight                     = 1
#     }
#     member {
#         admin_state                = "ENABLED"
#         backup_member              = false
#         display_name               = var.site_a_pool_member_2_name
#         ip_address                 = var.site_a_pool_member_2_ip
#         max_concurrent_connections = 12
#         port                       = "30001"
#         weight                     = 1
#     }
#     snat {
#         type = "AUTOMAP"
#     }
#     tcp_multiplexing_enabled = false
# }

# resource "nsxt_policy_lb_pool" "pool-20" {
#     display_name        = "pool-20"
#     description         = "Server pool for web (HTTP) traffic"
#     algorithm           = "ROUND_ROBIN"
#     active_monitor_paths = ["/infra/lb-monitor-profiles/default-icmp-lb-monitor"]
#     passive_monitor_path = "/infra/lb-monitor-profiles/default-passive-lb-monitor"
#     member {
#         admin_state                = "ENABLED"
#         backup_member              = false
#         display_name               = var.site_a_pool_member_1_name
#         ip_address                 = var.site_a_pool_member_1_ip
#         max_concurrent_connections = 12
#         port                       = "30001"
#         weight                     = 1
#     }
#     member {
#         admin_state                = "ENABLED"
#         backup_member              = false
#         display_name               = var.site_a_pool_member_2_name
#         ip_address                 = var.site_a_pool_member_2_ip
#         max_concurrent_connections = 12
#         port                       = "30001"
#         weight                     = 1
#     }
#     snat {
#         type = "AUTOMAP"
#     }
#     tcp_multiplexing_enabled = true
# }

resource "nsxt_policy_lb_pool" "juice-pool" {
    display_name        = "juice-pool"
    description         = "Server pool for web (HTTP) traffic"
    algorithm           = "ROUND_ROBIN"
    #active_monitor_path = "/infra/lb-monitor-profiles/default-icmp-lb-monitor"
    active_monitor_paths = ["/infra/lb-monitor-profiles/default-icmp-lb-monitor"]
    passive_monitor_path = "/infra/lb-monitor-profiles/default-passive-lb-monitor"
    member {
        admin_state                = "ENABLED"
        backup_member              = false
        display_name               = var.site_a_pool_member_1_name
        ip_address                 = var.site_a_pool_member_1_ip
        max_concurrent_connections = 12
        port                       = "30003"
        weight                     = 1
    }
    member {
        admin_state                = "ENABLED"
        backup_member              = false
        display_name               = var.site_a_pool_member_2_name
        ip_address                 = var.site_a_pool_member_2_ip
        max_concurrent_connections = 12
        port                       = "30003"
        weight                     = 1
    }
    snat {
        type = "AUTOMAP"
    }
    tcp_multiplexing_enabled = true
}

resource "nsxt_policy_lb_virtual_server" "hol-nsx-http-vs-01" {
  display_name              = "hol-nsx-http-vs-01"
  enabled                   = true
  application_profile_path  = data.nsxt_policy_lb_app_profile.default_http_app_profile.path
  ip_address                = "172.16.230.101"
  ports                     = ["80"]
  service_path              = nsxt_policy_lb_service.site_a_load_balancer_1.path
  pool_path                 = nsxt_policy_lb_pool.pool-01.path
}

resource "nsxt_policy_lb_virtual_server" "hol-nsx-http-vs-02" {
  display_name              = "hol-nsx-http-vs-02"
  enabled                   = true
  application_profile_path  = data.nsxt_policy_lb_app_profile.default_http_app_profile.path
  ip_address                = "172.16.230.102"
  ports                     = ["80"]
  service_path              = nsxt_policy_lb_service.site_a_load_balancer_1.path
  pool_path                 = nsxt_policy_lb_pool.pool-02.path

  rule {
    display_name   = "http_access_rule"
    match_strategy = "ALL"
    phase          = "HTTP_ACCESS"

    action {
      connection_drop {}
    } 
    condition {
      ip_header {
        source_address = "10.0.0.2"
      }
    }
  }   
}

resource "nsxt_policy_lb_virtual_server" "hol-nsx-http-vs-03" { 
  display_name              = "hol-nsx-http-vs-03"
  enabled                   = true
  application_profile_path  = data.nsxt_policy_lb_app_profile.default_http_app_profile.path
  ip_address                = "172.16.230.103"
  ports                     = ["80"]
  service_path              = nsxt_policy_lb_service.site_a_load_balancer_1.path
  pool_path                 = nsxt_policy_lb_pool.pool-03.path

  rule {
    display_name   = "juice-rule"
    match_strategy = "ALL"
    phase          = "HTTP_FORWARDING"

    action {
      select_pool {
        pool_id   = nsxt_policy_lb_pool.juice-pool.path
      }
    }
    condition {
      http_request_uri {
        uri = "/juice"
        match_type = "STARTS_WITH"
      }
    }
  }
}

# resource "nsxt_policy_lb_virtual_server" "hol-nsx-http-vs-04" { 
#   display_name              = "hol-nsx-http-vs-04"
#   enabled                   = true
#   application_profile_path  = data.nsxt_policy_lb_app_profile.default_http_app_profile.path
#   ip_address                = "172.16.230.104"
#   ports                     = ["80"]
#   service_path              = nsxt_policy_lb_service.site_a_load_balancer_1.path
#   pool_path                 = nsxt_policy_lb_pool.pool-04.path

# }

resource "nsxt_policy_lb_virtual_server" "hol-nsx-http-vs-05" { 
  display_name              = "hol-nsx-http-vs-05"
  enabled                   = true
  application_profile_path  = data.nsxt_policy_lb_app_profile.default_http_app_profile.path
  ip_address                = "172.16.230.105"
  ports                     = ["80"]
  service_path              = nsxt_policy_lb_service.site_a_load_balancer_1.path
  pool_path                 = nsxt_policy_lb_pool.pool-05.path

  rule { 
    display_name   = "request_rewrite"
    match_strategy = "ALL"
    phase          = "HTTP_REQUEST_REWRITE"

    action {
      http_request_header_rewrite {
        header_name = "LB-TYPE"
        header_value = "Avi"
      }
    }
    condition {
      http_request_header {
        header_name = "LB-TYPE"
        header_value = "NSX-LB"
        match_type = "EQUALS"
      }
    }
  }
}


resource "nsxt_policy_lb_virtual_server" "hol-nsx-http-vs-06" { 
  display_name              = "hol-nsx-http-vs-06"
  enabled                   = true
  application_profile_path  = data.nsxt_policy_lb_app_profile.default_http_app_profile.path
  ip_address                = "172.16.230.106"
  ports                     = ["80"]
  service_path              = nsxt_policy_lb_service.site_a_load_balancer_1.path
  pool_path                 = nsxt_policy_lb_pool.pool-06.path

  rule {
    display_name   = "match_method_rewrite_header"
    match_strategy = "ALL"
    phase          = "HTTP_REQUEST_REWRITE"

    action {
      http_request_header_rewrite {
        header_name = "Client_Method"
        header_value = "MODIFIED_GET"
      }
    }
    condition {
      http_request_method {
        method = "GET"
      }
    }
  }
}

# resource "nsxt_policy_lb_virtual_server" "hol-nsx-http-vs-07" { 
#   display_name              = "hol-nsx-http-vs-07"
#   enabled                   = true
#   application_profile_path  = data.nsxt_policy_lb_app_profile.default_http_app_profile.path
#   ip_address                = "172.16.230.107"
#   ports                     = ["80"]
#   service_path              = nsxt_policy_lb_service.site_a_load_balancer_1.path
#   pool_path                 = nsxt_policy_lb_pool.pool-07.path
#   persistence_profile_path  = data.nsxt_policy_lb_persistence_profile.default-source-ip.path

# }

# resource "nsxt_policy_lb_virtual_server" "hol-nsx-http-vs-08" { 
#   display_name              = "hol-nsx-http-vs-08"
#   enabled                   = true
#   application_profile_path  = data.nsxt_policy_lb_app_profile.default_http_app_profile.path
#   ip_address                = "172.16.230.108"
#   ports                     = ["80"]
#   service_path              = nsxt_policy_lb_service.site_a_load_balancer_1.path
#   pool_path                 = nsxt_policy_lb_pool.pool-08.path
#   persistence_profile_path  = data.nsxt_policy_lb_persistence_profile.default-cookie.path

# }

# resource "nsxt_policy_lb_virtual_server" "hol-nsx-http-vs-09" { 
#   display_name              = "hol-nsx-http-vs-09"
#   enabled                   = true
#   application_profile_path  = data.nsxt_policy_lb_app_profile.default_http_app_profile.path
#   ip_address                = "172.16.230.109"
#   ports                     = ["80"]
#   service_path              = nsxt_policy_lb_service.site_a_load_balancer_1.path
#   pool_path                 = nsxt_policy_lb_pool.pool-09.path
#   persistence_profile_path  = data.nsxt_policy_lb_persistence_profile.default-cookie.path
  
# }

resource "nsxt_policy_lb_virtual_server" "hol-nsx-http-vs-10" { 
  display_name              = "hol-nsx-http-vs-10"
  enabled                   = true
  application_profile_path  = resource.nsxt_policy_lb_http_application_profile.http-to-https.path
  ip_address                = "172.16.230.111"
  ports                     = ["80"]
  service_path              = nsxt_policy_lb_service.site_a_load_balancer_1.path
  
}

resource "nsxt_policy_lb_virtual_server" "hol-nsx-http-vs-11" { 
  display_name              = "hol-nsx-http-vs-11"
  enabled                   = true
  application_profile_path  = data.nsxt_policy_lb_app_profile.default_http_app_profile.path
  ip_address                = "172.16.230.111"
  ports                     = ["443"]
  service_path              = nsxt_policy_lb_service.site_a_load_balancer_1.path
  pool_path                 = nsxt_policy_lb_pool.pool-11.path

  client_ssl {
    default_certificate_path = data.nsxt_policy_certificate.hol-wildcard.path
    ssl_profile_path         = data.nsxt_policy_lb_client_ssl_profile.default-balanced-client-ssl-profile.path
  }
}

# resource "nsxt_policy_lb_virtual_server" "hol-nsx-http-vs-12" { 
#   display_name              = "hol-nsx-http-vs-12"
#   enabled                   = true
#   application_profile_path  = data.nsxt_policy_lb_app_profile.default_http_app_profile.path
#   ip_address                = "172.16.230.112"
#   ports                     = ["443"]
#   service_path              = nsxt_policy_lb_service.site_a_load_balancer_1.path
#   pool_path                 = nsxt_policy_lb_pool.pool-12.path
#   persistence_profile_path  = data.nsxt_policy_lb_persistence_profile.default-source-ip.path

#   client_ssl {
#     default_certificate_path = data.nsxt_policy_certificate.hol-wildcard.path
#     ssl_profile_path         = data.nsxt_policy_lb_client_ssl_profile.default-balanced-client-ssl-profile.path
#   }
# }

# resource "nsxt_policy_lb_virtual_server" "hol-nsx-http-vs-13" { 
#   display_name              = "hol-nsx-http-vs-13"
#   enabled                   = true
#   application_profile_path  = data.nsxt_policy_lb_app_profile.default_http_app_profile.path
#   ip_address                = "172.16.230.113"
#   ports                     = ["80"]
#   service_path              = nsxt_policy_lb_service.site_a_load_balancer_1.path
#   pool_path                 = nsxt_policy_lb_pool.pool-13.path
#   max_concurrent_connections = 6
#   max_new_connection_rate    = 20
  
#   client_ssl {
#     default_certificate_path = data.nsxt_policy_certificate.hol-wildcard.path
#     ssl_profile_path         = data.nsxt_policy_lb_client_ssl_profile.default-balanced-client-ssl-profile.path
#   }
# }


resource "nsxt_policy_lb_virtual_server" "hol-nsx-http-vs-14" { 
  display_name              = "hol-nsx-http-vs-14"
  enabled                   = true
  application_profile_path  = data.nsxt_policy_lb_app_profile.default_http_app_profile.path
  ip_address                = "172.16.230.114"
  ports                     = ["443"]
  service_path              = nsxt_policy_lb_service.site_a_load_balancer_1.path
  pool_path                 = nsxt_policy_lb_pool.pool-14.path

  rule {
    display_name   = "ssl_end_to_end"
    match_strategy = "ALL"
    phase          = "TRANSPORT"

    action {
      ssl_mode_selection {
        ssl_mode = "SSL_END_TO_END"
      }
    }
    condition {
      ssl_sni  {
        sni = "172.16.230.10"
        match_type = "EQUALS"
      }
    }
  }
  client_ssl {
    default_certificate_path = data.nsxt_policy_certificate.hol-wildcard.path
    ssl_profile_path         = data.nsxt_policy_lb_client_ssl_profile.default-balanced-client-ssl-profile.path
  }
  server_ssl {
      client_certificate_path = data.nsxt_policy_certificate.hol-wildcard.path
      ssl_profile_path        = data.nsxt_policy_lb_server_ssl_profile.default-balanced-server-ssl-profile.path
  }
}

resource "nsxt_policy_lb_virtual_server" "hol-nsx-tcp-vs-15" { 
  display_name              = "hol-nsx-http-vs-15"
  enabled                   = true
  application_profile_path  = data.nsxt_policy_lb_app_profile.default_tcp_app_profile.path
  ip_address                = "172.16.230.115"
  ports                     = ["8080"]
  service_path              = nsxt_policy_lb_service.site_a_load_balancer_1.path
  pool_path                 = nsxt_policy_lb_pool.pool-15.path
  
  access_list_control {
    action = "DROP"
    group_path = nsxt_policy_group.student-desktop.path
  }
}

# resource "nsxt_policy_lb_virtual_server" "hol-nsx-tcp-vs-16" { 
#   display_name              = "hol-nsx-tcp-vs-16"
#   enabled                   = true
#   application_profile_path  = data.nsxt_policy_lb_app_profile.default_tcp_app_profile.path
#   ip_address                = "172.16.230.116"
#   ports                     = ["8080"]
#   service_path              = nsxt_policy_lb_service.site_a_load_balancer_1.path
#   pool_path                 = nsxt_policy_lb_pool.pool-16.path
#   persistence_profile_path  = data.nsxt_policy_lb_persistence_profile.default-source-ip.path

# }

# resource "nsxt_policy_lb_virtual_server" "hol-nsx-tcp-vs-17" { 
#   display_name              = "hol-nsx-tcp-vs-17"
#   enabled                   = true
#   application_profile_path  = data.nsxt_policy_lb_app_profile.custom-fast-tcp.path
#   ip_address                = "172.16.230.117"
#   ports                     = ["8080"]
#   service_path              = nsxt_policy_lb_service.site_a_load_balancer_1.path
#   pool_path                 = nsxt_policy_lb_pool.pool-17.path

# }

# resource "nsxt_policy_lb_virtual_server" "hol-nsx-tcp-vs-18" { 
#   display_name              = "hol-nsx-tcp-vs-18"
#   enabled                   = true
#   application_profile_path  = data.nsxt_policy_lb_app_profile.default_udp_app_profile.path
#   ip_address                = "172.16.230.118"
#   ports                     = ["8081"]
#   service_path              = nsxt_policy_lb_service.site_a_load_balancer_1.path
#   pool_path                 = nsxt_policy_lb_pool.pool-18.path

#   access_list_control {
#     action = "DROP"
#     group_path = nsxt_policy_group.student-desktop.path
#   }
# }

# resource "nsxt_policy_lb_virtual_server" "hol-nsx-udp-vs-19" { 
#   display_name              = "hol-nsx-udp-vs-19"
#   enabled                   = true
#   application_profile_path  = data.nsxt_policy_lb_app_profile.default_udp_app_profile.path
#   ip_address                = "172.16.230.119"
#   ports                     = ["8081"]
#   service_path              = nsxt_policy_lb_service.site_a_load_balancer_1.path
#   pool_path                 = nsxt_policy_lb_pool.pool-19.path

# }

# resource "nsxt_policy_lb_virtual_server" "hol-nsx-udp-vs-20" { 
#   display_name              = "hol-nsx-udp-vs-20"
#   enabled                   = true
#   application_profile_path  = data.nsxt_policy_lb_app_profile.custom-fast-udp.path
#   ip_address                = "172.16.230.120"
#   ports                     = ["8081"]
#   service_path              = nsxt_policy_lb_service.site_a_load_balancer_1.path
#   pool_path                 = nsxt_policy_lb_pool.pool-20.path

# }