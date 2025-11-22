# Terraform Deployment Script
# Usage: .\deploy.ps1 [-Action init|plan|apply|destroy]

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("init", "plan", "apply", "destroy", "output")]
    [string]$Action = "plan"
)

$ErrorActionPreference = "Stop"
$LogFile = "terraform-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"

function Write-Log {
    param([string]$Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] $Message"
    Write-Host $LogMessage
    Add-Content -Path $LogFile -Value $LogMessage
}

function Test-TerraformVars {
    if (-not (Test-Path "terraform.tfvars")) {
        Write-Log "ERROR: terraform.tfvars not found"
        Write-Log "Copy terraform.tfvars.example and fill with your keys"
        exit 1
    }
    
    $Content = Get-Content "terraform.tfvars" -Raw
    if ($Content -match "VOTRE_CLE") {
        Write-Log "ERROR: terraform.tfvars contains placeholder values"
        Write-Log "Replace all VOTRE_CLE_* with real API keys"
        exit 1
    }
    
    Write-Log "terraform.tfvars validation passed"
}

Write-Log "Starting Terraform $Action operation"
Write-Log "Log file: $LogFile"

# Navigate to terraform directory if not already there
$TerraformDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $TerraformDir
Write-Log "Working directory: $TerraformDir"

switch ($Action) {
    "init" {
        Write-Log "Initializing Terraform (downloading Render provider)"
        terraform init | Tee-Object -FilePath $LogFile -Append
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Terraform initialized successfully"
        } else {
            Write-Log "ERROR: Terraform init failed with exit code $LASTEXITCODE"
            exit $LASTEXITCODE
        }
    }
    
    "plan" {
        Test-TerraformVars
        Write-Log "Planning infrastructure changes (dry-run)"
        terraform plan -out=tfplan | Tee-Object -FilePath $LogFile -Append
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Plan generated successfully - review output above"
            Write-Log "To apply: .\deploy.ps1 -Action apply"
        } else {
            Write-Log "ERROR: Terraform plan failed with exit code $LASTEXITCODE"
            exit $LASTEXITCODE
        }
    }
    
    "apply" {
        Test-TerraformVars
        
        if (Test-Path "tfplan") {
            Write-Log "Applying saved plan (tfplan)"
            terraform apply tfplan | Tee-Object -FilePath $LogFile -Append
            Remove-Item "tfplan" -ErrorAction SilentlyContinue
        } else {
            Write-Log "Creating infrastructure (will prompt for confirmation)"
            terraform apply | Tee-Object -FilePath $LogFile -Append
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Infrastructure deployed successfully"
            Write-Log "Fetching outputs..."
            terraform output | Tee-Object -FilePath $LogFile -Append
        } else {
            Write-Log "ERROR: Terraform apply failed with exit code $LASTEXITCODE"
            exit $LASTEXITCODE
        }
    }
    
    "destroy" {
        Write-Log "WARNING: This will DELETE all infrastructure"
        $Confirmation = Read-Host "Type 'destroy' to confirm"
        
        if ($Confirmation -eq "destroy") {
            Write-Log "Destroying infrastructure"
            terraform destroy | Tee-Object -FilePath $LogFile -Append
            
            if ($LASTEXITCODE -eq 0) {
                Write-Log "Infrastructure destroyed successfully"
            } else {
                Write-Log "ERROR: Terraform destroy failed with exit code $LASTEXITCODE"
                exit $LASTEXITCODE
            }
        } else {
            Write-Log "Destroy cancelled"
            exit 0
        }
    }
    
    "output" {
        Write-Log "Fetching deployment outputs"
        terraform output | Tee-Object -FilePath $LogFile -Append
    }
}

Write-Log "Operation completed"
Write-Log "Full log saved to: $LogFile"
