param([string]$Out, [switch]$Offline)
$ErrorActionPreference = "Continue"
$R = "C:\Users\hp\Documents\antigravity\mysterious-darwin"
$t = "$env:TEMP\md_dry"
if (Test-Path $t) { Remove-Item $t -Recurse -Force }
robocopy $R $t /E /XD .git .agents __pycache__ /NFL /NDL /NJH /NJS | Out-Null
Push-Location $t
git init -q; git add -A; git -c user.name=a -c user.email=a@a commit -qm base | Out-Null
Get-ChildItem Env: | Where-Object { $_.Name -match 'KEY|TOKEN|WEBHOOK|SUPABASE|CMS_|LINKEDIN|TELEGRAM|DRY_RUN|OFFLINE' } | ForEach-Object { Remove-Item "Env:$($_.Name)" }
if ($Offline) { $env:OFFLINE = "1" }
$env:PYTHONIOENCODING = "utf-8"
python engine.py *> run.txt
$ec = $LASTEXITCODE
git status --short --untracked-files=all | Out-File status.txt -Encoding utf8
$bundles = git status --short --untracked-files=all | Where-Object { $_ -match '^\?\? queue/' } | ForEach-Object { $_.Substring(3) }
$bundles | Out-File bundle_files.txt -Encoding utf8
Pop-Location
New-Item -ItemType Directory -Force $Out | Out-Null
Copy-Item "$t\run.txt", "$t\status.txt", "$t\bundle_files.txt" $Out
"$ec" | Out-File "$Out\exit.txt" -Encoding utf8
"EXIT=$ec"
