resource "aws_ecr_repository" "backend" {
  name = "${local.name}-backend"
}
resource "aws_ecr_repository" "frontend" {
  name = "${local.name}-frontend"
}
resource "aws_ecs_cluster" "main" {
  name = "${local.name}-ecs-cluster"
}
resource "aws_cloudwatch_log_group" "ecs" {
  name = "/ecs/${local.name}"
  retention_in_days = 14
}
