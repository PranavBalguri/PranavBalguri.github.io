-- int_transactions_enriched.sql
-- Joins transactions with account data
-- Adds business context needed by both P&L and fraud marts

with transactions as (
    select * from {{ ref('stg_transactions') }}
),

accounts as (
    select * from {{ ref('stg_accounts') }}
),

enriched as (
    select
        -- Transaction fields
        t.transaction_id,
        t.account_id,
        t.transaction_date,
        t.transaction_month,
        t.transaction_year,
        t.transaction_month_num,
        t.day_of_week,
        t.amount,
        t.amount_abs,
        t.transaction_type,
        t.status,
        t.product_category,
        t.business_line,
        t.description,
        t.flow_direction,
        t.is_flagged,
        t.is_failed,
        t.is_pending,
        t.is_completed,

        -- Account fields
        a.customer_name,
        a.account_type,
        a.account_status,
        a.credit_limit,
        a.risk_tier,
        a.risk_score_base,
        a.relationship_manager,
        a.is_flagged_account,
        a.account_age_days,

        -- Combined risk context
        case
            when t.is_flagged or a.is_flagged_account then 'high'
            when a.risk_tier = 'medium' then 'medium'
            else 'low'
        end                                                     as combined_risk_level,

        -- Revenue contribution (simplified net interest / fee model)
        case
            when t.business_line = 'wealth_management' then t.amount_abs * 0.015
            when t.business_line = 'lending' then t.amount_abs * 0.04
            when t.business_line = 'retail_banking' then t.amount_abs * 0.005
            else 0
        end                                                     as estimated_revenue

    from transactions t
    left join accounts a
        on t.account_id = a.account_id
)

select * from enriched
