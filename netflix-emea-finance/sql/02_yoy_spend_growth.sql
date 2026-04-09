-- ============================================================
-- Query 02: Year-on-Year Spend Growth by Market
-- Business Question: Which markets are growing fastest and
--                    how does 2025 compare to 2024?
-- ============================================================

WITH spend_with_year AS (
    -- Extract year from month field and join to vendors
    SELECT
        s.spend_gbp,
        s.spend_category,
        CAST(LEFT(s.month, 4) AS INTEGER)               AS spend_year,
        v.market
    FROM raw_spend s
    LEFT JOIN raw_vendors v
        ON s.vendor_id = v.vendor_id
),

annual_spend AS (
    -- Total spend per market per year
    SELECT
        market,
        spend_year,
        SUM(spend_gbp)                                  AS total_spend_gbp,
        COUNT(*)                                        AS transaction_count
    FROM spend_with_year
    GROUP BY market, spend_year
),

yoy_comparison AS (
    -- Use LAG to bring prior year spend alongside current
    SELECT
        market,
        spend_year,
        total_spend_gbp                                 AS current_year_spend,
        LAG(total_spend_gbp) OVER (
            PARTITION BY market
            ORDER BY spend_year
        )                                               AS prior_year_spend,
        transaction_count
    FROM annual_spend
)

SELECT
    market,
    spend_year,
    current_year_spend,
    prior_year_spend,
    current_year_spend - prior_year_spend               AS yoy_variance_gbp,
    CASE
        WHEN prior_year_spend IS NULL THEN NULL
        ELSE ROUND(
            (current_year_spend - prior_year_spend)
            * 100.0 / prior_year_spend
        , 1)
    END                                                 AS yoy_growth_pct,
    CASE
        WHEN prior_year_spend IS NULL THEN 'Base Year'
        WHEN current_year_spend > prior_year_spend THEN 'Growth'
        ELSE 'Decline'
    END                                                 AS trend,
    transaction_count
FROM yoy_comparison
ORDER BY market, spend_year
