# 四、数据模型与证据模型

## 1. 核心实体

### Company

- `company_id`
- `legal_name`
- `brand_name`
- `aliases[]`
- `country`
- `headquarters`
- `founded_date`
- `website`
- `product_summary`
- `customer_type`
- `business_model`
- `deployment_model`
- `sector_tags[]`

### FinancingEvent

- `event_id`
- `company_id`
- `announcement_date`
- `transaction_date`
- `round_label_raw`
- `round_normalized`
- `amount_original`
- `currency_original`
- `amount_usd` / `amount_cny`
- `fx_rate_date`
- `valuation`
- `valuation_status`
- `cumulative_funding`
- `lead_investors[]`
- `other_investors[]`
- `fund_use[]`

换算金额只用于比较，文章首先展示原币金额，并注明汇率日期。

### Investor

- `investor_id`
- `legal_entity_name`
- `brand_name`
- `manager_name`
- `investor_type`
- `country`
- `website`
- `portfolio_matches[]`
- `first_entry_round`
- `follow_on_status`

### Source

- `source_id`
- `url`
- `publisher`
- `title`
- `published_at`
- `accessed_at`
- `tier`
- `language`
- `content_type`
- `content_hash`
- `archive_path`
- `access_notes`

### Claim

- `claim_id`
- `case_id`
- `statement`
- `claim_type`: `F/S/H`
- `topic`
- `confidence`: `A/B/C/D`
- `source_ids[]`
- `quoted_excerpt`（短摘录）
- `location_hint`（页码/段落/字段）
- `conflict_status`
- `review_status`
- `reviewer`

### Comparable

- `foreign_company_id`
- `china_company_id`
- 六维评分及解释
- `total_score`
- `comparison_type`
- `why_comparable`
- `why_not_comparable`

### FollowUp

- `hypothesis_id`
- `hypothesis`
- `metric`
- `baseline`
- `target_or_trigger`
- `review_date`
- `result`
- `conclusion_change`

## 2. 可信度等级

- `A`：一级来源直接确认；
- `B`：两个独立可信来源一致，或一级来源加二级来源；
- `C`：单一可信媒体/商业数据库；
- `D`：代理信号、推断、未证实或存在重大冲突。

关键交易字段不得低于 B；观点可以是 H，但必须明确写出依据。

## 3. Claim–Evidence 原则

文章不是事实库。先建立 Claim，再生成文章：

1. 每个关键陈述拆成最小可核验 Claim；
2. Claim 绑定一个或多个 Source；
3. 记录证据位置；
4. 冲突来源同时保留；
5. 渲染文章时只使用达到质量门槛的 Claim；
6. 观点段落必须指向支持它的事实或信号。

## 4. 版本与更正

- 案例数据使用不可变版本号；
- 发布后修正必须记录 `changed_field`、旧值、新值、原因、来源和时间；
- 不覆盖原判断，追加“判断更新”；
- 原始来源与处理后数据分目录保存。
