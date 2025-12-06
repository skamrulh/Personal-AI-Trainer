output "ecr_backend" { value = aws_ecr_repository.backend.repository_url }
output "ecr_frontend" { value = aws_ecr_repository.frontend.repository_url }
output "alb_dns" { value = aws_lb.alb.dns_name }
output "redis_endpoint" { value = aws_elasticache_cluster.redis.cache_nodes[0].address }
output "rds_endpoint" { value = aws_db_instance.postgres.address }
output "s3_assets" { value = aws_s3_bucket.assets.bucket }
