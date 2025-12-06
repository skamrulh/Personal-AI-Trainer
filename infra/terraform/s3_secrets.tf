resource "random_id" "bucket_id" { byte_length = 4 }

resource "aws_s3_bucket" "assets" {
  bucket = "${local.name}-assets-${random_id.bucket_id.hex}"
  acl = "private"
}

resource "aws_secretsmanager_secret" "openai" {
  name = "${local.name}/openai"
}
