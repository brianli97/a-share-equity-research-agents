# A股招股书与财报解读规则

当用户要求分析 A 股上市公司、招股说明书、财报或生成基本面 PDF 时：

1. 先读取项目内 `.agent-skills/a-share-filing-review/SKILL.md`。
2. 按其中链接依次读取 `references/source-policy.md`、`references/analysis-framework.md` 和 `references/output-convention.md`。
3. 严格执行来源优先级和证据纪律；不要用财经摘要替代官方公告。
4. 需要下载文件、联网、写文件或运行转换工具时，遵守当前 TRAE Agent 的工具和权限设置。
5. 如果不能生成 PDF，交付完整 Markdown 或 HTML，并明确说明缺失能力，不能假装完成。

典型请求：`分析万向钱潮，下载招股说明书和近一年财报，并生成详细解读 PDF。`

