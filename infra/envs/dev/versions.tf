terraform {
  required_version = ">= 1.9"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.70"
    }
  }

  # Remote state. Values come from backend.hcl (see infra/README.md):
  #   terraform init -backend-config=backend.hcl
  backend "s3" {
    key     = "dev/terraform.tfstate"
    encrypt = true
  }
}
