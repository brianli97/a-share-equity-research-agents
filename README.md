# A股权益研究 Agent Skills

面向 A 股研究的三个独立 Skill，由同一个仓库统一维护、安装和校验。

```text
a-share-industry-screening
  └─ 建立行业候选池和 Top 20 名单
             ↓ screening/universe.json
a-share-filing-review
  └─ 逐家公司解读招股书和定期报告
             ↓ extracted/report_data.json
a-share-peer-value-ranking
  └─ 统一可比口径并生成同行价值排序
```

三个 Skill 可以串联使用，也可以单独调用。仓库合并不改变各自的触发条件、`SKILL.md` 或输出契约。

## 仓库结构

```text
skills/
├─ a-share-industry-screening/
├─ a-share-filing-review/
└─ a-share-peer-value-ranking/
adapters/
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

默认一次安装全部三个 Skill：

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
使用 $a-share-industry-screening 筛选人形机器人产业链前20家A股公司。

使用 $a-share-filing-review 分析万向钱潮的招股书和最近一年财报，生成PDF。

使用 $a-share-peer-value-ranking 比较同行公司的质量、成长和估值，生成排序报告。
```

完整研究建议按“行业筛选 → 单公司深研 → 同行价值排序”的顺序执行。具体证据政策、输出结构和安全边界以各 Skill 的 `SKILL.md` 及其 references 为准。

## 校验

```powershell
python .\scripts\validate.py
```

校验器会检查全部三个 Skill 的 frontmatter、资源、引用、OpenAI 元数据和适配器路径。

## 输出与版本管理

生成资料默认位于 `output/`。正式财报 PDF、提取中间件和生成报告属于运行产物；除有意保留的研究成品外，不建议持续加入 Git。大量二进制文件应使用 Release、对象存储或 Git LFS，避免仓库不断膨胀。
