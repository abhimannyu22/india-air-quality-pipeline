-- severity warn: a stopped station is worth knowing about, but shouldn't fail the build
{{ config(severity='warn') }}
select * from {{ ref('dim_station') }}
where not is_active