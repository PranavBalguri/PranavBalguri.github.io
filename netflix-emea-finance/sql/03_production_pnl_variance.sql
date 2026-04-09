-- ============================================================
-- Query 03: Production P&L — Budget vs Actual Variance
-- Business Question: Which productions are over or under
--                    budget and by how much?
-- ============================================================

WITH production_variance AS (
    SELECT
        production_id,
        title,
        genre,
        market,
        year,
        quarter,
        status,
        budget_gbp,
        actual_spend_gbp,

        -- Absolute variance
        actual_spend_gbp - budget_gbp                   AS variance_gbp,

        -- Percentage variance
        ROUND(
            (actual_spend_gbp - budget_gbp)
            * 100.0 / budget_gbp
        , 1)                                            AS variance_pct,

        -- Budget status classification
        CASE
            WHEN actual_spend_gbp > budget_gbp * 1.10
                THEN 'Significantly Over Budget'
            WHEN actual_spend_gbp > budget_gbp
                THEN 'Slightly Over Budget'
            WHEN actual_spend_gbp < budget_gbp * 0.90
                THEN 'Significantly Under Budget'
            ELSE 'On Budget'
        END                                             AS budget_status,

        -- Flag for over budget
        CASE
            WHEN actual_spend_gbp > budget_gbp
                THEN TRUE
            ELSE FALSE
        END                                             AS is_over_budget

    FROM raw_productions
),

market_pnl_summary AS (
    -- Rollup to market level
    SELECT
        market,
        COUNT(production_id)                            AS total_productions,
        SUM(budget_gbp)                                 AS total_budget,
        SUM(actual_spend_gbp)                           AS total_actual,
        SUM(variance_gbp)                               AS total_variance,
        ROUND(AVG(variance_pct), 1)                     AS avg_variance_pct,
        SUM(CASE WHEN is_over_budget THEN 1 ELSE 0 END) AS over_budget_count,
        SUM(CASE WHEN NOT is_over_budget
            THEN 1 ELSE 0 END)                          AS on_or_under_budget_count
    FROM production_variance
    GROUP BY market
)

-- Production level detail
SELECT
    pv.production_id,
    pv.title,
    pv.genre,
    pv.market,
    pv.year,
    pv.quarter,
    pv.status,
    pv.budget_gbp,
    pv.actual_spend_gbp,
    pv.variance_gbp,
    pv.variance_pct,
    pv.budget_status,
    pv.is_over_budget,

    -- Market context
    ms.total_budget                                     AS market_total_budget,
    ms.avg_variance_pct                                 AS market_avg_variance_pct,

    -- Rank by overspend within market
    RANK() OVER (
        PARTITION BY pv.market
        ORDER BY pv.variance_gbp DESC
    )                                                   AS overspend_rank_in_market

FROM production_variance pv
LEFT JOIN market_pnl_summary ms
    ON pv.market = ms.market
ORDER BY
    pv.variance_gbp DESC
