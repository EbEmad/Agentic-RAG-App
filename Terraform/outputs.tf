output "s3_bucket_name" {
  value = aws_s3_bucket.mlops_bucket.id
}

output "ec2_public_ip" {
  value = aws_instance.mlops_vm.public_ip
}
