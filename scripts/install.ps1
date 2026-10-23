[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("codex", "claude", "trae", "generic")]
    [string]$Agent,
    [ValidateSet("user", "project")]
    [string]$Scope = "user",
    [ValidateSet("all", "a-share-industry-screening", "a-share-filing-review", "a-share-peer-value-ranking")]
    [string]$Skill = "all",
    [string]$ProjectPath = (Get-Location).Path,
    [switch]$Update
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$skillNames = if ($Skill -eq "all") {
    @("a-share-industry-screening", "a-share-filing-review", "a-share-peer-value-ranking")
} else { @($Skill) }

function Copy-Skill([string]$SkillName, [string]$Target) {
    $skillSource = Join-Path $repoRoot "skills\$SkillName"
    if (-not (Test-Path -LiteralPath (Join-Path $skillSource "SKILL.md"))) {
        throw "Skill source not found: $skillSource"
    }
    New-Item -ItemType Directory -Path (Split-Path -Parent $Target) -Force | Out-Null
    $staged = "$Target.stage-$PID"
    $backup = "$Target.backup-$PID"
    if ((Test-Path -LiteralPath $staged) -or (Test-Path -LiteralPath $backup)) {
        throw "Temporary update path already exists for: $Target"
    }
    if ((Test-Path -LiteralPath $Target) -and -not $Update) {
        throw "Target already exists: $Target`nRun again with -Update to replace it from the repository."
    }
    Copy-Item -LiteralPath $skillSource -Destination $staged -Recurse
    if (-not (Test-Path -LiteralPath (Join-Path $staged "SKILL.md"))) {
        Remove-Item -LiteralPath $staged -Recurse -Force
        throw "Staged skill is incomplete: $staged"
    }
    if (Test-Path -LiteralPath $Target) {
        Move-Item -LiteralPath $Target -Destination $backup
        try {
            Move-Item -LiteralPath $staged -Destination $Target
            Remove-Item -LiteralPath $backup -Recurse -Force
            Write-Host "Updated: $Target"
        } catch {
            if (-not (Test-Path -LiteralPath $Target) -and (Test-Path -LiteralPath $backup)) {
                Move-Item -LiteralPath $backup -Destination $Target
            }
            if (Test-Path -LiteralPath $staged) {
                Remove-Item -LiteralPath $staged -Recurse -Force
            }
            throw
        }
    } else {
        Move-Item -LiteralPath $staged -Destination $Target
        Write-Host "Installed: $Target"
    }
}

foreach ($skillName in $skillNames) {
    switch ($Agent) {
        "codex" {
            $target = if ($Scope -eq "user") {
                Join-Path $env:USERPROFILE ".codex\skills\$skillName"
            } else {
                Join-Path ([IO.Path]::GetFullPath($ProjectPath)) ".agents\skills\$skillName"
            }
            Copy-Skill $skillName $target
        }
        "claude" {
            $target = if ($Scope -eq "user") {
                Join-Path $env:USERPROFILE ".claude\skills\$skillName"
            } else {
                Join-Path ([IO.Path]::GetFullPath($ProjectPath)) ".claude\skills\$skillName"
            }
            Copy-Skill $skillName $target
        }
        "trae" {
            if ($Scope -ne "project") { throw "TRAE adapter requires -Scope project." }
            $project = [IO.Path]::GetFullPath($ProjectPath)
            Copy-Skill $skillName (Join-Path $project ".agent-skills\$skillName")
            $adapterDir = Join-Path $project ".trae-adapters"
            New-Item -ItemType Directory -Path $adapterDir -Force | Out-Null
            $adapterSource = Join-Path $repoRoot "adapters\$skillName\trae"
            Copy-Item -LiteralPath (Join-Path $adapterSource "project_rules.md") -Destination (Join-Path $adapterDir "$skillName-project-rules.md") -Force
            Copy-Item -LiteralPath (Join-Path $adapterSource "custom-agent-prompt.md") -Destination (Join-Path $adapterDir "$skillName-custom-agent.md") -Force
        }
        "generic" {
            if ($Scope -ne "project") { throw "Generic adapter requires -Scope project." }
            $project = [IO.Path]::GetFullPath($ProjectPath)
            Copy-Skill $skillName (Join-Path $project "skills\$skillName")
            $adapterSource = Join-Path $repoRoot "adapters\$skillName\generic\AGENTS.md"
            Copy-Item -LiteralPath $adapterSource -Destination (Join-Path $project "AGENTS.$skillName.md") -Force
        }
    }
}
Write-Host "Completed installation for: $($skillNames -join ', ')"
