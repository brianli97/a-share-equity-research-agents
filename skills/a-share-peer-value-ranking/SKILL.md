---
name: a-share-peer-value-ranking
description: Compare multiple A-share companies in the same industry using standardized filing-review evidence, rank business quality, growth, financial resilience, valuation and margin of safety, and deliver a sourced PDF report with an ordered value-investing research shortlist. Use for A股同行横向比较、行业公司价值排序、财报汇总排名、价值投资建议与候选分层 or comparing outputs from a-share-filing-review. Do not use to screen an industry universe from scratch, analyze only one company, or issue unconditional buy/sell instructions.
---

# A股同行价值比较与排序

读取同行公司的公开披露研究结果，统一报告期、口径和证据等级，输出可复核的横向比较 PDF、多情景排名和价值投资研究建议。报告必须明确给出公司排列顺序，但把排名解释为研究与配置条件的优先级，不写成无条件买入指令或收益承诺。

## 执行前读取

1. 读取 [references/input-contract.md](references/input-contract.md)，检查行业筛选和单公司深研输入是否完整。
2. 读取 [references/comparison-framework.md](references/comparison-framework.md)，选择可比指标、行业适配和情景权重。
3. 涉及估值或“更值得投资”时读取 [references/valuation-policy.md](references/valuation-policy.md)，统一估值日期并约束安全边际结论。
4. 读取 [references/output-schema.md](references/output-schema.md)，生成标准化中间数据和最终交付物。

## 默认输入

- 可选读取 `a-share-industry-screening` 生成的 `screening/universe.json`，取得研究范围、入选理由和行业角色。
- 读取每家公司由 `a-share-filing-review` 生成的 `extracted/report_data.json`、完整 Markdown/HTML/PDF 报告或其提取表。
- 至少三家公司才形成排名；少于三家时只做并列比较。
- 默认以最近一个完整年度为共同基期，并用之后最新季度或半年度材料检查趋势。报告期不一致时先重述为共同口径，无法重述则标记不可比。

## 工作流

1. 核对证券代码、公司全称、行业角色、报告期和价格时点，建立输入清单。禁止把同一家公司不同名称当成两个样本。
2. 从各公司报告中提取事实和计算结果，保存到 `comparison/peer_data.json`。页面排版结构不是数据口径；不要直接按 `report_data.json` 的页数、段落或措辞评分。
3. 统一币种、单位、会计期间和计算公式。对并购重组、会计政策变化、周期高低点、亏损阶段和业务结构差异作可比性调整。
4. 比较业务质量、护城河证据、增长质量、盈利与现金流、资产负债、资本配置、治理与风险。只有取得统一价格日期后才加入估值和安全边际。
5. 将“事实数据”“计算指标”“分析判断”“估算结果”分开；每个核心结论保留来源、期间和证据等级。
6. 使用可用指标计算分项分位排名。缺失值不得填零；重新归一剩余权重，并以覆盖率和证据质量降低最终置信度。
7. 至少展示质量优先、成长优先、估值优先三种情景。估值数据不可用时停用估值情景，不用旧价格或不同日期数据补位。
8. 进行稳健性检查：改变权重、去除单一指标和处理极端值后，记录排名变化。高度敏感的名次不得写成确定结论。
9. 输出综合排名之外的候选分层、每家公司的优势/反证/失效条件，以及“为什么排名靠前或靠后”。最终结论必须按顺序列出所有参评公司，并给出价值投资研究建议。
10. 保存 `comparison/peer_data.json`、`comparison/ranking_data.json`、`comparison/report_data.json` 和 `comparison/comparison_report.md`。
11. 默认使用 `scripts/build_comparison_report.py` 生成 `report/<行业>_同行价值比较_<YYYYMMDD>.pdf`。逐页渲染检查字体、表格、裁切、重叠、分页与来源可读性；不合格就修改通用数据或渲染器后重建。仅在 PDF 工具不可用时交付完整 Markdown，并明确说明限制。

## 默认候选分层

- **重点研究**：质量、证据和估值至少两项占优，且没有未解释的重大风险。
- **优秀但等待价格**：业务质量较高，但缺少安全边际或估值明显偏高。
- **成长验证期**：潜在增速高，但现金流、订单转收入或资本回报尚未证实。
- **价值观察**：估值较低，但需验证周期位置、资产质量或治理问题。
- **证据不足/高风险**：关键数据缺失、业务暴露低、治理或财务风险显著。

## 最终价值投资建议

报告结论按综合研究顺序列出全部公司，并对每家公司给出以下之一：

- **优先研究/满足价格条件可考虑**：质量和证据较强，且在取得统一估值后显示合理安全边际。
- **优秀公司，等待更好价格**：质量较强，但估值或安全边际不足。
- **成长验证期，等待经营证据**：潜力较高，但订单转收入、现金流或资本回报尚未验证。
- **价值观察，先排除陷阱**：估值可能较低，但周期、资产质量或治理风险需要先解决。
- **暂不优先**：相对质量、风险或证据覆盖不足。

每条建议必须同时写明：适用条件、主要证据、最大反证、需要的价格/经营触发条件以及投资逻辑失效条件。没有统一价格数据时，不得使用“低估”“安全边际充足”或“值得买入”，应写“基本面优先研究”或“等待价格数据”。

## 排名纪律

- 不因单一低 PE、热门概念或管理层规划把公司列为首选。
- 市值、价格与估值必须使用同一交易日；否则只比较基本面。
- 亏损公司不使用失真的 PE；周期公司不使用景气顶点利润得出“便宜”结论。
- 相关业务尚处送样、研发或小批量阶段时，不把总公司历史利润当成新业务盈利能力。
- 综合分必须同时展示分项分、覆盖率、证据置信度和情景变化。
- 不给出精确目标价；用户明确要求估值区间时，展示假设和敏感性，不把情景写成预测。

## 脚本使用

完成并校验 `comparison/peer_data.json` 后，可运行：

```powershell
python <skill目录>/scripts/rank_peers.py <输出目录>/comparison/peer_data.json
python <skill目录>/scripts/build_comparison_report.py <输出目录>/comparison/report_data.json
```

排名脚本只执行确定性的标准化、缺失值处理、覆盖率计算和情景排序；PDF脚本只负责排版。两者都不负责创造原始财务数据或分析判断。

## 异常处理

- 输入只有摘要、没有来源或期间：先补证据；无法补齐时降低等级，不生成伪精确排名。
- 公司跨多个行业：优先比较同一业务分部；没有分部数据时降低可比性。
- 新上市或历史不足：允许进入比较，但不计算需要三至五年序列的指标。
- 金融、地产与一般制造业混合：不得使用同一套指标直接排名，应拆组比较。
- 所有公司均缺价格数据：交付“基本面研究优先级”，明确无法判断当前安全边际。

