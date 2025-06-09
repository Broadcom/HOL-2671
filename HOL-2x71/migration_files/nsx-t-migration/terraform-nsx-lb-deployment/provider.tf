terraform {
  required_providers {
    nsxt = {
      source = "vmware/nsxt"
    }
  }
}

provider "nsxt" {
  username             = var.nsxt_username
  password             = var.nsxt_password
  host                 = var.nsxt_host
  allow_unverified_ssl = true
}
