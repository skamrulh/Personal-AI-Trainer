resource "aws_lb" "alb" {
  name = "${local.name}-alb"
  internal = false
  load_balancer_type = "application"
  subnets = aws_subnet.public[*].id
  security_groups = [aws_security_group.alb.id]
}

resource "aws_lb_target_group" "tg" {
  name = "${local.name}-tg"
  port = 5000
  protocol = "HTTP"
  vpc_id = aws_vpc.main.id
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.alb.arn
  port = 80
  protocol = "HTTP"
  default_action { type = "forward"; target_group_arn = aws_lb_target_group.tg.arn }
}
