<#
  Holder git opdateret på denne pc. Køres af sig selv, når man logger ind.

  Git-mappen ligger uden for Google Drive (Drive kan ødelægge en .git-mappe), så hver pc har sin egen.
  Filen .git i mad-mappen siger hvor (C:/Users/tobia/.git-repos/mad). Scriptet:
    1. henter repoet fra GitHub, hvis pc'en ikke har git-mappen endnu (en ny pc),
    2. slår core.autocrlf til, så Windows-linjeskift ikke ser ud som ændringer,
    3. henter det nyeste fra GitHub og retter historikken til, uden at røre filerne i Drive.
  Har pc'en commits, der ikke er pushet, rører det ingenting. Det committer og pusher aldrig selv:
  push går direkte ud på alles telefoner, og Drive kan stadig være i gang med at synkronisere.

  Én gang på en ny pc (i PowerShell):
    powershell -ExecutionPolicy Bypass -File "G:\My Drive\Privat\mad\git-start.ps1" -Installer
  Det lægger en genvej i Windows' Start-mappe og kører scriptet første gang. Loggen: %LOCALAPPDATA%\mad-git.log
#>
param([switch]$Installer)

$mappe = $PSScriptRoot
$repo = "https://github.com/tobias539/opbrugt.git"
$log = Join-Path $env:LOCALAPPDATA "mad-git.log"
function Skriv($t) {
  Add-Content -Path $log -Encoding UTF8 -Value ("{0}  {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $t)
  Write-Host $t
}

if ($Installer) {
  # Genvejen venter på, at Drive har monteret drevet (op til 5 min), før den kører scriptet
  $fil = Join-Path $mappe "git-start.ps1"
  $genvej = Join-Path ([Environment]::GetFolderPath("Startup")) "Mad app git.lnk"
  $g = (New-Object -ComObject WScript.Shell).CreateShortcut($genvej)
  $g.TargetPath = "powershell.exe"
  $g.Arguments = "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -Command `"`$f='$fil'; for(`$i=0; `$i -lt 60 -and -not (Test-Path `$f); `$i++){ Start-Sleep 5 }; if(Test-Path `$f){ & `$f }`""
  $g.WindowStyle = 7
  $g.Description = "Holder git for Mad app opdateret"
  $g.Save()
  Skriv "Installeret: $genvej"
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) { Skriv "Git er ikke installeret på denne pc (https://git-scm.com)."; exit 1 }
$gitfil = Join-Path $mappe ".git"
if (-not (Test-Path $gitfil -PathType Leaf)) { Skriv "Fandt ikke filen .git i $mappe."; exit 1 }
$gitdir = ((Get-Content $gitfil -Raw) -replace "^\s*gitdir:\s*", "").Trim()

# 1. Ny pc: hent repoet ind i den mappe, .git peger på. Filerne hentes ikke; dem har Drive allerede.
if (-not (Test-Path (Join-Path $gitdir "HEAD"))) {
  Skriv "Ny pc: henter repoet til $gitdir"
  New-Item -ItemType Directory -Force -Path (Split-Path $gitdir) | Out-Null
  $tmp = Join-Path $env:TEMP ("mad-tmp-" + [guid]::NewGuid().ToString("N").Substring(0, 8))
  git clone -q --no-checkout --separate-git-dir $gitdir $repo $tmp
  if ($LASTEXITCODE) { Skriv "Kunne ikke hente repoet fra GitHub."; exit 1 }
  Remove-Item -Recurse -Force $tmp
}

# 2. Linjeskift
git -C $mappe config core.autocrlf true

# 3. Det nyeste fra GitHub
git -C $mappe fetch -q origin
if ($LASTEXITCODE) { Skriv "Kunne ikke hente fra GitHub (er der net?)."; exit 1 }
$gren = git -C $mappe rev-parse --abbrev-ref HEAD
if ($gren -ne "main") { Skriv "Står på grenen '$gren' og ikke main. Rører ingenting."; exit 0 }
$ikkePushet = [int](git -C $mappe rev-list --count "origin/main..HEAD")
if ($ikkePushet -gt 0) { Skriv "$ikkePushet commit(s) på denne pc er ikke pushet endnu. Rører ingenting."; exit 0 }
git -C $mappe reset -q origin/main
$sidste = git -C $mappe log -1 --format="%h %s"
$aendret = @(git -C $mappe status --porcelain).Count
Skriv ("Opdateret til {0}. {1}" -f $sidste, $(if ($aendret) { "$aendret fil(er) i mappen er ændret og ikke committet." } else { "Ingen ændringer mangler at blive committet." }))
