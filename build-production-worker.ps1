# Build Production Worker Image with Flows Baked In
# This creates an immutable image for production deployments

param(
    [string]$Registry = "your-registry.com",
    [string]$Version = "v1.0.0",
    [switch]$Push
)

Write-Host "=== Building Production Prefect Worker Image ===" -ForegroundColor Cyan
Write-Host ""

$imageName = "$Registry/prefect-worker-with-flows:$Version"
$imageLatest = "$Registry/prefect-worker-with-flows:latest"

# Build the image from project root
Write-Host "Building image: $imageName" -ForegroundColor Cyan
docker build `
    -f helm-charts/ml-platform/charts/prefect/Dockerfile.worker-production `
    -t $imageName `
    -t $imageLatest `
    .

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Build failed" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Image built successfully!" -ForegroundColor Green
Write-Host ""

if ($Push) {
    Write-Host "Pushing to registry..." -ForegroundColor Cyan
    docker push $imageName
    docker push $imageLatest
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Images pushed to registry" -ForegroundColor Green
        Write-Host ""
        Write-Host "To deploy to production:" -ForegroundColor Yellow
        Write-Host "  1. Update values-production.yaml:" -ForegroundColor White
        Write-Host "     prefect.worker.image.repository: $Registry/prefect-worker-with-flows" -ForegroundColor Gray
        Write-Host "     prefect.worker.image.tag: $Version" -ForegroundColor Gray
        Write-Host ""
        Write-Host "  2. Deploy with Helm:" -ForegroundColor White
        Write-Host "     helm upgrade ml-platform ./helm-charts/ml-platform -f helm-charts/ml-platform/values-production.yaml -n mlops-prod" -ForegroundColor Gray
    } else {
        Write-Host "✗ Push failed" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Image built locally. To push to registry, run:" -ForegroundColor Yellow
    Write-Host "  .\build-production-worker.ps1 -Registry $Registry -Version $Version -Push" -ForegroundColor White
}

Write-Host ""
Write-Host "Image details:" -ForegroundColor Cyan
Write-Host "  Name: $imageName" -ForegroundColor White
Write-Host "  Contains: Prefect worker + all flows from flows/ directory" -ForegroundColor White
Write-Host "  Python Path: /opt/prefect/flows" -ForegroundColor White
