from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "a-share-industry-screening"
SKILL = ROOT / "skills" / SKILL_NAME

required = [
    ROOT / "README.md",
    SKILL / "SKILL.md",
    SKILL / "agents" / "openai.yaml",
    SKILL / "references" / "source-policy.md",
    SKILL / "references" / "screening-framework.md",
    SKILL / "references" / "output-schema.md",
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
if not re.search(rf"^name:\s*{re.escape(SKILL_NAME)}\s*$", frontmatter, re.MULTILINE):
    raise SystemExit("Unexpected or missing skill name")
if not re.search(r"^description:\s*\S", frontmatter, re.MULTILINE):
    raise SystemExit("Missing skill description")
if "[TODO:" in text:
    raise SystemExit("Unfinished TODO placeholder in SKILL.md")

for ref in re.findall(r"\]\((references/[^)]+)\)", text):
    if not (SKILL / ref).is_file():
        raise SystemExit(f"Broken reference: {ref}")

openai_yaml = (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")
if f"${SKILL_NAME}" not in openai_yaml:
    raise SystemExit("OpenAI default prompt does not name the skill")

canonical_path = f".agent-skills/{SKILL_NAME}/SKILL.md"
for adapter in [
    ROOT / "adapters" / "trae" / "project_rules.md",
    ROOT / "adapters" / "trae" / "custom-agent-prompt.md",
]:
    if canonical_path not in adapter.read_text(encoding="utf-8"):
        raise SystemExit(f"TRAE adapter does not reference the canonical skill: {adapter.name}")

for installer in [ROOT / "scripts" / "install.ps1", ROOT / "scripts" / "install.sh"]:
    installer_text = installer.read_text(encoding="utf-8")
    for agent in ["codex", "claude", "trae", "generic"]:
        if agent not in installer_text:
            raise SystemExit(f"Installer does not mention {agent}: {installer.name}")

print("Validation passed: canonical skill, references, adapters, and installers are present.")
