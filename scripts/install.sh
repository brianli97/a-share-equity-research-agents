#!/usr/bin/env bash
set -euo pipefail

agent="${1:-}"
scope="${2:-user}"
project_path="${3:-$PWD}"
skill="${4:-all}"
update="${5:-}"
if [[ "$project_path" == "--update" ]]; then project_path="$PWD"; update="--update"; fi
if [[ "$skill" == "--update" ]]; then skill="all"; update="--update"; fi

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
all_skills=(a-share-industry-screening a-share-filing-review a-share-peer-value-ranking)

usage() {
  echo "Usage: $0 <codex|claude|trae|generic> <user|project> [project-path] [all|skill-name] [--update]"
}

[[ -z "$update" || "$update" == "--update" ]] || { usage; exit 2; }
case "$skill" in
  all) skills=("${all_skills[@]}") ;;
  a-share-industry-screening|a-share-filing-review|a-share-peer-value-ranking) skills=("$skill") ;;
  *) usage; exit 2 ;;
esac

copy_skill() {
  local skill_name="$1" target="$2" source parent staged backup
  source="$repo_root/skills/$skill_name"
  [[ -f "$source/SKILL.md" ]] || { echo "Skill source not found: $source" >&2; exit 1; }
  parent="$(dirname "$target")"
  mkdir -p "$parent"
  if [[ -e "$target" && "$update" != "--update" ]]; then
    echo "Target already exists: $target" >&2
    echo "Run again with --update to replace it from the repository." >&2
    exit 2
  fi
  staged="$(mktemp -d "$parent/.$skill_name.stage.XXXXXX")"
  cp -R "$source/." "$staged/"
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

for skill_name in "${skills[@]}"; do
  case "$agent:$scope" in
    codex:user) copy_skill "$skill_name" "$HOME/.codex/skills/$skill_name" ;;
    codex:project) copy_skill "$skill_name" "$(cd "$project_path" && pwd)/.agents/skills/$skill_name" ;;
    claude:user) copy_skill "$skill_name" "$HOME/.claude/skills/$skill_name" ;;
    claude:project) copy_skill "$skill_name" "$(cd "$project_path" && pwd)/.claude/skills/$skill_name" ;;
    trae:project)
      project="$(cd "$project_path" && pwd)"
      copy_skill "$skill_name" "$project/.agent-skills/$skill_name"
      mkdir -p "$project/.trae-adapters"
      cp "$repo_root/adapters/$skill_name/trae/project_rules.md" "$project/.trae-adapters/$skill_name-project-rules.md"
      cp "$repo_root/adapters/$skill_name/trae/custom-agent-prompt.md" "$project/.trae-adapters/$skill_name-custom-agent.md"
      ;;
    generic:project)
      project="$(cd "$project_path" && pwd)"
      copy_skill "$skill_name" "$project/skills/$skill_name"
      cp "$repo_root/adapters/$skill_name/generic/AGENTS.md" "$project/AGENTS.$skill_name.md"
      ;;
    *) usage; exit 2 ;;
  esac
done

echo "Completed installation for: ${skills[*]}"
