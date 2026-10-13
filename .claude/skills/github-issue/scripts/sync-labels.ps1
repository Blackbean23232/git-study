# Sync labels.json to the current GitHub repo. Idempotent: only missing labels are created.
# A label with "rename_from" renames that existing label instead of creating a duplicate.
# Keep this file ASCII-only (Windows PowerShell 5.1 misreads non-BOM UTF-8 scripts).
param(
    [string]$Catalog = (Join-Path $PSScriptRoot '..\references\labels.json')
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [Text.Encoding]::UTF8
$utf8 = New-Object Text.UTF8Encoding($false)

$labels = [IO.File]::ReadAllText($Catalog, $utf8) | ConvertFrom-Json
$existing = @(gh api 'repos/{owner}/{repo}/labels' --paginate --jq '.[].name')
if ($LASTEXITCODE -ne 0) { throw 'Failed to list labels (check gh auth status).' }

$tmp = [IO.Path]::GetTempFileName()
try {
    foreach ($l in $labels) {
        if ($existing -contains $l.name) { continue }

        $rename = $l.rename_from -and ($existing -contains $l.rename_from)
        if ($rename) {
            $body = @{ new_name = $l.name; color = $l.color; description = $l.description }
            $method = 'PATCH'
            $path = "repos/{owner}/{repo}/labels/$($l.rename_from)"
        } else {
            $body = @{ name = $l.name; color = $l.color; description = $l.description }
            $method = 'POST'
            $path = 'repos/{owner}/{repo}/labels'
        }

        [IO.File]::WriteAllText($tmp, ($body | ConvertTo-Json -Compress), $utf8)
        gh api $path --method $method --input $tmp --silent
        if ($LASTEXITCODE -ne 0) { throw "Failed: $($l.name)" }

        if ($rename) { "renamed: $($l.rename_from) -> $($l.name)" } else { "created: $($l.name)" }
    }
} finally {
    Remove-Item $tmp -Confirm:$false
}
'labels in sync'
