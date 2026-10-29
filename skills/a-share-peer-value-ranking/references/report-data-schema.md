# 横向比较 PDF 数据格式

每个行业比较只保存一份 `comparison/report_data.json`，由通用渲染器生成 PDF：

```powershell
python <skill目录>/scripts/build_comparison_report.py <输出目录>/comparison/report_data.json
```

## 顶层字段

```json
{
  "title": "人形机器人产业链同行价值比较",
  "topic": "人形机器人产业链",
  "as_of_date": "2026-10-23",
  "footer": "人形机器人产业链｜同行价值比较",
  "output": "../report/人形机器人产业链_同行价值比较_20261023.pdf",
  "pages": []
}
```

`output` 相对于 `report_data.json`。`pages` 为页面数组，每页包含内容块。渲染器在页面之间强制分页，表格自身允许按行拆页。

## 内容块

- 段落：`{"type":"paragraph","style":"B","text":"..."}`；样式为 `T`、`Sub`、`H1`、`H2`、`B`、`S`、`Q`。
- 间距：`{"type":"spacer","mm":6}`。
- 指标卡：`{"type":"kpis","items":[{"value":"20家","label":"参评公司"}]}`，每组1至4项。
- 表格：`{"type":"table","widths_mm":[12,28,35,101],"rows":[["排名","公司","分层","核心结论"],...]}`；列宽合计不超过176 mm。
- 提示框：`{"type":"callout","tone":"positive","title":"价值投资建议","text":"..."}`；`tone` 为 `positive`、`warning` 或 `risk`。
- 导读：`{"type":"lead","text":"本页解决的问题。"}`。
- 要点列表：`{"type":"bullets","items":["要点一","要点二"]}`。
- 信息卡：`{"type":"cards","items":[{"title":"质量领先","text":"...","tone":"positive"}]}`。
- 横向条形图：`{"type":"bars","max_value":100,"unit":"分","items":[{"label":"公司A","value":88.2,"display":"88.2","tone":"positive"}]}`，用于分项分、增速和排名差异；必须同时显示数值。
- 多序列柱状图：`{"type":"series_bars","categories":["公司A","公司B"],"unit":"亿元","series":[{"label":"扣非净利润","values":[12.5,8.4]},{"label":"经营现金流","values":[15.1,7.9]}]}`。适合同期横向对比或 3–5 年趋势；支持 2–8 个类别、1–3 个系列，缺失值写 `null`，不得补零。

完整同行报告至少包含两张数据图：一张同期间公司规模/盈利对比，一张现金流、ROE 或多年增长对比。输入公司的 `financial_history` 未达到各自 `history_policy.required_years` 时必须显式披露并降低置信度，不得以较短窗口冒充完整趋势。

## 必需页面

1. 封面和一页结论。
2. 样本、共同报告期、价格日期和方法。
3. 综合公司排序及置信度。
4. 业务质量、成长、现金流、资产负债和资本配置比较。
5. 估值与安全边际；不可用时明确说明原因。
6. 质量、成长、估值情景及敏感性。
7. 价值投资建议分层。
8. 每家公司适用条件、核心证据、最大反证和失效条件。
9. 数据缺口、来源与复核方法。

报告应让非专业读者在不阅读原始财报的情况下理解“各公司做什么、为什么可比或不可比、名次由什么驱动、下一步验证什么”。专业术语首次出现时给出白话解释，并至少包含一页术语/方法说明。

报告可以增加页数，但不得省略最终公司排列顺序和价值投资建议。公司很多时，先用总表列全，再为重点公司使用详细证据卡。

