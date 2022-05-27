output "ec2_instance_public_ip" {
  value = aws_instance.airflow_server.public_ip
}

output "dags_s3_bucket" {
  value = aws_s3_bucket.dags.id
}
