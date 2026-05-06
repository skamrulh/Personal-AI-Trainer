# FIX 8: Terraform HCL does NOT use commas between variable block attributes.
# type and default must be on separate lines (or use semicolons, not commas).

variable "region" {
  type    = string
  default = "us-east-1"
}

variable "project" {
  type    = string
  default = "pt-coach"
}

variable "tf_state_bucket" {
  type        = string
  description = "S3 bucket name for Terraform remote state"
}

variable "tf_state_lock_table" {
  type        = string
  description = "DynamoDB table name for Terraform state locking"
}

variable "db_username" {
  type    = string
  default = "ptadmin"
}

variable "db_password" {
  type      = string
  sensitive = true
}
