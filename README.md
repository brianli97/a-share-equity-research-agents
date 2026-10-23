# A股同行价值比较与排序 Skill

把同一行业多家 A 股公司的筛选结果和财报深研结果归一为可比数据，分别评价业务质量、成长、盈利、现金流、资产负债、资本配置、治理与估值，并输出带公司排列顺序、价值投资研究建议和条件约束的 PDF 报告。

本仓库只维护一份核心 Skill。Codex 和 Claude Code 直接安装；TRAE 和其他仓库型 Agent 使用薄适配文件引用同一份规范。

## 与前序 Skill 的关系

```text
a-share-industry-screening
  └─ screening/universe.json        决定研究谁
             ↓
a-share-filing-review
  └─ extracted/report_data.json     逐家公司建立证据
             ↓
a-share-peer-value-ranking
  ├─ comparison/peer_data.json      统一可比口径
  ├─ comparison/ranking_data.json   多情景确定性排名
  ├─ comparison/comparison_report.md
  └─ report/<行业>_同行价值比较_<日期>.pdf
```

筛选阶段的分数不会直接继承到价值排名；单公司报告的页面结构也不会被当作财务数据。新 Skill 会先建立独立的 `peer_data.json`。

## 仓库结构

```text
a-share-peer-value-ranking/
├─ skills/a-share-peer-value-ranking/
│  ├─ SKILL.md
│  ├─ agents/openai.yaml
│  ├─ references/
│  │  ├─ input-contract.md
│  │  ├─ comparison-framework.md
│  │  ├─ valuation-policy.md
│  │  ├─ output-schema.md
│  │  └─ report-data-schema.md
│  └─ scripts/
│     ├─ rank_peers.py
│     └─ build_comparison_report.py
├─ adapters/
│  ├─ trae/project_rules.md
│  ├─ trae/custom-agent-prompt.md
│  └─ generic/AGENTS.md
└─ scripts/
   ├─ install.ps1
   ├─ install.sh
   └─ validate.py
```

## 安装与更新

### Windows PowerShell

```powershell
# Codex
.\scripts\install.ps1 -Agent codex -Scope user
.\scripts\install.ps1 -Agent codex -Scope user -Update

# Claude Code
.\scripts\install.ps1 -Agent claude -Scope user
.\scripts\install.ps1 -Agent claude -Scope user -Update

# 项目级安装
.\scripts\install.ps1 -Agent codex -Scope project -ProjectPath D:\your-project
.\scripts\install.ps1 -Agent claude -Scope project -ProjectPath D:\your-project
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

安装器不联网；目标已存在时默认停止，只有显式 `-Update` 或 `--update` 才替换。更新采用暂存、切换和失败回滚。

## 各平台如何使用

### Codex

用户级安装目录：

```text
~/.codex/skills/a-share-peer-value-ranking/
```

项目级安装目录：

```text
<project>/.agents/skills/a-share-peer-value-ranking/
```

新建任务或刷新 Skill 列表后调用：

```text
使用 $a-share-peer-value-ranking，读取人形机器人行业的筛选结果和公司财报报告，按价值投资研究优先级排序并生成PDF。
```

显式写出 `$a-share-peer-value-ranking` 最确定；当任务明显属于同行财报横向比较时，也允许自动触发。

### Claude Code

用户级目录：

```text
~/.claude/skills/a-share-peer-value-ranking/
```

项目级目录：

```text
<project>/.claude/skills/a-share-peer-value-ranking/
```

调用示例：

```text
/a-share-peer-value-ranking 比较三花智控、拓普集团、绿的谐波和汇川技术，按价值投资研究优先级排序并生成PDF
```

也可以用自然语言要求 Claude 读取该 Skill 后执行。

### TRAE

TRAE 使用项目 Rules、自定义 Agent 和项目文件作为适配入口。项目级安装会生成：

```text
<project>/.agent-skills/a-share-peer-value-ranking/
<project>/.trae-adapters/a-share-peer-value-ranking-project-rules.md
<project>/.trae-adapters/a-share-peer-value-ranking-custom-agent.md
```

安装后：

1. 打开 **AI Management → Rules**。
2. 新建项目规则并粘贴 `a-share-peer-value-ranking-project-rules.md`。
3. 如需独立 Agent，在自定义 Agent 提示词中粘贴另一个适配文件。
4. 确保 Agent 能读取上游 JSON、公司报告、网页和本地文件，并能运行 Python。
5. 仓库更新后，使用相同安装命令并增加 `-Update` 或 `--update`。

### 其他 Agent

支持 Agent Skills 结构的平台，可把 `skills/a-share-peer-value-ranking` 放入其技能目录。

只支持仓库规则的平台运行 `generic` 安装模式。脚本会生成：

```text
<project>/skills/a-share-peer-value-ranking/
<project>/AGENTS.a-share-peer-value-ranking.md
```

将生成的 AGENTS 文件合并到平台实际使用的 `AGENTS.md`、Rules 或等价规则文件。

## Skill 使用说明

### 完整 Workflow

推荐按以下顺序使用：

1. `$a-share-industry-screening` 生成行业候选池 `screening/universe.json`。
2. `$a-share-filing-review` 对候选公司逐家生成财报分析和 `extracted/report_data.json`。
3. `$a-share-peer-value-ranking` 统一口径、补齐同一价格日期、生成价值排序和 PDF。

标准请求：

```text
使用 $a-share-peer-value-ranking，读取人形机器人Top 20筛选结果和已完成的公司财报报告，按质量优先、成长优先和估值优先三种情景进行比较。缺失统一价格时停用估值排名。
```

指定公司请求：

```text
横向比较三花智控、拓普集团、绿的谐波、汇川技术和宇树科技，按价值投资研究优先级排序，说明哪些公司满足条件后值得考虑、哪些需要等待价格或经营证据，并生成PDF。
```

推荐在请求中明确：

- 公司名单或 `universe.json` 路径。
- 各公司报告所在目录。
- 统一研究截止日和价格日期。
- 是否采用质量、成长或估值偏好。
- 输出目录；未指定时使用当前工作目录的 `output/a-share-peer-value-ranking/`。

### 默认输出

```text
<当前工作目录>/output/a-share-peer-value-ranking/
└─ <行业或主题>_<YYYYMMDD>/
   ├─ comparison/
   │  ├─ peer_data.json
   │  ├─ ranking_data.json
   │  ├─ report_data.json
   │  └─ comparison_report.md
   ├─ sources/
   │  └─ source_manifest.json
   └─ report/
      └─ <行业>_同行价值比较_<YYYYMMDD>.pdf
