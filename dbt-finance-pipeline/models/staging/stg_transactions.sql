-- stg_transactions.sql
-- Cleans and standardises raw transaction data
-- Applies consistent naming, types, and removes nulls

with source as (
    select * from {{ ref('raw_transactions') }}
),

cleaned as (
    select
        transaction_id,
        account_id,
        cast(transaction_date as date)               as transaction_date,
        cast(amount as decimal(18, 2))               as amount,
        abs(cast(amount as decimal(18, 2)))          as amount_abs,
        lower(trim(transaction_type))                as transaction_type,
        lower(trim(status))                          as status,
        lower(trim(product_category))                as product_category,
        lower(trim(business_line))                   as business_line,
        trim(description)                            as description,

        -- Derived flags
        case when amount > 0 then 'inflow' else 'outflow' end   as flow_direction,
        case when status = 'flagged' then true else false end    as is_flagged,
        case when status = 'failed' then true else false end     as is_failed,
        case when status = 'pending' then true else false end    as is_pending,
        case when status = 'completed' then true else false end  as is_completed,

        -- Date parts for aggregation
        date_trunc('month', cast(transaction_date as date))     as transaction_month,
        extract('year' from cast(transaction_date as date))     as transaction_year,
        extract('month' from cast(transaction_date as date))    as transaction_month_num,
        extract('dow' from cast(transaction_date as date))      as day_of_week

    from source
    where transaction_id is not null
      and account_id is not null
      and amount is not null
)

select * from cleaned
