Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$credentialRoot=Join-Path $PSScriptRoot '_local'
[System.IO.Directory]::CreateDirectory($credentialRoot) | Out-Null
$form=New-Object System.Windows.Forms.Form
$form.Text='教材实验 · DeepSeek 本地配置'
$form.Size=New-Object System.Drawing.Size(620,280)
$form.StartPosition='CenterScreen'
$form.TopMost=$true
$form.Font=New-Object System.Drawing.Font('Microsoft YaHei',10)
$label=New-Object System.Windows.Forms.Label
$label.Location=New-Object System.Drawing.Point(22,18)
$label.Size=New-Object System.Drawing.Size(568,70)
$label.Text="请输入 DeepSeek API Key（不是密钥 ID）。`r`n验证地址：https://api.deepseek.com`r`n凭据仅由当前 Windows 账户加密保存，不放入教材资料包。"
$form.Controls.Add($label)
$inputBox=New-Object System.Windows.Forms.TextBox
$inputBox.Location=New-Object System.Drawing.Point(24,100)
$inputBox.Size=New-Object System.Drawing.Size(555,28)
$inputBox.UseSystemPasswordChar=$true
$form.Controls.Add($inputBox)
$status=New-Object System.Windows.Forms.Label
$status.Location=New-Object System.Drawing.Point(24,143)
$status.Size=New-Object System.Drawing.Size(555,40)
$form.Controls.Add($status)
$button=New-Object System.Windows.Forms.Button
$button.Text='验证并保存'
$button.Location=New-Object System.Drawing.Point(420,190)
$button.Size=New-Object System.Drawing.Size(160,32)
$form.Controls.Add($button)
$form.AcceptButton=$button
$button.Add_Click({
    if ([string]::IsNullOrWhiteSpace($inputBox.Text)) { $status.Text='请填写 API Key。'; return }
    $button.Enabled=$false
    $status.Text='正在验证连接……'
    $form.Refresh()
    try {
        $keyForRequest=$inputBox.Text.Trim()
        $models=Invoke-RestMethod -Uri 'https://api.deepseek.com/models' -Headers @{Authorization=('Bearer '+$keyForRequest)} -TimeoutSec 25
        $secureValue=ConvertTo-SecureString $keyForRequest -AsPlainText -Force
        $credential=New-Object System.Management.Automation.PSCredential('DeepSeek',$secureValue)
        $credential | Export-Clixml -LiteralPath (Join-Path $credentialRoot 'deepseek.credential.xml')
        @{ready=$true;verified_at=(Get-Date).ToString('o');models=@($models.data.id);host='api.deepseek.com'} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $credentialRoot 'connection_status.json') -Encoding UTF8
        $keyForRequest=$null
        $inputBox.Clear()
        $form.Close()
    } catch {
        $code=if($_.Exception.Response){[int]$_.Exception.Response.StatusCode}else{'network'}
        $status.Text="验证失败（$code）。请检查密钥和账户后重试。"
        $button.Enabled=$true
    }
})
[void]$form.ShowDialog()
$form.Dispose()
