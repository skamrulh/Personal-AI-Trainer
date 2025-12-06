variable "region" { type = string, default = "us-east-1" }
variable "project" { type = string, default = "pt-coach" }
variable "tf_state_bucket" { type = string }
variable "tf_state_lock_table" { type = string }
variable "db_username" { type = string, default = "ptadmin" }
variable "db_password" { type = string }
