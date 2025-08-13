resource "aws_s3_bucket" "mlops_bucket" {
  bucket = var.s3_bucket_name

  tags = {
    Name        = "mlops-artifact-store"
    Environment = "dev"
  }
}
