from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "a-share-filing-review"

required = [
    ROOT / "README.md",
    SKILL / "SKILL.md",
    SKILL / "agents" / "openai.yaml",
    SKILL / "references" / "source-policy.md",
    SKILL / "references" / "analysis-framework.md",
    SKILL / "references" / "reader-guide.md",
    SKILL / "references" / "output-convention.md",
    ROOT / "adapters" / "trae" / "project_rules.md",
    ROOT / "adapters" / "trae" / "custom-agent-prompt.md",
    ROOT / "adapters" / "generic" / "AGENTS.md",
    ROOT / "scripts" / "install.ps1",
    ROOT / "scripts" / "install.sh",
]

missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
if missing:
    raise SystemExit("Missing files:\n- " + "\n- ".join(missing))

text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
if not match:
    raise SystemExit("SKILL.md has invalid YAML frontmatter markers")

frontmatter = match.group(1)
if not re.search(r"^name:\s*a-share-filing-review\s*$", frontmatter, re.MULTILINE):
    raise SystemExit("Unexpected or missing skill name")
if not re.search(r"^description:\s*\S", frontmatter, re.MULTILINE):
    raise SystemExit("Missing skill description")
if "[TODO:" in text:
    raise SystemExit("Unfinished TODO placeholder in SKILL.md")

for ref in re.findall(r"\]\((references/[^)]+)\)", text):
    if not (SKILL / ref).is_file():
        raise SystemExit(f"Broken reference: {ref}")

openai_yaml = (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")
if "$a-share-filing-review" not in openai_yaml:
    raise SystemExit("OpenAI default prompt does not name the skill")

for adapter in [
    ROOT / "adapters" / "trae" / "project_rules.md",
    ROOT / "adapters" / "trae" / "custom-agent-prompt.md",
]:
    if ".agent-skills/a-share-filing-review/SKILL.md" not in adapter.read_text(encoding="utf-8"):
        raise SystemExit(f"TRAE adapter does not reference the canonical skill: {adapter.name}")

print("Validation passed: canonical skill, references, adapters, and installers are present.")

