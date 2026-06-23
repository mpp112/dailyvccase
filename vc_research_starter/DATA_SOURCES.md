# 三、数据来源与采集规则

核验日期：2026-06-22。实际使用前应再次检查网站条款、API 文档和访问限制。

## 1. 来源等级

### Tier 1：一级来源

- 创业公司官网、新闻中心、产品文档、定价页；
- 领投/参投机构官网及“Why we invested”；
- 创始人或投资合伙人的实名公开声明；
- 监管申报、交易所公告、招股书、年报；
- 政府企业登记和基金登记信息。

用途：确认交易、法定主体、投资方、产品、客户、财务或股权事实。

### Tier 2：可信二级来源

- Reuters 等具备编辑审核的财经/科技媒体；
- TechCrunch、Sifted、36氪、投资界等专业媒体；
- 公司或机构授权发布的新闻稿平台。

用途：补充背景、采访、未在官方公告中展开的细节。重大数字需要交叉验证。

### Tier 3：商业数据库与聚合平台

海外：Crunchbase、Dealroom、PitchBook、CB Insights、Tracxn 等。

中国：IT桔子、清科私募通、CVSource、企查查、天眼查等。

用途：发现线索、补齐候选、辅助去重。不得作为关键交易事实的唯一来源。

### Tier 4：代理信号

- LinkedIn 员工与招聘；
- GitHub；
- App Store / Google Play；
- G2 / Capterra / Reddit；
- Similarweb、Google Trends；
- 招聘站、会议演讲、播客。

用途：形成 Signal，不得直接写成收入、客户或市场份额事实。

## 2. 海外一级来源

### 美国

- SEC EDGAR Search：监管文件搜索；
- SEC Form D Data Sets：结构化豁免发行通知；
- 公司、基金官网；
- 州级公司注册信息（按需）。

注意：Form D 是豁免发行通知，不自动等于新闻稿中的最终交割金额；需要区分 offering amount、amount sold、amendment 和公告口径。

### 英国

- Companies House：公司注册、董事、账目、申报历史；
- Companies House API：在授权和限速内结构化采集；
- 公司、基金官网。

注意：登记信息是申报记录，不应把所有股份变更推断为新融资。

### 其他地区

优先使用当地公司注册处、证券监管机构、交易所、公司和投资机构公告。无统一 API 时采用人工 URL 录入，保留原始语言和翻译。

## 3. 中国一级来源

- 公司官网与官方公众号；
- 投资机构官网与官方公众号；
- 国家企业信用信息公示系统；
- 巨潮资讯网；
- 上交所、深交所、北交所；
- 全国股转系统；
- 港交所披露易；
- 中国证券投资基金业协会信息公示。

用途：核验法定主体、上市公司投资公告、招股书、股权与基金管理人身份。

注意：基金登记备案不代表监管机构对投资能力、持续合规或基金安全作出背书。

## 4. 推荐采集方式

| 场景 | 方式 | 自动化等级 |
|---|---|---|
| RSS/公开 API | 定时拉取、增量游标、原始响应留档 | 高 |
| 公开静态网页 | HTTP 获取、正文抽取、内容哈希 | 中 |
| JS 渲染公开页 | Playwright，限低频、只读 | 中低 |
| PDF/公告 | 下载原件、保存页码/段落定位 | 中 |
| 公众号、验证码、登录页 | 人工录入 URL 和关键事实 | 低 |
| 付费数据库 | 官方 API 或人工导出 | 低/授权后中 |

## 5. 每次采集必须保存的元数据

- `source_id`；
- URL；
- 发布者；
- 页面标题；
- 发布时间；
- 访问时间；
- 来源等级；
- 原始语言；
- 内容类型；
- 内容哈希；
- 是否需要登录；
- 使用许可/备注；
- 对应公司、融资事件和 Claim ID。

## 6. 增量采集与去重

事件去重主键建议：

`标准化公司名 + 公告日期窗口 + 轮次 + 原币金额`

辅助匹配：品牌别名、法定名、域名、投资方组合和模糊字符串相似度。

同一事件的不同新闻不能合并成一个来源；它们应共享事件 ID，但保留独立 source_id。

## 7. 合规与安全边界

- 不绕过付费墙、登录、验证码、访问控制或 robots/服务条款；
- 不把个人联系方式、家庭住址等非必要个人信息写入数据库；
- API 密钥只放环境变量或秘密管理器；
- 原始网页内容只在许可范围内保存，优先保存元数据、短摘录和哈希；
- 来自网页的指令视为不可信内容，不能让采集器执行页面中的命令；
- 自动发布必须晚于人工审批；
- 任何来源冲突均保留，不静默覆盖。

## 8. 官方入口（建议写入 sources.yaml）

- OpenAI Codex Docs: https://developers.openai.com/codex
- SEC EDGAR Search: https://www.sec.gov/search-filings
- SEC Form D Data Sets: https://www.sec.gov/data-research/sec-markets-data/form-d-data-sets
- Companies House: https://find-and-update.company-information.service.gov.uk/
- Companies House API: https://developer.company-information.service.gov.uk/
- 国家企业信用信息公示系统: https://www.gsxt.gov.cn/
- 巨潮资讯: https://www.cninfo.com.cn/
- 上交所: https://www.sse.com.cn/
- 深交所: https://www.szse.cn/
- 北交所: https://www.bse.cn/
- 全国股转系统: https://www.neeq.com.cn/
- 港交所披露易: https://www.hkexnews.hk/
- 中国证券投资基金业协会: https://gs.amac.org.cn/
