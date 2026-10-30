$ErrorActionPreference = "Continue"
$R = "C:\Users\hp\Documents\antigravity\mysterious-darwin"
$F = "$R\.agents\tasks\rescue\final"
New-Item -ItemType Directory -Force $F | Out-Null
$env:PYTHONIOENCODING = "utf-8"
Set-Location $R
"== unittest (z e2e) ==" ; python -m unittest discover -s tests -v *> "$F\unittest.txt"; "unittest EXIT=$LASTEXITCODE"; Get-Content "$F\unittest.txt" | Select-Object -Last 4
"== compile/import ==" ; powershell -NoProfile -ExecutionPolicy Bypass -File "$R\.agents\tasks\rescue\scripts\compile_import.ps1" *> "$F\compile_import.txt"; Get-Content "$F\compile_import.txt" | Select-String 'FAIL|z \d'
"== dry run (siec) ==" ; powershell -NoProfile -ExecutionPolicy Bypass -File "$R\.agents\tasks\rescue\scripts\dryrun.ps1" -Out "$F\online"
"== dry run (OFFLINE) ==" ; powershell -NoProfile -ExecutionPolicy Bypass -File "$R\.agents\tasks\rescue\scripts\dryrun.ps1" -Out "$F\offline" -Offline
$t = "$env:TEMP\md_dry"
Push-Location $t
Get-ChildItem Env: | Where-Object { $_.Name -match 'KEY|TOKEN|WEBHOOK|SUPABASE|CMS_|LINKEDIN|TELEGRAM|DRY_RUN' } | ForEach-Object { Remove-Item "Env:$($_.Name)" }
"== approve/publish/leads w kopii ==" | Tee-Object "$F\cli.txt"
python approve.py list *>> "$F\cli.txt"; "approve list EXIT=$LASTEXITCODE" | Tee-Object -Append "$F\cli.txt"
$first = (Get-Content status.txt | Where-Object { $_ -match 'APPROVAL.json' } | Select-Object -First 1).Substring(3).Split('/')[1]
python approve.py approve $first *>> "$F\cli.txt"; "approve EXIT=$LASTEXITCODE ($first)" | Tee-Object -Append "$F\cli.txt"
python publish.py *>> "$F\cli.txt"; "publish EXIT=$LASTEXITCODE" | Tee-Object -Append "$F\cli.txt"
python approve.py approve nie-ma-takiej *>> "$F\cli.txt"; "approve missing EXIT=$LASTEXITCODE (oczekiwane 2)" | Tee-Object -Append "$F\cli.txt"
$env:LOCAL_DB_PATH = "$t\db\cli_test.db"
python leads.py add --name Test --email t@example.com *>> "$F\cli.txt"; "leads add EXIT=$LASTEXITCODE" | Tee-Object -Append "$F\cli.txt"
python leads.py list *>> "$F\cli.txt"; "leads list EXIT=$LASTEXITCODE" | Tee-Object -Append "$F\cli.txt"
python -m agents.analyst_agent --reset-stats *>> "$F\cli.txt"; "reset-stats bez --yes EXIT=$LASTEXITCODE (oczekiwane 2)" | Tee-Object -Append "$F\cli.txt"
Remove-Item Env:LOCAL_DB_PATH
git status --short --untracked-files=all | Out-File "$F\status_after_approve.txt" -Encoding utf8
Pop-Location
Get-Content "$F\cli.txt" | Select-String 'EXIT|DRY_RUN_SKIPPED|opublikowany' | ForEach-Object Line
"== html ==" ; python -m unittest tests.test_public_html -v *> "$F\html.txt"; "html EXIT=$LASTEXITCODE"
"== repo ==" ; git status --short | Select-String '^ ?D .*(queue/|public/articles/)'; "secrets:"; git grep -nE "AIza|gsk_|ghp_[A-Za-z0-9]{20}" -- . ':!.agents'
