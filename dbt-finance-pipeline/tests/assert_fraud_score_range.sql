-- tests/assert_fraud_score_range.sql
-- Custom test: fraud risk score must always be between 0 and 100
-- If any rows fail this, dbt test will fail and alert the team

select
    account_id,
    fraud_risk_score
from {{ ref('fct_fraud_indicators') }}
where fraud_risk_score < 0
   or fraud_risk_score > 100
