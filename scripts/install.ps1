[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("codex", "claude", "trae", "generic")]
    [string]$Agent,

    [ValidateSet("user", "project")]
    [string]$Scope = "user",

    [string]$ProjectPath = (Get-Location).Path
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$skillSource = Join-Path $repoRoot "skills\a-share-filing-review"

if (-not (Test-Path -LiteralPath (Join-Path $skillSource "SKILL.md"))) {
    throw "Skill source not found: $skillSource"
}

function Copy-Skill([string]$Target) {
    if (Test-Path -LiteralPath $Target) {
        throw "Target already exists: $Target`nBack it up or remove it, then retry."
    }
    $parent = Split-Path -Parent $Target
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
    Copy-Item -LiteralPath $skillSource -Destination $Target -Recurse
    Write-Host "Installed: $Target"
}

switch ($Agent) {
    "codex" {
        $target = if ($Scope -eq "user") {
            Join-Path $env:USERPROFILE ".codex\skills\a-share-filing-review"
        } else {
            Join-Path ([IO.Path]::GetFullPath($ProjectPath)) ".agents\skills\a-share-filing-review"
        }
        Copy-Skill $target
    }
    "claude" {
        $target = if ($Scope -eq "user") {
            Join-Path $env:USERPROFILE ".claude\skills\a-share-filing-review"
        } else {
            Join-Path ([IO.Path]::GetFullPath($ProjectPath)) ".claude\skills\a-share-filing-review"
        }
        Copy-Skill $target
    }
    "trae" {
        if ($Scope -ne "project") { throw "TRAE adapter requires -Scope project." }
        $project = [IO.Path]::GetFullPath($ProjectPath)
        Copy-Skill (Join-Path $project ".agent-skills\a-share-filing-review")
        $adapterDir = Join-Path $project ".trae-adapters"
        New-Item -ItemType Directory -Path $adapterDir -Force | Out-Null
        Copy-Item -LiteralPath (Join-Path $repoRoot "adapters\trae\project_rules.md") -Destination (Join-Path $adapterDir "a-share-filing-review-project-rules.md")
        Copy-Item -LiteralPath (Join-Path $repoRoot "adapters\trae\custom-agent-prompt.md") -Destination (Join-Path $adapterDir "a-share-filing-review-custom-agent.md")
        Write-Host "Open TRAE > AI Management > Rules and import/paste the generated project rule."
    }
    "generic" {
        if ($Scope -ne "project") { throw "Generic adapter requires -Scope project." }
        $project = [IO.Path]::GetFullPath($ProjectPath)
        Copy-Skill (Join-Path $project "skills\a-share-filing-review")
        Copy-Item -LiteralPath (Join-Path $repoRoot "adapters\generic\AGENTS.md") -Destination (Join-Path $project "AGENTS.a-share-filing-review.md")
        Write-Host "Merge AGENTS.a-share-filing-review.md into the agent rule file used by your platform."
    }
}

