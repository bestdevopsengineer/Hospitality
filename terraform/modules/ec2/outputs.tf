output "instance_id" {
  value = aws_instance.jump_server.id
}

output "private_ip" {
  value = aws_instance.jump_server.private_ip
}