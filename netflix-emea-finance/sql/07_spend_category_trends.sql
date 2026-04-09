-- ============================================================
-- Query 07: Spend Category Trend Analysis
-- Business Question: Which spend categories are growing
--                    fastest and where should we focus cost control?
-- ============================================================

WITH monthly_spend AS (
    SELECT
        s.spend_category,
        LEFT(s.month, 4)                                AS spend_year,
        LEFT(s.month, 7)                                AS spend_month,
        v.market,
        SUM(s.spend_gbp)                                AS monthly_spend_gbp,
        COUNT(s.spend_id)                               AS invoice_count
    FROM raw_spend s
    LEFT JOIN raw_vendors v
        ON s.vendor_id = v.vendor_id
    GROUP BY
        s.spend_category,
        LEFT(s.month, 4),
        LEFT(s.month, 7),
        v.market
),

annual_category AS (
    SELECT
        spend_category,
        spend_year,
        SUM(monthly_spend_gbp)                          AS annual_spend_gbp,
        SUM(invoice_count)                              AS annual_invoices,
        COUNT(DISTINCT spend_month)                     AS active_months
    FROM monthly_spend
    GROUP BY spend_category, spend_year
),

category_yoy AS (
    SELECT
        spend_category,
        spend_year,
        annual_spend_gbp,
        annual_invoices,
        LAG(annual_spend_gbp) OVER (
            PARTITION BY spend_category
            ORDER BY spend_year
        )                                               AS prior_year_spend,
        -- Running total across years
        SUM(annual_spend_gbp) OVER (
            PARTITION BY spend_category
            ORDER BY spend_year
            ROWS BETWEEN UNBOUNDED PRECEDING
            AND CURRENT ROW
        )                                               AS cumulative_spend_gbp
    FROM annual_category
),

grand_total_by_year AS (
    SELECT
        spend_year,
        SUM(annual_spend_gbp)                           AS year_total
    FROM annual_category
    GROUP BY spend_year
)

SELECT
    cy.spend_category,
    cy.spend_year,
    cy.annual_spend_gbp,
    cy.annual_invoices,
    cy.prior_year_spend,
    cy.cumulative_spend_gbp,

    -- YoY growth
    CASE
        WHEN cy.prior_year_spend IS NULL THEN NULL
        ELSE ROUND(
            (cy.annual_spend_gbp - cy.prior_year_spend)
            * 100.0 / cy.prior_year_spend
        , 1)
    END                                                 AS yoy_growth_pct,

    -- Share of total spend that year
    ROUND(
        cy.annual_spend_gbp * 100.0
        / gt.year_total
    , 1)                                                AS pct_of_year_spend,

    -- Rank by spend within year
    RANK() OVER (
        PARTITION BY cy.spend_year
        ORDER BY cy.annual_spend_gbp DESC
    )                                                   AS category_rank_by_year

FROM category_yoy cy
LEFT JOIN grand_total_by_year gt
    ON cy.spend_year = gt.spend_year
ORDER BY cy.spend_category, cy.spend_year
