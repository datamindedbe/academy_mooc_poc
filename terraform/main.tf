provider "aws" {
  region = "eu-west-1"
}


variable "your_public_ip" {
  type = string
}

variable "public_ssh_key" {
  type = string
}

resource "aws_instance" "airflow_server" {

  ami                    = "ami-0c1bc246476a5572b" # Amazon Linux 2 Kernel 5.10 AMI 2.0.20220426.0 x86_64 HVM gp2 - in EU-WEST-1
  instance_type          = "t3.medium"
  key_name               = aws_key_pair.ssh_key.key_name
  vpc_security_group_ids = [aws_security_group.main.id]
  
  root_block_device {
    volume_size = 15
    volume_type = "gp3"
  }

  tags = {
    Name = "MOOCAirflowServer"
  }
}

resource "aws_key_pair" "ssh_key" {
  key_name   = "my_ssh_key"
  public_key = var.public_ssh_key
}

resource "aws_security_group" "main" {
  egress = [
    {
      cidr_blocks = ["0.0.0.0/0", ]
      description = "Allow all outcoming connections to the outside world."
      from_port   = 0
      to_port     = 0

      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      protocol         = "-1"
      security_groups  = []
      self             = false
    }
  ]
  ingress = [
    {
      cidr_blocks      = ["${var.your_public_ip}/32",]
      description      = "Allow all incoming SSH connections from the outside world."
      from_port        = 22
      to_port          = 22
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      protocol         = "tcp"
      security_groups  = []
      self             = false
    },
    {
      cidr_blocks      = ["${var.your_public_ip}/32",]
      description      = "Allow all incoming connections from the outside world to the Airflow webserver."
      from_port        = 8080
      to_port          = 8080
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      protocol         = "tcp"
      security_groups  = []
      self             = false
    }
  ]
}

output "ec2_instance_public_ip" {
  value = aws_instance.airflow_server.public_ip
}
