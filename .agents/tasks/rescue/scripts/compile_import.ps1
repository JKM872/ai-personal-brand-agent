Set-Location "C:\Users\hp\Documents\antigravity\mysterious-darwin"
$env:PYTHONIOENCODING = "utf-8"
$f = Get-ChildItem -Recurse -Filter *.py | Where-Object { $_.FullName -notmatch '\\.agents\\|__pycache__|\\.git\\' }
$bad = 0
foreach ($x in $f) { python -m py_compile $x.FullName; if ($LASTEXITCODE) { $bad++; "FAIL $($x.FullName)" } }
"py_compile FAIL=$bad z $($f.Count)"
$root = (Get-Location).Path
$mods = $f | Where-Object { $_.FullName -notmatch '\\queue\\|\\tests\\' } | ForEach-Object { $_.FullName.Substring($root.Length + 1) -replace '\.py$', '' -replace '\\', '.' } | Where-Object { $_ -notmatch '__init__$' }
$ibad = 0
foreach ($m in $mods) { python -c "import importlib; importlib.import_module('$m')" *> $null; if ($LASTEXITCODE) { $ibad++; "IMPORT FAIL $m" } else { "IMPORT OK $m" } }
"import FAIL=$ibad z $($mods.Count)"
git status --short
