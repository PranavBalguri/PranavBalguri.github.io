-- fct_daily_pnl.sql
-- Daily P&L summary by business line and product category
-- This is the core finance reporting mart — mirrors a golden layer in Snowflake

with enriched as (
    select * from {{ ref('int_transactions_enriched') }}
    where is_completed = true  -- only settled transactions affect P&L
),

daily_summary as (
    select
        transaction_date,
        transaction_month,
        transaction_year,
        transaction_month_num,
        business_line,
        product_category,
        relationship_manager,

        -- Volume metrics
        count(transaction_id)                                   as total_transactions,
        count(case when flow_direction = 'inflow' then 1 end)   as inflow_count,
        count(case when flow_direction = 'outflow' then 1 end)  as outflow_count,

        -- Value metrics
        sum(case when flow_direction = 'inflow'
            then amount else 0 end)                             as gross_inflows,
        sum(case when flow_direction = 'outflow'
            then amount_abs else 0 end)                         as gross_outflows,
        sum(amount)                                             as net_position,

        -- Revenue metrics
        round(sum(estimated_revenue), 2)                        as estimated_revenue,

        -- Average transaction size
        round(avg(amount_abs), 2)                               as avg_transaction_size,
        max(amount_abs)                                         as max_transaction_size,

        -- Risk breakdown
        count(case when combined_risk_level = 'high' then 1 end)    as high_risk_count,
        count(case when combined_risk_level = 'medium' then 1 end)  as medium_risk_count,
        count(case when combined_risk_level = 'low' then 1 end)     as low_risk_count

    from enriched
    group by
        transaction_date,
        transaction_month,
        transaction_year,
        transaction_month_num,
        business_line,
        product_category,
        relationship_manager
),

with_mtd as (
    select
        *,
        -- Month-to-date cumulative revenue
        sum(estimated_revenue) over (
            partition by transaction_year, transaction_month_num, business_line
            order by transaction_date
            rows between unbounded preceding and current row
        )                                                       as mtd_revenue,

        -- Month-to-date net position
        sum(net_position) over (
            partition by transaction_year, transaction_month_num, business_line
            order by transaction_date
            rows between unbounded preceding and current row
        )                                                       as mtd_net_position

    from daily_summary
)

select * from with_mtd
order by transaction_date desc, business_line
