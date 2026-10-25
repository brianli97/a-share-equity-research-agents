---
name: a-share-industry-research-workflow
description: Orchestrate an end-to-end A-share industry research run by screening a Top-N universe, reviewing selected companies' official filings, and ranking comparable peers with resumable, validated outputs. Use when the user asks to research an A-share industry, sector, theme, or value chain through the complete 筛选—深研—同行比较 workflow. Do not use when only one stage or one company is requested.
---

# A股行业研究工作流

把一个行业、主题或产业链研究请求依次交给 `a-share-industry-screening`、`a-share-filing-review` 和 `a-share-peer-value-ranking`，在同一任务目录中保存阶段产物、运行状态和最终交付。默认由一个 Agent 顺序执行，不要求 Multica 或多个 Agent。

## 执行前读取

1. 读取 [references/workflow-contract.md](references/workflow-contract.md)，确定阶段门、默认参数和恢复规则。
2. 读取 [references/output-layout.md](references/output-layout.md)，创建统一目录和 `workflow_manifest.json`。
3. 进入每个阶段时，读取并遵循对应下游 Skill 的 `SKILL.md` 及其要求的参考资料；本 Skill 只负责编排，不复制或弱化下游的证据纪律。

## 默认参数

- 证券范围：仅上交所主板、深交所主板和深交所创业板 A 股；默认排除科创板与北交所。用户可显式覆盖，但必须写入清单。
- 行业筛选：综合模式，Top 20。
- 单公司深研：综合候选名单前 5 家。
- 同行排序：使用成功完成深研且可比的公司；至少 3 家才形成正式排名。
- 研究截止日：任务执行日；财务报告期和估值日期分别记录，不混用。
- 执行方式：单 Agent 顺序执行。除非用户明确要求并且当前环境支持，否则不创建子 Agent、不并行分派公司。
- 恢复策略：复用同一截止日下已经通过校验的产物；不静默覆盖已完成研究。

用户可以覆盖 Top-N、深研家数、筛选模式、截止日、是否包含估值、关注问题和输出位置。只有行业口径歧义或样本选择会实质改变结果时才询问。

## 工作流

1. 解析请求并固定参数。将证券范围和主题口径写入清单。宽主题先拆分产业链环节，并生成 `scope/industry_scope.json`、`scope/industry_scope_report.md`、`scope/report_data.json` 与美化 PDF；内容包括产业链地图、各环节白话解释、纳入/排除边界、合格候选数量、可比性和建议研究路径。范围报告复用 `a-share-peer-value-ranking/scripts/build_comparison_report.py` 的通用页面组件渲染，但不生成公司名次。完整产业链榜与同环节价值排名使用不同标签。创建 `<输出根目录>/<主题>_<YYYYMMDD>/` 和初始 `workflow_manifest.json`，将三个阶段设为 `pending`。
2. **行业筛选**：使用 `a-share-industry-screening` 生成 `screening/universe.json` 和 `screening/screening_report.md`。完成后检查主题、证券代码、公司全称、交易所、上市板块、排名、入选理由、证据等级、数据日期和 `deep_review_questions`；任一候选不属于清单允许板块时筛选不得标记为 `completed`。
3. **确定深研样本**：默认按综合榜顺序选择前 5 家。若综合榜不可用，依据已披露的替代规则选择并写入清单；不得临时凭印象换样本。为每家公司传递证券代码、公司全称、交易所、统一截止日、入选理由、业务暴露和待验证问题。
4. **逐家公司深研**：对样本中的每家公司使用 `a-share-filing-review`。每次开始前把公司状态改为 `in_progress`；完整报告默认覆盖最近 3 个完整年度和之后最新定期报告，包含图表化趋势、经营拆解、战略兑现、价值创造、AI 判断、风险与证伪条件。完成并校验 `extracted/report_data.json` 与最终报告后改为 `completed`。只有财务摘要或少于 12 页的简报不得冒充完整深研。失败时记录错误、数据缺口和可重试条件，然后继续下一家公司，不因单家公司失败丢失整个任务进度。
5. **阶段门**：统计成功且具备来源、报告期和核心指标的公司。达到 3 家后进入正式同行排名；少于 3 家时只允许并列比较，并在清单中把排名阶段标为 `skipped` 或 `partial`，说明原因。
6. **同行比较**：使用 `a-share-peer-value-ranking` 读取筛选范围及各公司 `report_data.json`。先按产业链环节和商业模式检查可比性：同环节或高度可比样本可生成同行价值排序；跨环节样本只能生成“跨产业链基本面研究优先级”，不得称为严格同行价值排序。统一公司身份、财务期间、指标定义和价格日期；只有统一价格日期可得时才启用估值与安全边际情景。
7. 生成并校验 `comparison/peer_data.json`、`comparison/ranking_data.json`、`comparison/report_data.json`、`comparison/comparison_report.md` 和最终 PDF。同行报告默认读取各公司 2–3 年趋势和经营结论；在同日行情可得时加入估值与安全边际情景，并汇总最新国家政策、行业景气与“行业是否具有投资价值”的条件性判断。运行 `scripts/validate_workflow.py <任务目录>`；修复本工作流产生的结构或路径错误后再交付。
   最终 PDF 默认面向非专业投资者：先给白话结论，再给证据和方法；包含产业链地图、公司赚钱方式、关键指标解释、图表、术语卡、情景和跟踪清单。内容丰富不等于重复或塞满页面。
8. 最终回复列出筛选结果、每家深研状态、参与排名的公司、共同报告期、价格日期、数据缺口、失败项、全部成品路径以及是否可断点续跑。

## 恢复与更新

- 开始执行前读取已有 `workflow_manifest.json`，只复用文件存在、格式有效且与本次主题和截止日一致的 `completed` 阶段。
- 上游样本、截止日或证据发生变化时，将受影响的下游阶段重新设为 `pending`；不得沿用已经失效的排名。
- 单家公司失败后可以从该公司继续；已完成公司无需重跑。若用户要求刷新全部研究，先在清单中记录新截止日和重跑范围。
- 状态文件必须在每个阶段和每家公司开始、完成或失败时立即更新，不能只在任务结束时补写。

## 边界

- 本 Skill 不直接创造筛选分数、财务事实或同行结论；这些分别由三个专业 Skill 负责。
- 不因流程完整而降低来源、期间、可比性或 PDF 视觉检查要求。
- 不把 Top 20 全部自动深研；除非用户明确要求，默认只深研前 5 家，避免生成超出需求的大量报告。
- 排名表示研究与条件性配置优先级，不构成无条件买入指令、收益承诺或精确目标价。
- 外部资料下载、联网、写文件和其他动作仍受当前环境权限约束；Skill 本身不扩大授权范围。
