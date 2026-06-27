<#
.SYNOPSIS
    SEO SWARM PowerShell Installer
.DESCRIPTION
    Installs SEO SWARM via npm, pip, or other package managers on Windows.
.EXAMPLE
    .\install.ps1
#>

Write-Host "`n🐝 SEO SWARM Windows Installer`n" -ForegroundColor Yellow

# Check for common package managers
$managers = @(
    @{Name="npm"; Exists=(Get-Command npm -ErrorAction SilentlyContinue); Cmd="npm install -g seo-swarm"},
    @{Name="yarn"; Exists=(Get-Command yarn -ErrorAction SilentlyContinue); Cmd="yarn global add seo-swarm"},
    @{Name="pnpm"; Exists=(Get-Command pnpm -ErrorAction SilentlyContinue); Cmd="pnpm add -g seo-swarm"},
    @{Name="bun"; Exists=(Get-Command bun -ErrorAction SilentlyContinue); Cmd="bun install -g seo-swarm"},
    @{Name="pip"; Exists=(Get-Command pip -ErrorAction SilentlyContinue); Cmd="pip install seo-swarm"},
    @{Name="pip3"; Exists=(Get-Command pip3 -ErrorAction SilentlyContinue); Cmd="pip3 install seo-swarm"}
)

foreach ($mgr in $managers) {
    if ($mgr.Exists) {
        Write-Host "✓ Installing via $($mgr.Name)..." -ForegroundColor Green
        Invoke-Expression $mgr.Cmd
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ SEO SWARM installed successfully!" -ForegroundColor Green
            Write-Host "  Run: seo-swarm --help" -ForegroundColor Cyan
            exit 0
        }
    }
}

Write-Host "✗ No supported package manager found." -ForegroundColor Red
Write-Host "  Install one of: npm, yarn, pnpm, bun, or pip" -ForegroundColor Yellow
exit 1
