-- ============================================================
-- Query 04: Top Vendors & Spend Concentration Analysis
-- Business Question: Who are our biggest vendors and do we
--                    have concentration risk?
-- ============================================================

WITH vendor_spend_summary AS (
    SELECT
        v.vendor_id,
        v.vendor_name,
        v.vendor_type,
        v.market,
        SUM(s.spend_gbp)                                AS total_spend_gbp,
        COUNT(DISTINCT s.production_id)                 AS productions_supported,
        COUNT(s.spend_id)                               AS invoice_count,
        ROUND(AVG(s.spend_gbp), 0)                      AS avg_invoice_gbp,
        MAX(s.spend_gbp)                                AS largest_single_invoice,
        MIN(s.spend_gbp)                                AS smallest_single_invoice
    FROM raw_spend s
    LEFT JOIN raw_vendors v
        ON s.vendor_id = v.vendor_id
    GROUP BY
        v.vendor_id, v.vendor_name,
        v.vendor_type, v.market
),

total_spend AS (
    SELECT SUM(spend_gbp) AS grand_total FROM raw_spend
),

vendor_ranked AS (
    SELECT
        vs.*,
        ts.grand_total,
        ROUND(
            vs.total_spend_gbp * 100.0 / ts.grand_total
        , 2)                                            AS pct_of_total_spend,
        RANK() OVER (
            ORDER BY vs.total_spend_gbp DESC
        )                                               AS overall_rank,
        RANK() OVER (
            PARTITION BY vs.market
            ORDER BY vs.total_spend_gbp DESC
        )                                               AS rank_within_market
    FROM vendor_spend_summary vs
    CROSS JOIN total_spend ts
),

cumulative_spend AS (
    SELECT
        *,
        SUM(pct_of_total_spend) OVER (
            ORDER BY total_spend_gbp DESC
            ROWS BETWEEN UNBOUNDED PRECEDING
            AND CURRENT ROW
        )                                               AS cumulative_pct
    FROM vendor_ranked
)

SELECT
    overall_rank,
    vendor_name,
    vendor_type,
    market,
    total_spend_gbp,
    pct_of_total_spend,
    cumulative_pct,
    productions_supported,
    invoice_count,
    avg_invoice_gbp,
    largest_single_invoice,
    rank_within_market,

    -- Concentration risk flag
    CASE
        WHEN pct_of_total_spend > 20
            THEN 'HIGH — Single vendor risk'
        WHEN pct_of_total_spend > 10
            THEN 'MEDIUM — Monitor closely'
        ELSE 'LOW — Acceptable'
    END                                                 AS concentration_risk,

    -- Top 3 flag for 80/20 analysis
    CASE
        WHEN overall_rank <= 3 THEN TRUE
        ELSE FALSE
    END                                                 AS is_top_3_vendor

FROM cumulative_spend
ORDER BY overall_rank
