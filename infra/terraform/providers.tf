terraform {
  required_version = ">= 1.3.0"
  required_providers {
    aws = { source = "hashicorp/aws" }
    random = { source = "hashicorp/random" }
  }
  backend "s3" {
    bucket = var.tf_state_bucket
    key    = "${var.project}/terraform.tfstate"
    region = var.region
    dynamodb_table = var.tf_state_lock_table
  }
}

provider "aws" {
  region = var.region
}
