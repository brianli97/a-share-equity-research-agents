# 统一输出布局

每次完整研究使用一个独立任务目录：

```text
output/
`-- <主题>_<YYYYMMDD>/
    |-- workflow_manifest.json
    |-- scope/
    |   |-- industry_scope.json
    |   |-- industry_scope_report.md
    |   |-- report_data.json
    |   `-- industry_scope_report.pdf
    |-- screening/
    |   |-- universe.json
    |   |-- screening_report.md
    |   `-- sources/source_manifest.json
    |-- companies/
    |   `-- <证券代码>_<公司简称>/
    |       |-- source/
    |       |-- extracted/report_data.json
    |       `-- report/<稳定文件名>.pdf
    `-- peer-ranking/
        |-- comparison/
        |   |-- peer_data.json
        |   |-- ranking_data.json
        |   |-- report_data.json
        |   `-- comparison_report.md
        |-- report/<行业>_同行价值比较_<YYYYMMDD>.pdf
        `-- sources/source_manifest.json
```

主题目录名应移除 Windows 不允许的字符并保持简短。证券代码用于稳定识别公司，不能只用公司简称作为目录键。

## `workflow_manifest.json`

路径全部相对于任务目录，不保存依赖某台机器的绝对路径。

```json
{
  "schema_version": "1.0",
  "topic": "人形机器人产业链",
  "as_of_date": "2026-10-24",
  "parameters": {
    "allowed_boards": ["SSE_MAIN", "SZSE_MAIN", "SZSE_CHINEXT"],
    "excluded_boards": ["SSE_STAR", "BSE"],
    "screening_mode": "composite",
    "screening_top_n": 20,
    "filing_review_top_n": 5,
    "ranking_min_companies": 3
  },
  "stages": {
    "scope_definition": {
      "status": "completed",
      "required": true,
      "data_path": "scope/industry_scope.json",
      "markdown_path": "scope/industry_scope_report.md",
      "report_data_path": "scope/report_data.json",
      "report_path": "scope/industry_scope_report.pdf"
    },
    "screening": {
      "status": "completed",
      "universe_path": "screening/universe.json",
      "report_path": "screening/screening_report.md"
    },
    "filing_reviews": {
      "status": "in_progress",
      "selected_companies": [{
        "security_code": "000001",
        "company_name": "示例股份有限公司",
        "status": "completed",
        "report_data_path": "companies/000001_示例股份/extracted/report_data.json",
        "report_path": "companies/000001_示例股份/report/000001_示例股份_招股书与财报解读_20261024.pdf",
        "error": null
      }]
    },
    "peer_ranking": {
      "status": "pending",
      "peer_data_path": "peer-ranking/comparison/peer_data.json",
      "ranking_data_path": "peer-ranking/comparison/ranking_data.json",
      "report_data_path": "peer-ranking/comparison/report_data.json",
      "markdown_path": "peer-ranking/comparison/comparison_report.md",
      "report_path": "peer-ranking/report/人形机器人产业链_同行价值比较_20261024.pdf"
    }
  },
  "limitations": []
}
```

失败公司保留在 `selected_companies` 中，并在 `error` 写明可操作的失败原因。路径尚未产生时可以为 `null`；一旦相应状态为 `completed`，必要路径必须存在。
