# analyze-sub-domain 评分口径（v0.1）

## 1. 新词分（Novelty, 0-100）

构成：

- 新鲜度（0-40）：关键词在历史分析中“首次出现”比例
- 稀有度（0-25）：关键词历史出现频率越低分越高
- 动量（0-30）：点击量与上涨强度（rise_ratio）
- 惩罚（-20~0）：品牌词/导航词（login/official/brand）

解释：

- >= 70：高潜新词
- 50-69：中等新颖，建议观察
- < 50：偏存量或品牌导向

## 2. 搜索意图（Intent）

分类：

- 工具型（calculator/converter/generator/checker 等）
- 信息型（guide/tutorial/how to/wiki 等）
- 商业调研型（best/vs/compare/review 等）
- 交易型（buy/price/deal/download 等）
- 导航型（login/official/docs/dashboard 等）

输出：

- `intent_label`
- `intent_confidence`（0-100）
- `intent_evidence`（命中词）

## 3. 问题-解法抽取

每个候选输出：

- 用户问题（一句话）
- 当前站点解法（内容/工具/导航）
- 可复制建站方案（建议站型 + MVP 页面）

## 4. 赛道分（Track Score, 0-100）

构成：

- 需求强度（0-30）：点击量等级
- 增长质量（0-25）：趋势与上涨证据
- 意图价值（0-20）：工具型/信息型/商业调研型更高
- 可复制性（0-15）：非品牌、可扩展长尾
- 变现潜力（0-10）：广告/联盟/SaaS/线索

等级：

- A: >=80（优先立项）
- B: 65-79（进入候选池）
- C: 50-64（继续观察）
- D: <50（暂不考虑）

## 5. 硬过滤规则（命中即排除）

- 个人博客/作品集（portfolio/resume/about me）
- 产品官网/品牌导航（official/login/pricing/app/docs）
- 纯文档站（api/changelog/reference）
- 活动落地页（conference/summit/year campaign）
- 本地企业展示站（clinic/restaurant/hotel 等）

输出字段必须包括：

- `excluded=true`
- `exclusion_category`
- `exclusion_reason`
- `exclusion_evidence`
