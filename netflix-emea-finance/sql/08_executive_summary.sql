-- ============================================================
-- Query 08: EMEA Executive Summary
-- Business Question: What is the single-page summary a
--                    senior stakeholder needs every week?
-- ============================================================

WITH production_summary AS (
    SELECT
        market,
        year,
        COUNT(production_id)                            AS total_productions,
        SUM(CASE WHEN status = 'completed'
            THEN 1 ELSE 0 END)                          AS completed,
        SUM(CASE WHEN status = 'in_production'
            THEN 1 ELSE 0 END)                          AS in_production,
        SUM(budget_gbp)                                 AS total_budget,
        SUM(actual_spend_gbp)                           AS total_actual_spend,
        SUM(actual_spend_gbp - budget_gbp)              AS total_variance,
        ROUND(AVG(
            (actual_spend_gbp - budget_gbp)
            * 100.0 / budget_gbp
        ), 1)                                           AS avg_variance_pct,
        SUM(CASE WHEN actual_spend_gbp > budget_gbp
            THEN 1 ELSE 0 END)                          AS over_budget_count
    FROM raw_productions
    GROUP BY market, year
),

jobs_summary AS (
    SELECT
        market,
        p.year,
        SUM(h.direct_jobs + h.indirect_jobs)            AS total_jobs,
        SUM(h.direct_jobs)                              AS direct_jobs,
        SUM(h.crew_days)                                AS total_crew_days
    FROM raw_headcount h
    LEFT JOIN raw_productions p
        ON h.production_id = p.production_id
    GROUP BY market, p.year
),

vendor_summary AS (
    SELECT
        v.market,
        CAST(LEFT(s.month, 4) AS INTEGER)               AS year,
        SUM(s.spend_gbp)                                AS total_vendor_spend,
        COUNT(DISTINCT s.vendor_id)                     AS unique_vendors
    FROM raw_spend s
    LEFT JOIN raw_vendors v ON s.vendor_id = v.vendor_id
    GROUP BY v.market, CAST(LEFT(s.month, 4) AS INTEGER)
)

SELECT
    ps.market,
    ps.year,

    -- Production metrics
    ps.total_productions,
    ps.completed,
    ps.in_production,

    -- Financial metrics
    ps.total_budget,
    ps.total_actual_spend,
    ps.total_variance,
    ps.avg_variance_pct,
    ps.over_budget_count,

    -- Jobs metrics
    js.total_jobs,
    js.direct_jobs,
    js.total_crew_days,

    -- Vendor metrics
    vs.total_vendor_spend,
    vs.unique_vendors,

    -- Derived KPIs
    ROUND(
        ps.total_actual_spend * 1.0
        / NULLIF(js.total_jobs, 0)
    , 0)                                                AS spend_per_job_gbp,

    ROUND(
        js.total_jobs * 1.0
        / NULLIF(ps.total_actual_spend / 1000000.0, 0)
    , 1)                                                AS jobs_per_million_gbp,

    -- Market health score (simple composite)
    CASE
        WHEN ps.avg_variance_pct <= 0 AND ps.over_budget_count = 0
            THEN 'GREEN — On track'
        WHEN ps.avg_variance_pct <= 5
            THEN 'AMBER — Monitor'
        ELSE 'RED — Action required'
    END                                                 AS market_health

FROM production_summary ps
LEFT JOIN jobs_summary js
    ON ps.market = js.market AND ps.year = js.year
LEFT JOIN vendor_summary vs
    ON ps.market = vs.market AND ps.year = vs.year
ORDER BY ps.year, ps.total_actual_spend DESC
