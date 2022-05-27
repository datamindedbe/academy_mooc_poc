data "aws_caller_identity" "current" {}

resource "aws_s3_bucket" "dags" {
  bucket = "mooc-dags-${data.aws_caller_identity.current.account_id}"
}
