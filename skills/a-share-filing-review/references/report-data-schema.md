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

生成前检查必填字段、非空页面、表格列数与列宽；生成后仍须按视觉规范逐页渲染检查。结构化数据承载公司事实、计算、判断和引用，通用脚本只负责排版。
