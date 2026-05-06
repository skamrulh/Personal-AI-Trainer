resource "aws_db_subnet_group" "rds_subnets" {
  name       = "${local.name}-rds-subnet"
  subnet_ids = aws_subnet.public[*].id
}

resource "aws_db_instance" "postgres" {
  identifier           = "${local.name}-postgres"
  engine               = "postgres"
  instance_class       = "db.t3.micro"
  allocated_storage    = 20
  db_name              = "ptcoach"   # FIX 9: deprecated 'name' attr → 'db_name'
  username             = var.db_username
  password             = var.db_password
  skip_final_snapshot  = true
  db_subnet_group_name = aws_db_subnet_group.rds_subnets.name
}
