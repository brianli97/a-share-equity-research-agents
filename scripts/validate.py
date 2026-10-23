from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SKILLS = {
    "a-share-industry-screening": [
        "references/source-policy.md",
        "references/screening-framework.md",
        "references/output-schema.md",
    ],
    "a-share-filing-review": [
        "references/source-policy.md",
        "references/analysis-framework.md",
        "references/reader-guide.md",
        "references/output-convention.md",
    ],
    "a-share-peer-value-ranking": [
        "references/input-contract.md",
        "references/comparison-framework.md",
        "references/valuation-policy.md",
        "references/output-schema.md",
        "references/report-data-schema.md",
        "scripts/rank_peers.py",
        "scripts/build_comparison_report.py",
    ],
}

required = [ROOT / "README.md", ROOT / "scripts" / "install.ps1", ROOT / "scripts" / "install.sh"]
for name, resources in SKILLS.items():
    skill = ROOT / "skills" / name
    required.extend([skill / "SKILL.md", skill / "agents" / "openai.yaml"])
    required.extend(skill / resource for resource in resources)
    required.extend([
        ROOT / "adapters" / name / "trae" / "project_rules.md",
        ROOT / "adapters" / name / "trae" / "custom-agent-prompt.md",
        ROOT / "adapters" / name / "generic" / "AGENTS.md",
    ])

missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
if missing:
    raise SystemExit("Missing files:\n- " + "\n- ".join(missing))

for name in SKILLS:
    skill = ROOT / "skills" / name
    text = (skill / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        raise SystemExit(f"{name}/SKILL.md has invalid YAML frontmatter markers")
    frontmatter = match.group(1)
    if not re.search(rf"^name:\s*{re.escape(name)}\s*$", frontmatter, re.MULTILINE):
        raise SystemExit(f"Unexpected or missing skill name: {name}")
    if not re.search(r"^description:\s*\S", frontmatter, re.MULTILINE):
        raise SystemExit(f"Missing skill description: {name}")
    if "[TODO:" in text:
        raise SystemExit(f"Unfinished TODO placeholder: {name}")
    for ref in re.findall(r"\]\((references/[^)]+)\)", text):
        if not (skill / ref).is_file():
            raise SystemExit(f"Broken reference in {name}: {ref}")
    openai_yaml = (skill / "agents" / "openai.yaml").read_text(encoding="utf-8")
    if f"${name}" not in openai_yaml:
        raise SystemExit(f"OpenAI default prompt does not name ${name}")
    for adapter_name in ["project_rules.md", "custom-agent-prompt.md"]:
        adapter = ROOT / "adapters" / name / "trae" / adapter_name
        if f".agent-skills/{name}/SKILL.md" not in adapter.read_text(encoding="utf-8"):
            raise SystemExit(f"TRAE adapter does not reference the canonical skill: {adapter}")

print(f"Validation passed: {len(SKILLS)} canonical skills, references, adapters, and installers are present.")
