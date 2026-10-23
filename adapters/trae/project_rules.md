# A股行业公司筛选规则

当用户要求筛选 A 股行业、领域、概念、产业链公司，寻找龙头或高热度公司时：

1. 先读取项目内 `.agent-skills/a-share-industry-screening/SKILL.md`。
2. 按其中链接读取 `references/source-policy.md`、`references/screening-framework.md` 和 `references/output-schema.md`。
3. 严格区分官方行业、市场概念和实际业务暴露；不要把热门标签当成主营业务证据。
4. 对行情、估值、财务和热度数据分别记录日期；缺失数据不得默认记零。
5. 需要联网、下载资料、写文件或运行工具时，遵守当前 TRAE Agent 的工具和权限设置。
6. 输出候选池、入选与排除理由、数据来源、风险及证据等级，不把排名表述为买卖建议。

典型请求：`筛选人形机器人产业链前20家A股公司，分别生成龙头榜、热度榜和基本面榜。`

