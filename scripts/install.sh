#!/usr/bin/env bash
set -euo pipefail

agent="${1:-}"
scope="${2:-user}"
project_path="${3:-$PWD}"
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
skill_source="$repo_root/skills/a-share-filing-review"

usage() {
  echo "Usage: $0 <codex|claude|trae|generic> <user|project> [project-path]"
}

copy_skill() {
  local target="$1"
  if [[ -e "$target" ]]; then
    echo "Target already exists: $target" >&2
    echo "Back it up or remove it, then retry." >&2
    exit 2
  fi
  mkdir -p "$(dirname "$target")"
  cp -R "$skill_source" "$target"
  echo "Installed: $target"
}

[[ -f "$skill_source/SKILL.md" ]] || { echo "Skill source not found: $skill_source" >&2; exit 1; }

case "$agent:$scope" in
  codex:user) copy_skill "$HOME/.codex/skills/a-share-filing-review" ;;
  codex:project) copy_skill "$(cd "$project_path" && pwd)/.agents/skills/a-share-filing-review" ;;
  claude:user) copy_skill "$HOME/.claude/skills/a-share-filing-review" ;;
  claude:project) copy_skill "$(cd "$project_path" && pwd)/.claude/skills/a-share-filing-review" ;;
  trae:project)
    project="$(cd "$project_path" && pwd)"
    copy_skill "$project/.agent-skills/a-share-filing-review"
    mkdir -p "$project/.trae-adapters"
    cp "$repo_root/adapters/trae/project_rules.md" "$project/.trae-adapters/a-share-filing-review-project-rules.md"
    cp "$repo_root/adapters/trae/custom-agent-prompt.md" "$project/.trae-adapters/a-share-filing-review-custom-agent.md"
    echo "Open TRAE > AI Management > Rules and import/paste the generated project rule."
    ;;
  generic:project)
    project="$(cd "$project_path" && pwd)"
    copy_skill "$project/skills/a-share-filing-review"
    cp "$repo_root/adapters/generic/AGENTS.md" "$project/AGENTS.a-share-filing-review.md"
    echo "Merge AGENTS.a-share-filing-review.md into the rule file used by your agent."
    ;;
  *) usage; exit 2 ;;
esac

