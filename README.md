# A股行业公司筛选 Skill

输入一个 A 股行业、领域、概念或产业链环节，建立可复核的候选池，分别识别行业龙头、市场热度与基本面质量，并输出默认 Top 20 名单及后续公司深研所需的结构化数据。

本仓库只维护一份核心 Skill。Codex 和 Claude Code 直接安装该 Skill；TRAE 与不支持 Agent Skills 标准的平台使用薄适配文件引用同一份规范，避免多份副本逐渐不一致。

## 仓库结构

```text
a-share-industry-screening/
├─ skills/a-share-industry-screening/  # 唯一事实源
│  ├─ SKILL.md
│  ├─ agents/openai.yaml
│  └─ references/
│     ├─ source-policy.md
│     ├─ screening-framework.md
│     └─ output-schema.md
├─ adapters/
│  ├─ trae/project_rules.md
│  ├─ trae/custom-agent-prompt.md
│  └─ generic/AGENTS.md
└─ scripts/
   ├─ install.ps1
   ├─ install.sh
   └─ validate.py
```

## 快速安装与更新

### Windows PowerShell

在仓库根目录运行：

```powershell
# Codex 用户级安装与更新
.\scripts\install.ps1 -Agent codex -Scope user
.\scripts\install.ps1 -Agent codex -Scope user -Update

# Claude Code 用户级安装与更新
.\scripts\install.ps1 -Agent claude -Scope user
.\scripts\install.ps1 -Agent claude -Scope user -Update

# Codex / Claude Code 项目级安装
.\scripts\install.ps1 -Agent codex -Scope project -ProjectPath D:\your-project
.\scripts\install.ps1 -Agent claude -Scope project -ProjectPath D:\your-project

# TRAE 或其他仓库型 Agent
.\scripts\install.ps1 -Agent trae -Scope project -ProjectPath D:\your-project
.\scripts\install.ps1 -Agent generic -Scope project -ProjectPath D:\your-project
```

### macOS、Linux 或 WSL

```bash
./scripts/install.sh codex user
./scripts/install.sh codex user --update
./scripts/install.sh claude user
./scripts/install.sh claude user --update
./scripts/install.sh codex project /path/to/project
./scripts/install.sh claude project /path/to/project
./scripts/install.sh trae project /path/to/project
./scripts/install.sh generic project /path/to/project
```

安装脚本只复制本地文件，不联网。目标已存在时默认停止；只有显式提供 `-Update` 或 `--update` 才会更新。更新会先生成完整暂存副本，再替换目标；失败时恢复旧副本。

## 平台接口

### Codex

用户级目录：

```text
~/.codex/skills/a-share-industry-screening/
```

项目级目录：

```text
<project>/.agents/skills/a-share-industry-screening/
```

调用示例：

```text
使用 $a-share-industry-screening 筛选人形机器人产业链前20家A股公司，分别列出龙头榜和热度榜。
```

### Claude Code

用户级目录：

```text
~/.claude/skills/a-share-industry-screening/
```

项目级目录：

```text
<project>/.claude/skills/a-share-industry-screening/
```

调用示例：

```text
/a-share-industry-screening 储能逆变器，筛选前20家A股公司并说明业务纯度
```

### TRAE

TRAE 使用项目 Rules、自定义 Agent 和项目文件作为适配入口。脚本会生成：

```text
<project>/.agent-skills/a-share-industry-screening/
<project>/.trae-adapters/a-share-industry-screening-project-rules.md
<project>/.trae-adapters/a-share-industry-screening-custom-agent.md
```

在 TRAE 的 **AI Management → Rules** 中粘贴项目规则；如需独立 Agent，再粘贴自定义 Agent 提示词。更新仓库后，使用同一命令并增加 `-Update` 或 `--update`。

### 其他 Agent

支持 Agent Skills 的平台可直接安装 `skills/a-share-industry-screening`。只支持仓库规则的平台使用 `generic` 安装模式，然后把生成的 `AGENTS.a-share-industry-screening.md` 合并到其规则文件。

## 校验

校验器无第三方依赖：

```powershell
python .\scripts\validate.py
```

或：

```bash
python3 ./scripts/validate.py
```

## 运行要求

执行该 Skill 的 Agent 至少需要访问公开网页、读取公告或财报、获取必要行情数据并写入输出目录的能力。缺少行情或热度数据时仍可完成基本面候选池，但必须明确缺失维度及其对排名的影响。

