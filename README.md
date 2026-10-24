# A股权益研究 Agent Skills

面向 A 股研究的四个 Skill，由同一个仓库统一维护、安装和校验。三个专业 Skill 分别解决“研究谁”“这家公司怎么样”和“同行中谁更值得优先研究”，总控 Skill 负责把三者串成可恢复的完整工作流。

## 四个 Skill 怎么选

| Skill | 核心问题 | 典型输入 | 主要输出 | 能力边界 |
| --- | --- | --- | --- | --- |
| `a-share-industry-research-workflow` | 如何从一个行业请求完成筛选、深研和同行排序？ | 行业、主题或产业链；可选 Top-N、深研家数和截止日 | 统一任务目录、`workflow_manifest.json` 及三个阶段的全部产物 | 只负责编排，不替代三个专业 Skill 的研究判断 |
| `a-share-industry-screening` | 这个行业或主题应该先研究哪些公司？ | 行业、主题或产业链环节；筛选模式；Top N | `screening/universe.json`、候选池和筛选报告 | 不替代单家公司财报深研，不直接给出买卖建议 |
| `a-share-filing-review` | 这家公司的基本面、治理和主要风险怎么样？ | 一家 A 股公司的名称或代码 | 基于招股书和定期报告的溯源 PDF、`extracted/report_data.json` | 不负责多公司统一排名，不提供目标价或无条件买卖建议 |
| `a-share-peer-value-ranking` | 同行中哪些公司更值得优先研究？ | 通常至少 3 家公司的标准化研究数据；统一口径的估值信息 | 同行比较、情景排名、研究优先级和 PDF 报告 | 不从全市场建立候选池；排名不等于直接投资建议 |

`a-share-industry-research-workflow` 默认由一个 Agent 顺序执行，筛选 Top 20、深研前 5 家，并在至少 3 家深研成功后生成正式排名；运行状态写入 `workflow_manifest.json`，中断后可以继续。它不要求 Multica 或多个 Agent。`a-share-industry-screening` 支持龙头、热度、基本面和综合等筛选模式。`a-share-filing-review` 以公司官方披露文件为主要证据，生成单公司研究报告，并为同行比较提供结构化数据。`a-share-peer-value-ranking` 会统一报告期、指标定义和估值时点，从质量、成长、盈利与现金流、资产负债表、资本配置、治理及安全边际等维度形成多情景排序。

默认证券范围仅包括上交所主板、深交所主板和深交所创业板 A 股，排除科创板与北交所；用户可以在请求中显式覆盖。对“半导体”等宽主题，工作流先拆分产业链环节：跨环节结果称为基本面研究优先级，严格同行价值排序只在同一或高度可比环节内生成。

PDF 报告默认采用面向普通投资者的可读设计：先讲公司如何赚钱和核心结论，再展示财务证据、图表、风险、情景与跟踪指标；专业术语附白话解释。渲染器支持指标卡、信息卡、要点列表和横向条形图，并要求生成后逐页渲染检查。

宽行业请求还会先生成产业链导览 Markdown 与美化 PDF，解释各环节做什么、哪些公司符合板块限制、哪些样本可以真正进行同行比较，再进入 Top-N 筛选。

## 推荐工作流

```text
行业、主题或产业链环节
  ↓ a-share-industry-research-workflow（总控）
  ├─ a-share-industry-screening
候选公司池 / screening/universe.json
  ├─ a-share-filing-review（逐家公司）
单公司研究 PDF / extracted/report_data.json
  └─ a-share-peer-value-ranking
同行比较、价值排序和研究优先级报告
```

需要完整流程时使用总控 Skill；三个专业 Skill 也可以独立调用：已有明确公司时可直接使用 `a-share-filing-review`；已有同行名单及足够的标准化证据时可直接使用 `a-share-peer-value-ranking`；只需要候选池时使用 `a-share-industry-screening`。

## 仓库结构

```text
skills/
├─ a-share-industry-research-workflow/
├─ a-share-industry-screening/
├─ a-share-filing-review/
└─ a-share-peer-value-ranking/
adapters/
├─ a-share-industry-research-workflow/
├─ a-share-industry-screening/
├─ a-share-filing-review/
└─ a-share-peer-value-ranking/
scripts/
├─ install.ps1
├─ install.sh
└─ validate.py
```

每个 `skills/<name>/` 都是可独立安装的 Agent Skill，并包含自己的 `SKILL.md`、UI 元数据、引用资料及必要脚本。`adapters/` 为 TRAE 和通用仓库型 Agent 提供对应的薄适配层。

## 安装

### Windows PowerShell

默认一次安装全部四个 Skill：

```powershell
.\scripts\install.ps1 -Agent codex -Scope user
.\scripts\install.ps1 -Agent codex -Scope user -Update
```

只安装一个 Skill：

```powershell
.\scripts\install.ps1 -Agent codex -Scope user -Skill a-share-filing-review
```

安装到项目或其他 Agent：

```powershell
.\scripts\install.ps1 -Agent codex -Scope project -ProjectPath D:\your-project
.\scripts\install.ps1 -Agent claude -Scope user
.\scripts\install.ps1 -Agent trae -Scope project -ProjectPath D:\your-project
.\scripts\install.ps1 -Agent generic -Scope project -ProjectPath D:\your-project
```

### macOS、Linux 或 WSL

```bash
./scripts/install.sh codex user
./scripts/install.sh codex user "$PWD" a-share-filing-review
./scripts/install.sh codex project /path/to/project all --update
./scripts/install.sh trae project /path/to/project
```

安装器只复制本地文件，不联网。目标已存在时默认停止；显式使用 `-Update` 或 `--update` 才会替换，并在失败时恢复旧副本。

## 调用

```text
使用 $a-share-industry-research-workflow 完整研究人形机器人产业链：综合筛选 Top 20，顺序深研前 5 家，并生成同行价值排序和统一任务目录。

使用 $a-share-industry-screening，按综合模式筛选人形机器人产业链前 20 家 A 股公司，输出候选池和筛选报告。

使用 $a-share-filing-review，基于官方招股书和最近一期年度报告分析万向钱潮，生成带来源的 PDF 和结构化研究数据。

使用 $a-share-peer-value-ranking，比较已完成单公司研究的同行公司，统一报告期和估值日期，从质量、成长和估值等维度生成多情景排序报告。
```

完整研究建议按“行业筛选 → 单公司深研 → 同行价值排序”的顺序执行。同行估值比较应尽量采用同一价格日期，最终排名表示研究优先级，不构成无条件买卖建议。具体证据政策、输出结构和安全边界以各 Skill 的 `SKILL.md` 及其 references 为准。

## 校验

```powershell
python .\scripts\validate.py
```

校验器会检查全部四个 Skill 的 frontmatter、资源、引用、OpenAI 元数据和适配器路径。

## 输出与版本管理

生成资料默认位于 `output/`。正式财报 PDF、提取中间件和生成报告属于运行产物；除有意保留的研究成品外，不建议持续加入 Git。大量二进制文件应使用 Release、对象存储或 Git LFS，避免仓库不断膨胀。
