terraform {
  required_providers {
    avi = {
      source = "vmware/avi"
    }
  }
}

provider "avi" {
  avi_username             = "admin"
  avi_password             = "VMware123!"
  avi_controller           = "avicon-01a.vcf.sddc.lab"
  avi_version              = "30.2.1"
}