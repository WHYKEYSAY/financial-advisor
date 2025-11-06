# Batch upload bank statements to CreditSphere API
# Usage: .\batch_upload.ps1

$token = Read-Host "Enter your access_token"
$apiUrl = "http://localhost:8000/files/upload"
$folder = "C:\Users\whyke\financial-advisor\bankstatement"

# Get all PDF and CSV files
$files = Get-ChildItem -Path $folder -Include *.pdf,*.csv,*.PDF,*.CSV -Recurse

Write-Host "Found $($files.Count) files to upload" -ForegroundColor Green

foreach ($file in $files) {
    Write-Host "`nUploading: $($file.Name)..." -ForegroundColor Cyan
    
    try {
        # Use curl via WSL for multipart/form-data
        $result = wsl bash -c "curl -s -X POST '$apiUrl' -H 'Authorization: Bearer $token' -F 'file=@$($file.FullName.Replace('\', '/').Replace('C:', '/mnt/c'))'"
        
        # Parse JSON response
        $response = $result | ConvertFrom-Json
        
        if ($response.message) {
            Write-Host "  ✓ $($response.message)" -ForegroundColor Green
            Write-Host "    Statement ID: $($response.statement_id)" -ForegroundColor Gray
        } else {
            Write-Host "  ✗ Upload failed" -ForegroundColor Red
            Write-Host "    $result" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "  ✗ Error: $_" -ForegroundColor Red
    }
    
    Start-Sleep -Seconds 1  # Avoid rate limiting
}

Write-Host "`n✓ Batch upload complete!" -ForegroundColor Green
