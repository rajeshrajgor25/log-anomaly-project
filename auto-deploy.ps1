# Auto-deploy script for Minikube
# This script restarts deployments every minute to pick up new :latest images

Write-Host "Starting auto-deploy watcher..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow

# Check if Minikube is running
function Test-MinikubeRunning {
    try {
        $null = kubectl cluster-info 2>$null
        return $true
    }
    catch {
        return $false
    }
}

while ($true) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] Checking for new images..." -ForegroundColor Cyan
    
    # Check if Minikube is running
    if (-not (Test-MinikubeRunning)) {
        Write-Host "[$timestamp] Minikube not running. Starting minikube..." -ForegroundColor Yellow
        minikube start
    }
    
    try {
        # Restart backend deployment
        kubectl rollout restart deployment log-anomaly-backend
        Write-Host "  ✓ Restarted log-anomaly-backend" -ForegroundColor Green
        
        # Restart frontend deployment
        kubectl rollout restart deployment log-anomaly-frontend
        Write-Host "  ✓ Restarted log-anomaly-frontend" -ForegroundColor Green
        
        # Wait for rollout to complete
        Write-Host "  Waiting for rollout to complete..." -ForegroundColor Yellow
        kubectl rollout status deployment/log-anomaly-backend --timeout=120s
        kubectl rollout status deployment/log-anomaly-frontend --timeout=120s
        
        Write-Host "[$timestamp] Deployments updated successfully!" -ForegroundColor Green
    }
    catch {
        Write-Host "[$timestamp] Error: $_" -ForegroundColor Red
    }
    
    Write-Host "  Next update in 60 seconds..." -ForegroundColor Cyan
    Start-Sleep -Seconds 60
}