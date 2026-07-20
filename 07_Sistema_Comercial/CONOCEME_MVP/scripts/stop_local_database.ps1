$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$pgCtl = Join-Path $projectRoot ".local\postgresql-runtime\pgsql\bin\pg_ctl.exe"
$data = Join-Path $projectRoot ".local\pgdata"

if (Test-Path -LiteralPath $pgCtl) {
    & $pgCtl -D $data stop -m fast
}
