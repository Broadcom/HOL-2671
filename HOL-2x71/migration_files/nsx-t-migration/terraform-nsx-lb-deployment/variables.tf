variable "nsxt_host" {
  description = "The NSX-T Manager host. Must resolve to a reachable IP address, e.g. `nsxmgr.example.tld`"
  type        = string
}

variable "nsxt_username" {
  description = "The NSX-T username, probably `admin`"
  type        = string
}

variable "nsxt_password" {
  description = "The NSX-T password"
  type        = string
  sensitive   = true
}

variable "site_a_load_balancer_1" {
    description = "The name of the site a load balancer 1"
    type        = string
}

variable "tier1_name" {
    description = "The name of the tier 1 the load balancers will be connected to"
    type        = string
}

variable "site_a_pool_member_1_name" {
    description = "Name of site b pool member one"
    type        = string
}

variable "project_name" {}

variable "site_a_pool_member_1_ip" {
    description = "IP Address of site b pool member one"
    type        = string
}

variable "site_a_pool_member_2_name" {
    description = "Name of site b pool member two"
    type        = string
}

variable "site_a_pool_member_2_ip" {
    description = "IP Address of site b pool member two"
    type        = string
}

variable "default-http-lb-app-profile" {
    description = "Default http app profile"
    type        = string
}

variable "default-tcp-lb-app-profile" {
    description = "Default tcp app profile"
    type        = string
}

variable "custom-fast-tcp" {
    description = "custom-fast-tcp"
    type        = string
}

variable "default-udp-lb-app-profile" {
    description = "Default udp app profile"
    type        = string
}

variable "custom-fast-udp" {
    description = "custom-fast-tcp"
    type        = string
}


variable "http-to-https" {
    description = "Default udp app profile"
    type        = string
}

variable "default-cookie-lb-persistence-profile" {
    description = "Default Cookie Persistence profile"
    type        = string
}

variable "default-source-ip-lb-persistence-profile" {
    description = "Default Cookie Persistence profile"
    type        = string
}

variable "student_desktop" {
    description = "Student Desktop IP"
    type        = string
}

variable "hol-wildcard" {
    description = "HOL wildcard"
    type        = string
}

variable "default-balanced-client-ssl-profile" {
    description = "default-balanced-client-ssl-profile"
    type        = string
}

variable "default-balanced-server-ssl-profile" {
    description = "default-balanced-client-ssl-profile"
    type        = string
}

variable "http-30001" {
    description = "http-30001"
    type        = string
}
