# Build and Deploy Bundled Flows Image
# Run this script whenever you update the flows

Write-Host "Building bundled-flows image..." -ForegroundColor Cyan

# Build the image from flows-container with parent context
docker build -t bundled-flows:latest -f flows-container/Dockerfile .

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Image built successfully" -ForegroundColor Green
    
    # Upgrade Helm release
    Write-Host "Upgrading Helm release..." -ForegroundColor Cyan
    helm upgrade ml-platform ./helm-charts/ml-platform -n mlops -f helm-charts/ml-platform/values-dev.yaml
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Helm upgrade complete" -ForegroundColor Green
        
        # Restart JupyterLab to pick up new flows
        Write-Host "Restarting JupyterLab..." -ForegroundColor Cyan
        kubectl delete pod -n mlops -l app.kubernetes.io/component=jupyter
        
        Write-Host "✓ Done! Waiting for pod to be ready..." -ForegroundColor Green
        kubectl wait --for=condition=ready pod -n mlops -l app.kubernetes.io/component=jupyter --timeout=120s
    }
} else {
    Write-Host "✗ Image build failed" -ForegroundColor Red
    exit 1
}
