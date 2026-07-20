$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$pgBin = Join-Path $projectRoot ".local\postgresql-runtime\pgsql\bin"
$data = Join-Path $projectRoot ".local\pgdata"
$log = Join-Path $projectRoot ".local\postgresql.log"

if (-not (Test-Path -LiteralPath (Join-Path $pgBin "pg_ctl.exe"))) {
    throw "PostgreSQL local no está instalado en .local. Consulta el README."
}

& (Join-Path $pgBin "pg_isready.exe") -h 127.0.0.1 -p 55432 | Out-Null
if ($LASTEXITCODE -ne 0) {
    & (Join-Path $pgBin "pg_ctl.exe") -D $data -l $log -o '"-p 55432 -h 127.0.0.1"' start
}

& (Join-Path $pgBin "pg_isready.exe") -h 127.0.0.1 -p 55432
