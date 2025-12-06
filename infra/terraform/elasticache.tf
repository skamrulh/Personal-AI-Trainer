resource "aws_elasticache_subnet_group" "redis" {
  name = "${local.name}-redis-subnet"
  subnet_ids = aws_subnet.public[*].id
}

resource "aws_elasticache_cluster" "redis" {
  cluster_id = "${local.name}-redis"
  engine = "redis"
  node_type = "cache.t3.micro"
  num_cache_nodes = 1
  subnet_group_name = aws_elasticache_subnet_group.redis.name
}