```

PDF 是默认最终成品；JSON 和 Markdown 是复核底稿，不应删除。

### 结果怎样解读

- `quality_first`：偏重护城河、资本回报、现金流和治理。
- `growth_first`：偏重新业务兑现、增长质量和再投资空间。
- `valuation_first`：只有全部公司具备同一价格日期和可比盈利口径时启用。
- `coverage_ratio`：实际可用指标权重覆盖率；低于70%不生成精确名次。
- `confidence`：覆盖率乘以证据质量，不等于投资成功概率。

最终排序是研究优先级。只有估值、安全边际和经营条件同时满足时，报告才可以使用“满足条件后可考虑”；否则使用“等待价格”“成长验证期”“价值观察”或“暂不优先”。

## 确定性排名脚本

完成 `peer_data.json` 后运行：

```powershell
python .\skills\a-share-peer-value-ranking\scripts\rank_peers.py <路径>\peer_data.json
```

排名脚本只处理已经审核的0–100维度分、缺失值、覆盖率、证据质量和情景权重。PDF渲染器只处理 `report_data.json` 中的页面内容。两者都不会联网或猜测财务数据。

## 校验

```powershell
python .\scripts\validate.py
```

或：

```bash
python3 ./scripts/validate.py
```

## 运行要求

执行该 Skill 的 Agent 至少需要：

- 读取上游 JSON、Markdown 和 PDF 报告的能力；
- 访问正式公告或其他可复核来源的能力；
- 取得同一交易日行情数据的能力，若要判断估值与安全边际；
- Python 3；生成 PDF 时需要 `reportlab`，视觉检查需要 Poppler 或等价渲染工具；
- 可写的输出目录。

缺少 PDF 依赖时先交付完整 Markdown 和 JSON，并明确说明未完成 PDF；不得生成空文件或声称已经检查页面。

## 安全边界

- 不把行业筛选阶段的分数直接当成价值排名。
- 不用不同交易日价格比较估值。
- 不把缺失数据记零，也不把低 PE 自动解释为低估。
- 不输出收益承诺、无条件买入指令或缺少假设的目标价。
- 数据和来源不足时降低置信度，不能编造排名依据。

