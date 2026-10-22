# 输出目录与交付规则

默认在当前工作目录创建：

```text
output/a-share-filing-review/
└─ <证券代码>_<公司简称>_<YYYYMMDD>/
   ├─ source/
   ├─ extracted/
   └─ report/
```

- `source/`：官方招股书、年报、半年报或季报；第三方历史镜像必须在文件名中标注。
- `extracted/`：结构化数据、文本提取和计算表。每家公司保存一份 `report_data.json` 供通用渲染器使用，不保存公司专用构建脚本。
- `report/`：最终 PDF；若环境不能生成 PDF，存放完整 Markdown 或 HTML 并说明限制。

最终报告采用稳定文件名：

```text
<证券代码>_<公司简称>_招股书与财报解读_<YYYYMMDD>.pdf
```

报告生成统一使用 Skill 内的 `scripts/build_report.py`；报告内容遵循 [report-data-schema.md](report-data-schema.md)。

交付前检查：

1. PDF 能打开且页数大于零。
2. 中文字体正常，无裁切、重叠、表格溢出和空白异常。
3. 每个关键数字能追溯至文件、章节或页码。
4. 最终回复列出报告期、未审计口径、缺失资料和全部成品路径。

