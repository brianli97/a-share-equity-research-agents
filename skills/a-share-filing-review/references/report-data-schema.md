# 通用报告数据格式

每家公司只保存一份 `extracted/report_data.json`，不要创建 `build_<公司>_report.py`。使用 Skill 内的通用渲染器生成 PDF：

```powershell
python <skill目录>/scripts/build_report.py <输出目录>/extracted/report_data.json
```

## 顶层字段

```json
{
  "title": "公司招股书与财报解读",
  "company": "公司简称",
  "code": "证券代码",
  "footer": "公司简称（证券代码）｜招股书与财报解读",
  "output": "../report/<稳定文件名>.pdf",
  "pages": []
}
```

`output` 相对于 JSON 所在目录。`pages` 是页面数组，每页又是内容块数组；渲染器在页面之间自动分页。

## 内容块

- 段落：`{"type":"paragraph","style":"B","text":"..."}`。可用样式为 `T`、`Sub`、`H1`、`H2`、`B`、`S`、`Q`。
- 间距：`{"type":"spacer","mm":8}`。
- 指标卡：`{"type":"kpis","items":[{"value":"48.88 亿元","label":"营业收入"}]}`。
- 表格：`{"type":"table","widths_mm":[35,45,96],"rows":[["表头1","表头2","表头3"],["...","...","..."]]}`。列宽合计不超过 176 mm。
- 提示框：`{"type":"callout","tone":"risk","title":"关键风险","text":"..."}`。`tone` 可为 `positive`、`warning` 或 `risk`。
- 导读：`{"type":"lead","text":"这一页用一句话说明要回答的问题。"}`。
- 要点列表：`{"type":"bullets","items":["要点一","要点二"]}`，建议 3–6 项。
- 信息卡：`{"type":"cards","items":[{"title":"优势","text":"...","tone":"positive"}]}`，每组 1–3 张。
- 横向条形图：`{"type":"bars","max_value":100,"unit":"%","items":[{"label":"收入增速","value":32.5,"display":"32.5%","tone":"positive"}]}`。`value` 必须是可复核数值，`display` 保留读者看到的单位与精度。
- 多序列柱状图：`{"type":"series_bars","categories":["2023","2024","2025"],"unit":"亿元","series":[{"label":"归母净利润","values":[10.2,12.5,15.1]},{"label":"扣非净利润","values":[9.8,11.9,14.4]}]}`。适合年度/季度趋势和同口径公司对比；支持 2–8 个期间、1–3 个系列，缺失值写 `null`，不得补零。

完整财报解读还应在顶层保存 `financial_history`，至少包含最近 3 个完整年度的 `period`、`revenue`、`net_profit`、`adjusted_net_profit`、`operating_cash_flow`、`roe` 与口径/单位说明。年度表展示同比，季度表仅在已取得真实单季数据时展示环比；不得用累计值直接计算环比。`pages` 至少包含两张 `series_bars`：收入趋势，以及利润/经营现金流/ROE 中至少一组趋势。

生成前检查必填字段、非空页面、表格列数与列宽；生成后仍须按视觉规范逐页渲染检查。结构化数据承载公司事实、计算、判断和引用，通用脚本只负责排版。
