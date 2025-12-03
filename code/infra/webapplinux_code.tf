resource "null_resource" "linux_web_app_app_deployment" {
  count = var.web_app_code_path != "" ? 1 : 0

  triggers = {
    file = one(data.archive_file.file_web_app[*].output_base64sha256)
  }

  provisioner "local-exec" {
    command = "az webapp deploy --resource-group ${azurerm_linux_web_app.linux_web_app.resource_group_name} --name ${azurerm_linux_web_app.linux_web_app.name} --src-path ${one(data.archive_file.file_web_app[*].output_path)}"
  }
}