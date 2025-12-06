resource "aws_db_subnet_group" "rds_subnets" {
  name = "${local.name}-rds-subnet"
  subnet_ids = aws_subnet.public[*].id
}

resource "aws_db_instance" "postgres" {
  identifier = "${local.name}-postgres"
  engine = "postgres"
  instance_class = "db.t3.micro"
  allocated_storage = 20
  name = "ptcoach"
  username = var.db_username
  password = var.db_password
  skip_final_snapshot = true
  db_subnet_group_name = aws_db_subnet_group.rds_subnets.name
}
