# Update Flows in Development Environment
# Copies flows to JupyterLab and restarts workers

param(
    [switch]$Deploy
)

Write-Host "=== Updating Flows in Development Environment ===" -ForegroundColor Cyan
Write-Host ""

# 1. Find Jupyter pod
Write-Host "1. Finding JupyterLab pod..." -ForegroundColor Cyan
$pod = kubectl get pods -n mlops -l app.kubernetes.io/component=jupyter -o jsonpath="{.items[?(@.status.phase=='Running')].metadata.name}" 2>$null

if (-not $pod) {
    Write-Host "   X No running JupyterLab pod found" -ForegroundColor Red
    exit 1
}

Write-Host "   OK Found: $pod" -ForegroundColor Green
Write-Host ""

# 2. Copy flows
Write-Host "2. Copying flows to JupyterLab..." -ForegroundColor Cyan
kubectl exec -n mlops $pod -- bash -c "mkdir -p /home/jovyan/work/flows" | Out-Null

$flowsDir = "c:\IT\ml-setup-experiments\flows"
$files = @("train_model.py", "titanic.ipynb", "requirements.txt", "README.md", "self-deploying.py", "deploy_flows.py")

foreach ($file in $files) {
    $filePath = Join-Path $flowsDir $file
    if (Test-Path $filePath) {
        Write-Host "   Copying $file..." -ForegroundColor Gray
        $content = Get-Content $filePath -Raw -Encoding UTF8
        $tempFile = [System.IO.Path]::GetTempFileName()
        Set-Content -Path $tempFile -Value $content -NoNewline -Encoding UTF8
        Get-Content $tempFile -Raw | kubectl exec -i -n mlops $pod -- bash -c "cat > /home/jovyan/work/flows/$file"
        Remove-Item $tempFile
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   OK $file" -ForegroundColor Green
        } else {
            Write-Host "   FAILED $file" -ForegroundColor Red
        }
    }
}

Write-Host ""

# 3. Restart workers
Write-Host "3. Restarting workers..." -ForegroundColor Cyan
kubectl rollout restart deployment/prefect-worker -n mlops | Out-Null
kubectl rollout status deployment/prefect-worker -n mlops --timeout=60s | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "   OK Workers restarted" -ForegroundColor Green
} else {
    Write-Host "   WARNING Worker restart may have timed out" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "== All files updated!" -ForegroundColor Green

if ($Deploy) {
    Write-Host ""
    Write-Host "4. Deploying flows to Prefect..." -ForegroundColor Cyan
    $deployCmd = "cd /home/jovyan/work/flows ; python deploy_flows.py"
    kubectl exec -n mlops $pod -- bash -c $deployCmd 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   OK Flows deployed!" -ForegroundColor Green
        Write-Host "   View at: http://localhost:4200/deployments" -ForegroundColor Cyan
    } else {
        Write-Host "   FAILED Deployment error" -ForegroundColor Red
    }
} else {
    Write-Host ""
    Write-Host "To deploy flows to Prefect:" -ForegroundColor Yellow
    Write-Host "  .\copy-flows-to-jupyter.ps1 -Deploy" -ForegroundColor White
}

Write-Host ""
