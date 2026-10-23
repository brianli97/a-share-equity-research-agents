from pathlib import Path
import ast
import re

ROOT = Path(__file__).resolve().parents[1]
NAME = "a-share-peer-value-ranking"
SKILL = ROOT / "skills" / NAME

required = [
    ROOT / "README.md",
    SKILL / "SKILL.md",
    SKILL / "agents" / "openai.yaml",
    SKILL / "references" / "input-contract.md",
    SKILL / "references" / "comparison-framework.md",
    SKILL / "references" / "valuation-policy.md",
    SKILL / "references" / "output-schema.md",
    SKILL / "references" / "report-data-schema.md",
    SKILL / "scripts" / "rank_peers.py",
    SKILL / "scripts" / "build_comparison_report.py",
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
front = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
if not front or not re.search(rf"^name:\s*{NAME}\s*$", front.group(1), re.MULTILINE):
    raise SystemExit("Invalid SKILL.md frontmatter")
if not re.search(r"^description:\s*\S", front.group(1), re.MULTILINE):
    raise SystemExit("Missing description")
if "[TODO:" in text:
    raise SystemExit("Unfinished TODO")
for ref in re.findall(r"\]\((references/[^)]+)\)", text):
    if not (SKILL / ref).is_file():
        raise SystemExit(f"Broken reference: {ref}")
if f"${NAME}" not in (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8"):
    raise SystemExit("Default prompt does not name the skill")

ast.parse((SKILL / "scripts" / "rank_peers.py").read_text(encoding="utf-8"))
ast.parse((SKILL / "scripts" / "build_comparison_report.py").read_text(encoding="utf-8"))
readme = (ROOT / "README.md").read_text(encoding="utf-8")
for platform in ["Codex", "Claude Code", "TRAE", "其他 Agent"]:
    if platform not in readme:
        raise SystemExit(f"README missing platform instructions: {platform}")
for installer in [ROOT / "scripts" / "install.ps1", ROOT / "scripts" / "install.sh"]:
    installer_text = installer.read_text(encoding="utf-8")
    for agent in ["codex", "claude", "trae", "generic"]:
        if agent not in installer_text:
            raise SystemExit(f"Installer does not mention {agent}: {installer.name}")
canonical = f".agent-skills/{NAME}/SKILL.md"
for adapter in [ROOT / "adapters" / "trae" / "project_rules.md", ROOT / "adapters" / "trae" / "custom-agent-prompt.md"]:
    if canonical not in adapter.read_text(encoding="utf-8"):
        raise SystemExit(f"TRAE adapter does not reference canonical skill: {adapter.name}")
print("Validation passed: skill, references, ranker, adapters, and installers are present.")
