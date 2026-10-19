# A股招股书与财报解读 Skill

把一个 A 股公司名称交给 Agent，由它下载官方招股说明书和最近一年定期报告，按统一框架梳理业务、财务、治理、风险，并生成可阅读、可复核的中文 PDF。

本仓库只维护一份核心 Skill，Codex 和 Claude Code 直接安装它；TRAE 和不支持 Agent Skills 标准的平台通过薄适配文件引用同一份规范，避免多份副本逐渐不一致。

## 能做什么

- 核对公司全称、股票代码、交易所、上市板块和曾用名。
- 优先从交易所、巨潮资讯和证监会下载官方文件。
- 默认读取最近完整年度报告，以及年报后最新的季度或半年度报告。
- 梳理商业模式、收入、利润、现金流、资产负债、客户供应商、研发、治理、募投和风险。
- 给出适合普通投资者的阅读顺序、PDF 搜索词、财务红旗和一页结论卡。
- 用“管理层计划→实际投入→财务变化→经营成果→下期验证”检查战略兑现度。
- 区分公司披露、计算结果和分析判断，给专业术语作通俗注释。
- 保存原始披露文件并生成约 10–18 页的中文 PDF。

## 仓库结构

```text
a-share-filing-review-agents/
├─ skills/a-share-filing-review/       # 唯一事实源，符合 Agent Skills 结构
│  ├─ SKILL.md
│  ├─ agents/openai.yaml               # Codex 展示与自动触发配置
│  └─ references/
│     ├─ analysis-framework.md
│     ├─ reader-guide.md
│     ├─ output-convention.md
│     └─ source-policy.md
├─ adapters/
│  ├─ trae/project_rules.md             # 在 TRAE 的项目规则中使用
│  ├─ trae/custom-agent-prompt.md        # 可选的 TRAE 自定义 Agent 提示词
│  └─ generic/AGENTS.md                  # 其他仓库型 Agent 的入口示例
└─ scripts/
   ├─ install.ps1                       # Windows 安装
   ├─ install.sh                        # macOS/Linux/WSL 安装
   └─ validate.py                       # 无第三方依赖的结构校验
```

## 快速安装

### Windows PowerShell

在仓库根目录运行：

```powershell
# Codex：为当前 Windows 用户安装
.\scripts\install.ps1 -Agent codex -Scope user

# 仓库更新后，同步覆盖已安装的 Codex Skill
.\scripts\install.ps1 -Agent codex -Scope user -Update

# Claude Code：为当前用户安装
.\scripts\install.ps1 -Agent claude -Scope user

# 安装到某个项目，而不是用户目录
.\scripts\install.ps1 -Agent codex -Scope project -ProjectPath D:\your-project
.\scripts\install.ps1 -Agent claude -Scope project -ProjectPath D:\your-project

# 为 TRAE 准备项目内资料与规则文件
.\scripts\install.ps1 -Agent trae -Scope project -ProjectPath D:\your-project
```

### macOS、Linux 或 WSL

```bash
./scripts/install.sh codex user
./scripts/install.sh codex user --update
./scripts/install.sh claude user
./scripts/install.sh codex project /path/to/project
./scripts/install.sh claude project /path/to/project
./scripts/install.sh trae project /path/to/project
```

安装脚本只复制文件且不联网。默认不会修改已有同名目录；仓库更新后可显式使用 `-Update`（PowerShell）或 `--update`（Shell）同步。更新时会先暂存完整新副本，再替换目标；替换失败会恢复旧副本。安装目录是仓库的副本，不会随 Git 更新自动变化。

## 各平台如何使用

### Codex

Codex 用户级目录：

```text
~/.codex/skills/a-share-filing-review/
```

仓库级目录：

```text
<project>/.agents/skills/a-share-filing-review/
```

调用示例：

```text
使用 $a-share-filing-review 分析万向钱潮，下载招股说明书和近一年财报，并生成详细解读 PDF。
```

也可以直接说：

```text
分析贵州茅台最近一年财报，重点关注现金流、渠道库存和关联交易，生成 PDF。
```

Codex 根据 `SKILL.md` 的名称和描述自动发现 Skill；显式写 `$a-share-filing-review` 更确定。OpenAI 官方说明：[Agent Skills](https://developers.openai.com/api/docs/guides/tools-skills)。

### Claude Code

Claude Code 与本仓库使用相同的 `SKILL.md` 格式。用户级目录：

```text
~/.claude/skills/a-share-filing-review/
```

项目级目录：

```text
<project>/.claude/skills/a-share-filing-review/
```

调用示例：

```text
/a-share-filing-review 万向钱潮，重点分析关联资金、债务和现金流
```

或使用自然语言要求 Claude 使用该 Skill。Claude Code 的个人级、项目级和插件级目录说明见：[Claude Code Skills](https://code.claude.com/docs/en/skills)。

### TRAE

TRAE 官方公开方案以 Rules、自定义 Agent 和文档上下文为主，因此本仓库不假设一个未经官方确认的“全局 Skill 目录”。安装脚本会在目标项目生成：

```text
<project>/.agent-skills/a-share-filing-review/
<project>/.trae-adapters/a-share-filing-review-project-rules.md
<project>/.trae-adapters/a-share-filing-review-custom-agent.md
```

然后在 TRAE 中：

1. 打开右侧的 **AI Management**。
2. 进入 **Rules**，新建项目规则。
3. 粘贴 `.trae-adapters/a-share-filing-review-project-rules.md` 的内容。
4. 如需独立 Agent，在自定义 Agent 提示词中粘贴另一个适配文件。
5. 发起任务时输入公司名，并确保 Agent 可以访问项目文件、网页和终端。

TRAE 官方规则优先级为：用户输入 > 自定义 Agent 提示词 > `user_rules.md` > `project_rules.md`。参考：[TRAE Rules 官方实践](https://www.trae.ai/blog/trae_tutorial_0825)。

### 其他 Agent

如果平台支持开放的 Agent Skills 结构，直接把 `skills/a-share-filing-review` 放进其技能目录。

如果平台只支持仓库规则：

1. 把本仓库的 `skills/` 放入目标项目。
2. 将 `adapters/generic/AGENTS.md` 合并到目标项目的 `AGENTS.md` 或等价规则文件。
3. 用自然语言要求 Agent 读取该 Skill 后执行。

## 运行要求

这是工作流 Skill，不包含浏览器、OCR 或 PDF 引擎。执行它的 Agent 至少需要：

- 访问公开网页并下载文件的能力；
- 读取大型 PDF 的能力；
- 生成 PDF 或将 HTML/Markdown 转成 PDF 的能力；
- 可写的输出目录。

缺少 PDF 工具时，Skill 会先生成结构完整的 Markdown 或 HTML，并明确说明未完成 PDF 渲染，不应假装已生成。

## 默认输出位置

```text
<当前工作目录>/output/a-share-filing-review/
└─ <证券代码>_<公司简称>_<YYYYMMDD>/
   ├─ source/       # 官方原始文件
   ├─ extracted/    # 可复核的提取数据或中间表
   └─ report/       # 最终 PDF
```

最终回复应给出全部成品的可点击路径，并说明报告期、资料缺失和未审计数据。

## 校验

```powershell
python .\scripts\validate.py
```

或：

```bash
python3 ./scripts/validate.py
```

## 安全边界

- 不使用财经网站摘要代替官方财报原文。
- 不绕过网站登录、验证码、访问控制或付费墙。
- 不输出买卖建议或目标价，除非用户明确要求并能取得可靠市场数据。
- 下载失败时列明缺失材料，不伪造链接、数字、页码或审计结论。

