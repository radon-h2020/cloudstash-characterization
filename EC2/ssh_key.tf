resource "aws_key_pair" "ubuntu" {
  key_name   = "ubuntu"
  public_key = file(var.ssh_pubkey_path)
}
