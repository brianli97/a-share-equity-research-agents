# 输入协议与归一化

## 可接受输入

按优先级使用：

1. 各公司的官方年报、季报、招股书及由其提取的结构化表。
2. `a-share-filing-review` 的完整报告和 `extracted/report_data.json`。
3. `a-share-industry-screening` 的 `screening/universe.json`，只用于研究范围、产业链角色和待验证问题。
4. 可靠行情服务提供的同一交易日价格、市值和估值数据。

筛选阶段的 `scores` 和 `ranks` 不得直接进入价值排名；它们只是研究优先级。单公司报告中的分析判断也应回到原始数字或引用复核。

## `peer_data.json` 最小结构

```json
{
  "schema_version": "1.0",
  "topic": "行业或主题",
  "as_of_date": "YYYY-MM-DD",
  "financial_period": "YYYY-MM-DD",
  "price_date": null,
  "scenarios": {},
  "companies": []
}
```

每家公司：

```json
{
  "security_code": "000000",
  "company_name": "公司全称",
  "short_name": "公司简称",
  "industry_role": "产业链角色",
  "comparability": "high",
  "evidence_quality": 0.85,
  "metrics": {
    "roic": {"value": 12.5, "unit": "%", "period_end": "2025-12-31", "source_id": "...", "direction": "higher"}
  },
  "qualitative_scores": {
    "moat": {"value": 75, "basis": "证据与反证", "source_ids": ["..."]}
  },
  "risks": [],
  "thesis_breakers": [],
  "data_gaps": []
}
```

## 字段规则

- `evidence_quality` 使用 0–1，综合来源等级、期间新鲜度、业务口径和是否可复核。
- `comparability` 为 `high`、`medium` 或 `low`。低可比公司可以展示，但默认不与高可比公司争夺精确名次。
- 数值指标必须带单位、期间/日期、来源和方向。`direction` 为 `higher` 或 `lower`。
- 定性分必须带 `basis`，说明证据、反证和为何不是更高或更低。
- 不使用从文字猜出的精确财务数字。无法取得时留空，并加入 `data_gaps`。

## 期间与单位

- 金额统一为人民币百万元或亿元，并保存原始单位。
- 比率统一为百分比；周转天数使用天；估值倍数使用 `x`。
- 年度数据与季度年化数据分开；不得把单季度利润机械乘四代替正常化利润。
- 对重组、并购和会计政策变化保留 `adjustment_note`。

