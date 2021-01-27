resource "aws_instance" "orchestrator" {
  key_name      = aws_key_pair.ubuntu.key_name
  ami           = "ami-01996625fff6b8fcc"
  instance_type = "t3.micro" # free-tier in Stockholm. t2 unavailable

  tags = {
    Name = "cloudstash_characterization_orchestrator"
  }

  vpc_security_group_ids = [
    aws_security_group.ubuntu.id
  ]

  connection {
    type        = "ssh"
    user        = "ubuntu"
    private_key = file(var.ssh_key_path)
    host        = self.public_ip
  }

  ebs_block_device {
    device_name = "/dev/sda1"
    volume_type = "gp2"
    volume_size = 30
  }
}

# Run provisioners over SSH after instance
# has been created and recieved a public ip address
resource "null_resource" "orchestrator-provisioner" {
  # run the provisioners after the instance has been created
  # and the ip address has been assigned
  depends_on = [
    aws_eip.ubuntu,
    aws_instance.orchestrator
  ]
  connection {
    type        = "ssh"
    user        = "ubuntu"
    private_key = file(var.ssh_key_path)
    host        = aws_eip.ubuntu.public_ip
  }

  # put deployment key
  provisioner "file" {
    source = var.cloudstash_deployment_key
    destination = "/home/ubuntu/.ssh/id_rsa"
  }
  # put aws credentials
  provisioner "file" {
    source = "secrets/.aws"
    destination = "/home/ubuntu/.aws"
  }


  # execute commands on the server
  provisioner "remote-exec" {
    inline = [
      # wait for cloud-init to finish
      "while [ ! -f /var/lib/cloud/instance/boot-finished ]; do echo 'Waiting for cloud-init...'; sleep 1; done",

      # update system
      "sudo apt-get update -q",
      "sudo apt-get upgrade -qq",

      # will install both docker and docker-compose
      "sudo DEBIAN_FRONTEND=noninteractive apt-get install -qq moreutils docker-compose awscli gnupg2 pass",
      # enable docker deamon
      "sudo systemctl enable --now docker",
      # add user to docker group
      "sudo usermod -aG docker ubuntu",

      # login to github docker registry
      "echo ${var.github_personal_access_token} | docker login https://docker.pkg.github.com -u ${var.github_username} --password-stdin",

      # pull docker image
      "docker pull docker.pkg.github.com/radon-h2020/cloudstash-characterization/cloudstash-benchmarker:main",

      # pull the characterization repository
      "git clone https://github.com/radon-h2020/cloudstash-characterization",

      # pull cloudstash repository from eficode git using deployment key
      "chown -R ubuntu:ubuntu /home/ubuntu/.aws",
      "chmod 600 /home/ubuntu/.ssh/id_rsa",
      "ssh-keyscan ssh-keyscan -H ${var.cloudstash_git_host} >> /home/ubuntu/.ssh/known_hosts",
      "git clone ${var.cloudstash_repository}",
    ]
  }
}
