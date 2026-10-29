# 输出协议

## 文件布局

```text
<行业或主题>-peer-ranking/
|-- comparison/
|   |-- peer_data.json
|   |-- ranking_data.json
|   |-- report_data.json
|   `-- comparison_report.md
|-- report/
|   `-- <行业>_同行价值比较_<YYYYMMDD>.pdf
`-- sources/
    `-- source_manifest.json
```

PDF 是默认最终交付物；JSON 和 Markdown 是可复核原件，不因生成 PDF 而删除。读取 [report-data-schema.md](report-data-schema.md) 构建 `report_data.json`，并使用通用渲染器生成 PDF。

## `ranking_data.json`

由 `scripts/rank_peers.py` 生成：

```json
{
  "schema_version": "1.0",
  "generated_at": "...",
  "input": "peer_data.json",
  "comparison_mode": "formal_ranking",
  "scenarios": {
    "quality_first": {
      "enabled": true,
      "weights": {},
      "ranking": []
    }
  },
  "companies": []
}
```

正式排名的每个排名项包含 `security_code`、`score`、`coverage_ratio`、`evidence_quality`、`confidence` 和 `rank`。3–4 家方向性比较把 `score` 设为 `null`，使用 `directional_order` 与 `relative_tier`；关闭的情景给出 `enabled: false` 与 `reason`。

## 报告结构

1. 一页结论：行业背景、共同基期、价格日期和最大限制。
2. 可比性矩阵：哪些公司真正可比，哪些只能旁列。
3. 原始指标表：保留单位、期间和来源。
4. 质量、成长、现金流、资产负债、资本配置和估值分项。
5. 三套情景排名与名次变化。
6. 按综合研究优先级列出第1至第N名，并解释每个名次。
7. 价值投资建议分层，以及每家公司“适用条件—优势—反证—失效条件—下期验证”。
8. 对排名前列公司给出需要满足的价格或经营触发条件；缺少统一价格时明确写“无法判断当前安全边际”。
9. 数据缺口、敏感性和读者复核方法。

## 与 Workflow 衔接

- 上游：读取 `a-share-industry-screening/screening/universe.json` 确定样本。
- 中游：读取各公司 `a-share-filing-review/extracted/report_data.json` 及原始引用，归一为 `peer_data.json`。
- 本 Skill：生成 `ranking_data.json`、`comparison_report.md` 和最终 PDF。
- 后续更新：新增财报或价格时只更新对应公司字段与共同价格日期，再重新运行排名脚本。

