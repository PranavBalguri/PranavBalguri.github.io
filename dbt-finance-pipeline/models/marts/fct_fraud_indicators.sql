-- fct_fraud_indicators.sql
-- Fraud risk scoring per account based on transaction behaviour
-- Rule-based model — mirrors real counter-fraud logic used in insurance/banking

with enriched as (
    select * from {{ ref('int_transactions_enriched') }}
),

-- Aggregate transaction behaviour per account
account_behaviour as (
    select
        account_id,
        customer_name,
        account_type,
        account_status,
        risk_tier,
        risk_score_base,
        is_flagged_account,
        credit_limit,
        account_age_days,
        relationship_manager,

        count(transaction_id)                                       as total_transactions,
        sum(amount_abs)                                             as total_volume,
        avg(amount_abs)                                             as avg_transaction_value,
        max(amount_abs)                                             as max_single_transaction,
        count(case when is_flagged then 1 end)                      as flagged_transaction_count,
        count(case when is_failed then 1 end)                       as failed_transaction_count,
        count(case when is_pending then 1 end)                      as pending_transaction_count,

        -- High value transaction count (>£9,000 — near structuring threshold)
        count(case when amount_abs > 9000 then 1 end)               as near_threshold_count,

        -- Velocity: transactions within any rolling period
        max(transaction_date)                                       as last_transaction_date,
        min(transaction_date)                                       as first_transaction_date,

        -- Inflow/outflow ratio
        sum(case when flow_direction = 'inflow' then amount_abs else 0 end)     as total_inflows,
        sum(case when flow_direction = 'outflow' then amount_abs else 0 end)    as total_outflows

    from enriched
    group by
        account_id, customer_name, account_type, account_status,
        risk_tier, risk_score_base, is_flagged_account, credit_limit,
        account_age_days, relationship_manager
),

-- Apply fraud scoring rules
fraud_scored as (
    select
        *,

        -- Rule 1: Account already flagged by compliance (+40 points)
        case when is_flagged_account then 40 else 0 end             as score_flagged_account,

        -- Rule 2: Multiple near-threshold transactions (+15 per occurrence, max 30)
        least(near_threshold_count * 15, 30)                        as score_structuring_pattern,

        -- Rule 3: High ratio of flagged transactions (+20)
        case
            when total_transactions > 0
             and (flagged_transaction_count * 1.0 / total_transactions) > 0.2
            then 20
            else 0
        end                                                         as score_high_flag_ratio,

        -- Rule 4: New account, high volume (+15)
        case
            when account_age_days < 180 and total_volume > 50000
            then 15
            else 0
        end                                                         as score_new_high_volume,

        -- Rule 5: Base risk tier score
        risk_score_base * 5                                         as score_risk_tier,

        -- Rule 6: High failed transaction rate (+10)
        case
            when total_transactions > 0
             and (failed_transaction_count * 1.0 / total_transactions) > 0.1
            then 10
            else 0
        end                                                         as score_failed_rate

    from account_behaviour
),

final as (
    select
        account_id,
        customer_name,
        account_type,
        account_status,
        risk_tier,
        relationship_manager,
        total_transactions,
        round(total_volume, 2)                                      as total_volume,
        round(avg_transaction_value, 2)                             as avg_transaction_value,
        round(max_single_transaction, 2)                            as max_single_transaction,
        flagged_transaction_count,
        near_threshold_count,
        account_age_days,
        round(total_inflows, 2)                                     as total_inflows,
        round(total_outflows, 2)                                    as total_outflows,

        -- Total fraud risk score (0–100)
        least(
            score_flagged_account
            + score_structuring_pattern
            + score_high_flag_ratio
            + score_new_high_volume
            + score_risk_tier
            + score_failed_rate,
            100
        )                                                           as fraud_risk_score,

        -- Human-readable risk band
        case
            when least(
                score_flagged_account + score_structuring_pattern
                + score_high_flag_ratio + score_new_high_volume
                + score_risk_tier + score_failed_rate, 100
            ) >= 60 then 'HIGH — Refer to Fraud Team'
            when least(
                score_flagged_account + score_structuring_pattern
                + score_high_flag_ratio + score_new_high_volume
                + score_risk_tier + score_failed_rate, 100
            ) >= 30 then 'MEDIUM — Enhanced Monitoring'
            else 'LOW — Standard Processing'
        end                                                         as risk_band,

        current_timestamp                                           as scored_at

    from fraud_scored
)

select * from final
order by fraud_risk_score desc
