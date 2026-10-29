# 输出协议

## 文件布局

```text
<行业或主题>-screening/
|-- screening/
|   |-- universe.json
|   `-- screening_report.md
`-- sources/
    `-- source_manifest.json
```

PDF 仅在用户要求时生成；不得删除 JSON 和 Markdown 原件。

## `universe.json`

顶层结构：

```json
{
  "schema_version": "1.0",
  "topic": {},
  "scope": {},
  "methodology": {},
  "rankings": {},
  "companies": [],
  "scope_excluded_companies": [],
  "excluded_companies": [],
  "sources": [],
  "limitations": []
}
```

必要字段：

- `topic`: `name`、`type`、`definition`、`included_segments`、`excluded_segments`。
- `scope`: `markets`、`discovery_boards`、`boards`、`excluded_boards`、`security_types`、`as_of_date`、`financial_period`、`top_n`、`eligibility_rules`。默认发现池覆盖全部 A 股普通股，`boards` 仍为 `SSE_MAIN`、`SZSE_MAIN`、`SZSE_CHINEXT`。
- `methodology`: 筛选模式、指标定义、方向、标准化、权重、缺失处理和敏感性情景。
- `rankings`: `leader`、`attention`、`fundamental`、`composite`，每项存证券代码数组和生成规则。
- `sources`: 来源标题、URL、来源等级、披露/数据日期和访问日期。

每家公司至少包含：

```json
{
  "security_code": "000000",
  "exchange": "SZSE",
  "board": "SZSE_MAIN",
  "company_name": "示例股份有限公司",
  "short_name": "示例股份",
  "official_industry": "",
  "theme_role": "",
  "business_exposure": {
    "value": null,
    "range": null,
    "basis": "",
    "is_estimate": false,
    "confidence": "high"
  },
  "metrics": {},
  "scores": {},
  "ranks": {},
  "included_reason": [],
  "risks": [],
  "evidence_level": "A",
  "data_gaps": [],
  "selection_traits": ["leader"],
  "deep_review_questions": [],
  "source_ids": []
}
```

每家公司必须包含 `board`，且与 `scope.boards` 一致；属于 `scope.discovery_boards` 但不属于 `scope.boards` 的产业关键公司移入 `scope_excluded_companies`，写明 `excluded_reason` 与 `industry_map_importance`，不得进入任何排名。其他排除项仍进入 `excluded_companies`。

`metrics` 中的每个数值对象应带 `value`、`unit`、`period_end` 或 `as_of_date`、`source_id`，派生数据另带 `formula`。不要只保存脱离日期和单位的裸数字。

## 与公司深研衔接

向 `a-share-filing-review` 传递：

- 公司全称、证券代码、交易所。
- 统一的研究截止日。
- 入选榜单和入选理由。
- 主题业务暴露及其证据等级。
- `deep_review_questions` 中需要通过年报、招股书验证的问题。

筛选结果属于候选池判断。单公司深研完成后，应以深研的 `extracted/report_data.json` 覆盖或修正筛选阶段的简化结论，并保留变更记录。

