-- ============================================================
-- Query 05: Jobs Created by EMEA Market
-- Business Question: What is Netflix's employment impact
--                    across EMEA and which markets benefit most?
-- ============================================================

WITH jobs_enriched AS (
    -- Join headcount to productions for full context
    SELECT
        h.production_id,
        p.title,
        p.genre,
        p.year,
        p.quarter,
        p.actual_spend_gbp,
        h.market,
        h.direct_jobs,
        h.indirect_jobs,
        h.direct_jobs + h.indirect_jobs                AS total_jobs,
        h.crew_days
    FROM raw_headcount h
    LEFT JOIN raw_productions p
        ON h.production_id = p.production_id
),

market_jobs_summary AS (
    SELECT
        market,
        year,
        SUM(direct_jobs)                                AS total_direct_jobs,
        SUM(indirect_jobs)                              AS total_indirect_jobs,
        SUM(total_jobs)                                 AS total_jobs,
        SUM(crew_days)                                  AS total_crew_days,
        SUM(actual_spend_gbp)                           AS total_spend_gbp,
        COUNT(production_id)                            AS productions_count,

        -- Efficiency metrics
        ROUND(
            SUM(actual_spend_gbp) * 1.0
            / NULLIF(SUM(total_jobs), 0)
        , 0)                                            AS spend_per_job_gbp,

        ROUND(
            SUM(total_jobs) * 1.0
            / NULLIF(SUM(actual_spend_gbp) / 1000000.0, 0)
        , 1)                                            AS jobs_per_million_spent,

        ROUND(
            SUM(direct_jobs) * 100.0
            / NULLIF(SUM(total_jobs), 0)
        , 1)                                            AS direct_jobs_pct

    FROM jobs_enriched
    GROUP BY market, year
),

yoy_jobs AS (
    SELECT
        *,
        LAG(total_jobs) OVER (
            PARTITION BY market
            ORDER BY year
        )                                               AS prior_year_jobs,
        LAG(total_direct_jobs) OVER (
            PARTITION BY market
            ORDER BY year
        )                                               AS prior_year_direct_jobs
    FROM market_jobs_summary
)

SELECT
    market,
    year,
    total_direct_jobs,
    total_indirect_jobs,
    total_jobs,
    total_crew_days,
    total_spend_gbp,
    productions_count,
    spend_per_job_gbp,
    jobs_per_million_spent,
    direct_jobs_pct,
    prior_year_jobs,

    -- YoY jobs growth
    CASE
        WHEN prior_year_jobs IS NULL THEN NULL
        ELSE ROUND(
            (total_jobs - prior_year_jobs)
            * 100.0 / prior_year_jobs
        , 1)
    END                                                 AS yoy_jobs_growth_pct,

    -- Market ranking by total jobs
    RANK() OVER (
        PARTITION BY year
        ORDER BY total_jobs DESC
    )                                                   AS jobs_rank_by_year

FROM yoy_jobs
ORDER BY year, total_jobs DESC
