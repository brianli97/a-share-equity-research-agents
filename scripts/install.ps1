[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("codex", "claude", "trae", "generic")]
    [string]$Agent,
    [ValidateSet("user", "project")]
    [string]$Scope = "user",
    [string]$ProjectPath = (Get-Location).Path,
    [switch]$Update
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$skillName = "a-share-peer-value-ranking"
$skillSource = Join-Path $repoRoot "skills\$skillName"

if (-not (Test-Path -LiteralPath (Join-Path $skillSource "SKILL.md"))) { throw "Skill source not found: $skillSource" }

function Copy-Skill([string]$Target) {
    $parent = Split-Path -Parent $Target
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
    $staged = "$Target.stage-$PID"
    $backup = "$Target.backup-$PID"
    if ((Test-Path -LiteralPath $staged) -or (Test-Path -LiteralPath $backup)) { throw "Temporary update path already exists for: $Target" }
    if ((Test-Path -LiteralPath $Target) -and -not $Update) { throw "Target already exists: $Target`nRun again with -Update." }
    Copy-Item -LiteralPath $skillSource -Destination $staged -Recurse
    if (-not (Test-Path -LiteralPath (Join-Path $staged "SKILL.md"))) { Remove-Item -LiteralPath $staged -Recurse -Force; throw "Staged skill is incomplete" }
    if (Test-Path -LiteralPath $Target) {
        Move-Item -LiteralPath $Target -Destination $backup
        try {
            Move-Item -LiteralPath $staged -Destination $Target
            Remove-Item -LiteralPath $backup -Recurse -Force
            Write-Host "Updated: $Target"
        } catch {
            if (-not (Test-Path -LiteralPath $Target) -and (Test-Path -LiteralPath $backup)) { Move-Item -LiteralPath $backup -Destination $Target }
            if (Test-Path -LiteralPath $staged) { Remove-Item -LiteralPath $staged -Recurse -Force }
            throw
        }
    } else { Move-Item -LiteralPath $staged -Destination $Target; Write-Host "Installed: $Target" }
}

switch ($Agent) {
    "codex" {
        $target = if ($Scope -eq "user") { Join-Path $env:USERPROFILE ".codex\skills\$skillName" } else { Join-Path ([IO.Path]::GetFullPath($ProjectPath)) ".agents\skills\$skillName" }
        Copy-Skill $target
    }
    "claude" {
        $target = if ($Scope -eq "user") { Join-Path $env:USERPROFILE ".claude\skills\$skillName" } else { Join-Path ([IO.Path]::GetFullPath($ProjectPath)) ".claude\skills\$skillName" }
        Copy-Skill $target
    }
    "trae" {
        if ($Scope -ne "project") { throw "TRAE adapter requires -Scope project." }
        $project = [IO.Path]::GetFullPath($ProjectPath)
        Copy-Skill (Join-Path $project ".agent-skills\$skillName")
        $adapterDir = Join-Path $project ".trae-adapters"
        New-Item -ItemType Directory -Path $adapterDir -Force | Out-Null
        Copy-Item -LiteralPath (Join-Path $repoRoot "adapters\trae\project_rules.md") -Destination (Join-Path $adapterDir "$skillName-project-rules.md") -Force
        Copy-Item -LiteralPath (Join-Path $repoRoot "adapters\trae\custom-agent-prompt.md") -Destination (Join-Path $adapterDir "$skillName-custom-agent.md") -Force
        Write-Host "Open TRAE > AI Management > Rules and import/paste the generated project rule."
    }
    "generic" {
        if ($Scope -ne "project") { throw "Generic adapter requires -Scope project." }
        $project = [IO.Path]::GetFullPath($ProjectPath)
        Copy-Skill (Join-Path $project "skills\$skillName")
        Copy-Item -LiteralPath (Join-Path $repoRoot "adapters\generic\AGENTS.md") -Destination (Join-Path $project "AGENTS.$skillName.md") -Force
        Write-Host "Merge AGENTS.$skillName.md into the agent rule file used by your platform."
    }
}

