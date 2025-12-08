
resource "local_file" "infra_tfvars" {
  filename = "../../code/infra/vars_test.tfvars"
  content  = local.tfvars

  lifecycle {
    prevent_destroy = true
  }
}
