data "nsxt_policy_project" "default_project" {
  display_name = var.project_name
}

data "nsxt_policy_tier1_gateway" "tier1_router" {
  context {
    project_id = data.nsxt_policy_project.default_project.id
  }
  display_name = var.tier1_name
}

data "nsxt_policy_lb_app_profile" "custom-fast-tcp" {
  display_name = var.custom-fast-tcp
}

data "nsxt_policy_lb_app_profile" "custom-fast-udp" {
  display_name = var.custom-fast-udp
}

data "nsxt_policy_lb_app_profile" "default_http_app_profile" {
  display_name = var.default-http-lb-app-profile
}

data "nsxt_policy_lb_app_profile" "default_tcp_app_profile" {
  display_name = var.default-tcp-lb-app-profile
}

data "nsxt_policy_lb_app_profile" "default_udp_app_profile" {
  display_name = var.default-udp-lb-app-profile
}

data "nsxt_policy_lb_persistence_profile" "default-source-ip" {
  display_name = var.default-source-ip-lb-persistence-profile
}

data "nsxt_policy_lb_persistence_profile" "default-cookie" {
  display_name = var.default-cookie-lb-persistence-profile
}

data "nsxt_policy_lb_client_ssl_profile" "default-balanced-client-ssl-profile" {
  display_name = var.default-balanced-client-ssl-profile
}

data "nsxt_policy_lb_server_ssl_profile" "default-balanced-server-ssl-profile" {
  display_name = var.default-balanced-server-ssl-profile
}

data "nsxt_policy_certificate" "hol-wildcard" {
  display_name = var.hol-wildcard
}

data "nsxt_policy_lb_monitor" "http-30001" {
  type         = "HTTP"
  display_name = "http-30001"
}
