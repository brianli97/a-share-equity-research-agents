#!/usr/bin/env bash
set -euo pipefail

agent="${1:-}"
scope="${2:-user}"
project_path="${3:-$PWD}"
update="${4:-}"
if [[ "$project_path" == "--update" ]]; then
  project_path="$PWD"
  update="--update"
fi
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
skill_source="$repo_root/skills/a-share-filing-review"

usage() {
  echo "Usage: $0 <codex|claude|trae|generic> <user|project> [project-path] [--update]"
}

[[ -z "$update" || "$update" == "--update" ]] || { usage; exit 2; }

copy_skill() {
  local target="$1"
  local parent staged backup
  parent="$(dirname "$target")"
  mkdir -p "$parent"

  if [[ -e "$target" && "$update" != "--update" ]]; then
    echo "Target already exists: $target" >&2
    echo "Run again with --update to replace it from the repository." >&2
    exit 2
  fi

  staged="$(mktemp -d "$parent/.a-share-filing-review.stage.XXXXXX")"
  cp -R "$skill_source/." "$staged/"
  [[ -f "$staged/SKILL.md" ]] || { rm -rf "$staged"; echo "Staged skill is incomplete" >&2; exit 1; }

  if [[ -e "$target" ]]; then
    backup="$target.backup.$$"
    mv "$target" "$backup"
    if mv "$staged" "$target"; then
      rm -rf "$backup"
      echo "Updated: $target"
    else
      mv "$backup" "$target"
      rm -rf "$staged"
      echo "Update failed; restored: $target" >&2
      exit 1
    fi
  else
    mv "$staged" "$target"
    echo "Installed: $target"
  fi
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

