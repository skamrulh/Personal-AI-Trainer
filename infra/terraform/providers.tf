# FIX 5: Terraform backend blocks CANNOT reference var.*
# Variables are forbidden in backend configuration.
# Use -backend-config CLI flags or a separate backend.hcl file at terraform init time.
#
# Usage:
#   terraform init \
#     -backend-config="bucket=my-tf-state-bucket" \
#     -backend-config="key=pt-coach/terraform.tfstate" \
#     -backend-config="region=us-east-1" \
#     -backend-config="dynamodb_table=my-tf-lock-table"
#
# Or create a backend.hcl file (not committed) with those values.

terraform {
  required_version = ">= 1.3.0"
  required_providers {
    aws    = { source = "hashicorp/aws",    version = "~> 5.0" }
    random = { source = "hashicorp/random", version = "~> 3.0" }
  }

  # FIX 5: bucket/key/region/dynamodb_table supplied via -backend-config flags.
  # Do NOT hardcode secrets or account-specific values here.
  backend "s3" {}
}

provider "aws" {
  region = var.region
}
