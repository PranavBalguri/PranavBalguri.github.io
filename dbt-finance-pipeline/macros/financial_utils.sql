-- macros/financial_utils.sql
-- Reusable macros for the financial reporting pipeline

{% macro gbp_format(column_name) %}
    '£' || round({{ column_name }}, 2)::varchar
{% endmacro %}


{% macro risk_band_label(score_column) %}
    case
        when {{ score_column }} >= 60 then 'HIGH'
        when {{ score_column }} >= 30 then 'MEDIUM'
        else 'LOW'
    end
{% endmacro %}


{% macro is_business_day(date_column) %}
    case
        when extract('dow' from {{ date_column }}) in (0, 6) then false
        else true
    end
{% endmacro %}


{% macro current_financial_year() %}
    case
        when extract('month' from current_date) >= 4
        then extract('year' from current_date)
        else extract('year' from current_date) - 1
    end
{% endmacro %}
