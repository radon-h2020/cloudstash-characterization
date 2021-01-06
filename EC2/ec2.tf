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


  # execute commands on the server
  provisioner "remote-exec" {
    inline = [
      # wait for cloud-init to finish
      "while [ ! -f /var/lib/cloud/instance/boot-finished ]; do echo 'Waiting for cloud-init...'; sleep 1; done",

      # update system
      "sudo apt-get update -q",
      "sudo apt-get upgrade -qq",

      # will install both docker and docker-compose
      "sudo apt-get install -qq moreutils docker-compose",
      # enable docker deamon
      "sudo systemctl enable --now docker",
      # add user to docker group
      "sudo usermod -aG docker ubuntu",

      # TODO add docker image(s)
      # "sudo docker pull -q ..."
      "git clone https://github.com/radon-h2020/cloudstash-characterization"
    ]
  }
}
