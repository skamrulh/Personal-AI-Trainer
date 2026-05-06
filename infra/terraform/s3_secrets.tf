resource "random_id" "bucket_id" { byte_length = 4 }

resource "aws_s3_bucket" "assets" {
  bucket = "${local.name}-assets-${random_id.bucket_id.hex}"
}

# FIX 11: acl = "private" is deprecated in AWS provider v4+.
# Use aws_s3_bucket_ownership_controls + aws_s3_bucket_acl instead.
resource "aws_s3_bucket_ownership_controls" "assets" {
  bucket = aws_s3_bucket.assets.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "assets" {
  depends_on = [aws_s3_bucket_ownership_controls.assets]
  bucket     = aws_s3_bucket.assets.id
  acl        = "private"
}

resource "aws_secretsmanager_secret" "openai" {
  name = "${local.name}/openai"
}
