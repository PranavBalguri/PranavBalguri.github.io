-- dim_accounts.sql
-- Account dimension table enriched with transaction summary stats
-- Used as a lookup across all reporting

with accounts as (
    select * from {{ ref('stg_accounts') }}
),

transaction_summary as (
    select
        account_id,
        count(transaction_id)               as lifetime_transactions,
        sum(amount_abs)                     as lifetime_volume,
        max(transaction_date)               as last_activity_date,
        min(transaction_date)               as first_activity_date,
        count(distinct product_category)    as products_used
    from {{ ref('stg_transactions') }}
    where is_completed = true
    group by account_id
),

final as (
    select
        a.account_id,
        a.customer_name,
        a.account_type,
        a.account_status,
        a.opened_date,
        a.credit_limit,
        a.risk_tier,
        a.risk_score_base,
        a.relationship_manager,
        a.country,
        a.is_flagged_account,
        a.account_age_days,

        -- Transaction enrichment
        coalesce(t.lifetime_transactions, 0)    as lifetime_transactions,
        coalesce(round(t.lifetime_volume, 2), 0) as lifetime_volume,
        t.last_activity_date,
        t.first_activity_date,
        coalesce(t.products_used, 0)            as products_used,

        -- Engagement tier
        case
            when coalesce(t.lifetime_transactions, 0) >= 10 then 'active'
            when coalesce(t.lifetime_transactions, 0) >= 3 then 'moderate'
            when coalesce(t.lifetime_transactions, 0) >= 1 then 'low'
            else 'dormant'
        end                                     as engagement_tier,

        current_timestamp                       as dbt_updated_at

    from accounts a
    left join transaction_summary t
        on a.account_id = t.account_id
)

select * from final
