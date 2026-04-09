-- ============================================================
-- Query 01: Total Vendor Spend by EMEA Market
-- Business Question: Which markets are we spending the most
--                    in and what is the spend breakdown?
-- ============================================================

WITH spend_enriched AS (
    -- Join spend to vendors to get market and vendor type
    SELECT
        s.spend_id,
        s.production_id,
        s.spend_gbp,
        s.spend_category,
        s.month,
        v.vendor_name,
        v.vendor_type,
        v.market
    FROM raw_spend s
    LEFT JOIN raw_vendors v
        ON s.vendor_id = v.vendor_id
),

market_summary AS (
    -- Aggregate total spend per market and category
    SELECT
        market,
        spend_category,
        SUM(spend_gbp)                                  AS total_spend_gbp,
        COUNT(DISTINCT production_id)                   AS productions_count,
        COUNT(spend_id)                                 AS transaction_count,
        ROUND(AVG(spend_gbp), 0)                        AS avg_transaction_gbp
    FROM spend_enriched
    GROUP BY market, spend_category
),

market_totals AS (
    -- Get total per market for percentage calculation
    SELECT
        market,
        SUM(total_spend_gbp)                            AS market_total_gbp
    FROM market_summary
    GROUP BY market
)

SELECT
    ms.market,
    ms.spend_category,
    ms.total_spend_gbp,
    ms.productions_count,
    ms.transaction_count,
    ms.avg_transaction_gbp,
    mt.market_total_gbp,
    ROUND(
        ms.total_spend_gbp * 100.0 / mt.market_total_gbp
    , 1)                                                AS pct_of_market_spend,
    RANK() OVER (
        PARTITION BY ms.market
        ORDER BY ms.total_spend_gbp DESC
    )                                                   AS spend_rank_within_market
FROM market_summary ms
LEFT JOIN market_totals mt
    ON ms.market = mt.market
ORDER BY
    mt.market_total_gbp DESC,
    ms.market,
    ms.total_spend_gbp DESC
