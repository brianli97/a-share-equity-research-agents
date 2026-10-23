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

报告可以增加页数，但不得省略最终公司排列顺序和价值投资建议。公司很多时，先用总表列全，再为重点公司使用详细证据卡。

