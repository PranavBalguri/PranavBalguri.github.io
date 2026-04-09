-- ============================================================
-- Query 06: Budget Adherence by Genre
-- Business Question: Which genres consistently overspend
--                    and should inform future budgeting?
-- ============================================================

WITH genre_pnl AS (
    SELECT
        genre,
        year,
        COUNT(production_id)                            AS production_count,
        SUM(budget_gbp)                                 AS total_budget,
        SUM(actual_spend_gbp)                           AS total_actual,
        SUM(actual_spend_gbp - budget_gbp)              AS total_variance,
        ROUND(AVG(
            (actual_spend_gbp - budget_gbp)
            * 100.0 / budget_gbp
        ), 1)                                           AS avg_variance_pct,
        SUM(CASE
            WHEN actual_spend_gbp > budget_gbp
            THEN 1 ELSE 0
        END)                                            AS over_budget_count,
        ROUND(AVG(budget_gbp), 0)                       AS avg_budget_per_production,
        ROUND(AVG(actual_spend_gbp), 0)                 AS avg_actual_per_production
    FROM raw_productions
    GROUP BY genre, year
),

genre_overall AS (
    SELECT
        genre,
        SUM(production_count)                           AS total_productions,
        SUM(total_budget)                               AS lifetime_budget,
        SUM(total_actual)                               AS lifetime_actual,
        SUM(total_variance)                             AS lifetime_variance,
        ROUND(AVG(avg_variance_pct), 1)                 AS overall_avg_variance_pct,
        SUM(over_budget_count)                          AS total_over_budget,
        ROUND(
            SUM(over_budget_count) * 100.0
            / SUM(production_count)
        , 1)                                            AS over_budget_rate_pct
    FROM genre_pnl
    GROUP BY genre
)

SELECT
    go.genre,
    go.total_productions,
    go.lifetime_budget,
    go.lifetime_actual,
    go.lifetime_variance,
    go.overall_avg_variance_pct,
    go.total_over_budget,
    go.over_budget_rate_pct,

    -- Risk classification
    CASE
        WHEN go.overall_avg_variance_pct > 5
            THEN 'HIGH RISK — Consistently overspends'
        WHEN go.overall_avg_variance_pct > 0
            THEN 'MEDIUM RISK — Slight overspend tendency'
        ELSE 'LOW RISK — Good budget adherence'
    END                                                 AS budget_risk_level,

    -- Rank genres by overspend risk
    RANK() OVER (
        ORDER BY go.overall_avg_variance_pct DESC
    )                                                   AS overspend_risk_rank

FROM genre_overall go
ORDER BY go.overall_avg_variance_pct DESC
