# DANGER: Unprotected production cloud infrastructure
provider "aws" {
  region = "us-east-1"
}

resource "aws_rds_cluster" "production_db" {
  cluster_identifier = "prod-aurora-cluster"
  database_name      = "customer_records"
}

