provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "prod_assets" {
  bucket = "prod-service-assets-bucket"
}

