-- stg_accounts.sql
-- Cleans and standardises raw account master data

with source as (
    select * from {{ ref('raw_accounts') }}
),

cleaned as (
    select
        account_id,
        trim(customer_name)                         as customer_name,
        lower(trim(account_type))                   as account_type,
        lower(trim(account_status))                 as account_status,
        cast(opened_date as date)                   as opened_date,
        cast(credit_limit as decimal(18, 2))        as credit_limit,
        lower(trim(risk_tier))                      as risk_tier,
        trim(relationship_manager)                  as relationship_manager,
        upper(trim(country))                        as country,

        -- Derived fields
        case
            when account_status = 'flagged' then true
            else false
        end                                         as is_flagged_account,

        case
            when risk_tier = 'high' then 3
            when risk_tier = 'medium' then 2
            when risk_tier = 'low' then 1
            else 0
        end                                         as risk_score_base,

        datediff(
            'day',
            cast(opened_date as date),
            current_date
        )                                           as account_age_days

    from source
    where account_id is not null
)

select * from cleaned
