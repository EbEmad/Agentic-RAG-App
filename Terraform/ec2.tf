resource "aws_eip" "static_ip" {
  instance = aws_instance.mlops_vm.id
}

resource "aws_security_group" "ssh" {
  name_prefix = "mlops-ssh"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 5000
    to_port     = 5050
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 4200
    to_port     = 4200
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

data "aws_subnet" "default" {
  filter {
    name   = "default-for-az"
    values = ["true"]
  }

  filter {
    name   = "availability-zone"
    values = ["us-east-1a"]  # Match your region/zone
  }
}



resource "aws_instance" "mlops_vm" {
  ami           = "ami-0001c5332b86ed44b"
  instance_type = "t2.micro"
  key_name      = "Master"
  vpc_security_group_ids = [aws_security_group.ssh.id]
  iam_instance_profile = aws_iam_instance_profile.mlflow_instance_profile.name

  #lifecycle {
  #  prevent_destroy = true
  #}
  associate_public_ip_address = false 
  
  tags = {
    Name = "mlops-instance"
  }

  provisioner "remote-exec" {
    inline = [
      "curl -fsSL https://get.docker.com -o get-docker.sh",
      "sh get-docker.sh",
      "sudo usermod -aG docker ubuntu"
    ]

    connection {
      type        = "ssh"
      user        = "ubuntu"
      private_key = file("../Master.pem")
      host        = self.public_ip
      timeout     = "5m"  
    }
  }


  depends_on = [aws_security_group.ssh]  

}

resource "aws_eip_association" "eip_assoc" {
  instance_id   = aws_instance.mlops_vm.id
  allocation_id = aws_eip.static_ip.id
}