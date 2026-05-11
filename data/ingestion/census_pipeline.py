"""
Census ACS 2024 - Complete Variable Pull
Political Intelligence Platform
Covers every demographic dimension needed for district-level political analysis
"""

import requests
import pandas as pd
import time

# ── CONFIG ───────────────────────────────────────────────────────
API_KEY = "YOUR_CENSUS_API_KEY"  # api.census.gov/data/key_signup.html
BASE_URL = "https://api.census.gov/data/2024/acs/acs5"

# ─────────────────────────────────────────────────────────────────
# VARIABLE GROUPS
# Census API allows max ~50 variables per call
# We split into multiple calls then merge on district_id
# ─────────────────────────────────────────────────────────────────

CALL_1_POPULATION_AGE = {
    "NAME":          "district_name",
    "B01003_001E":   "total_population",
    "B01002_001E":   "median_age",
    "B01002_002E":   "median_age_male",
    "B01002_003E":   "median_age_female",
    # Age buckets
    "B01001_007E":   "male_18_19",
    "B01001_008E":   "male_20",
    "B01001_009E":   "male_21",
    "B01001_010E":   "male_22_24",
    "B01001_011E":   "male_25_29",
    "B01001_012E":   "male_30_34",
    "B01001_019E":   "male_55_59",
    "B01001_020E":   "male_60_61",
    "B01001_021E":   "male_62_64",
    "B01001_022E":   "male_65_66",
    "B01001_023E":   "male_67_69",
    "B01001_024E":   "male_70_74",
    "B01001_025E":   "male_75_79",
    "B01001_026E":   "male_80_84",
    "B01001_027E":   "male_85_plus",
    "B01001_031E":   "female_18_19",
    "B01001_032E":   "female_20",
    "B01001_033E":   "female_21",
    "B01001_034E":   "female_22_24",
    "B01001_035E":   "female_25_29",
}

CALL_2_RACE_ETHNICITY = {
    # Race
    "B02001_001E":   "race_total_pop",
    "B02001_002E":   "white_alone",
    "B02001_003E":   "black_alone",
    "B02001_004E":   "native_american_alone",
    "B02001_005E":   "asian_alone",
    "B02001_006E":   "pacific_islander_alone",
    "B02001_007E":   "other_race_alone",
    "B02001_008E":   "two_or_more_races",
    # Hispanic
    "B03001_001E":   "hispanic_total_base",
    "B03001_003E":   "hispanic_latino_total",
    "B03001_004E":   "mexican",
    "B03001_005E":   "puerto_rican",
    "B03001_006E":   "cuban",
    "B03001_008E":   "central_american",
    "B03001_009E":   "south_american",
    # White non-Hispanic (key political segment)
    "B03002_003E":   "white_non_hispanic",
    "B03002_004E":   "black_non_hispanic",
    "B03002_012E":   "hispanic_any_race",
}

CALL_3_INCOME_POVERTY = {
    # Income
    "B19013_001E":   "median_household_income",
    "B19025_001E":   "aggregate_household_income",
    "B19301_001E":   "per_capita_income",
    "B19083_001E":   "gini_index",
    # Income brackets
    "B19001_002E":   "income_under_10k",
    "B19001_003E":   "income_10k_15k",
    "B19001_004E":   "income_15k_20k",
    "B19001_005E":   "income_20k_25k",
    "B19001_006E":   "income_25k_30k",
    "B19001_007E":   "income_30k_35k",
    "B19001_008E":   "income_35k_40k",
    "B19001_009E":   "income_40k_45k",
    "B19001_010E":   "income_45k_50k",
    "B19001_011E":   "income_50k_60k",
    "B19001_012E":   "income_60k_75k",
    "B19001_013E":   "income_75k_100k",
    "B19001_014E":   "income_100k_125k",
    "B19001_015E":   "income_125k_150k",
    "B19001_016E":   "income_150k_200k",
    "B19001_017E":   "income_over_200k",
    # Poverty
    "B17001_001E":   "poverty_base_pop",
    "B17001_002E":   "population_below_poverty",
    "B17001_031E":   "female_below_poverty",
    "B17001_015E":   "male_below_poverty",
    # SNAP / Food stamps
    "B22003_002E":   "households_with_snap",
    "B22003_001E":   "snap_base_households",
}

CALL_4_EDUCATION = {
    "B15003_001E":   "education_base_pop",
    "B15003_002E":   "no_schooling",
    "B15003_011E":   "grade_8_or_less",
    "B15003_014E":   "some_high_school",
    "B15003_017E":   "high_school_diploma",
    "B15003_018E":   "ged_alternative",
    "B15003_019E":   "some_college_less_1yr",
    "B15003_020E":   "some_college_more_1yr",
    "B15003_021E":   "associates_degree",
    "B15003_022E":   "bachelors_degree",
    "B15003_023E":   "masters_degree",
    "B15003_024E":   "professional_degree",
    "B15003_025E":   "doctorate_degree",
    # School enrollment
    "B14001_001E":   "school_enrollment_base",
    "B14001_002E":   "enrolled_in_school",
    "B14001_008E":   "enrolled_college_grad",
    # Student loans proxy
    "B15011_001E":   "bachelors_plus_by_sex_base",
}

CALL_5_EMPLOYMENT_INDUSTRY = {
    # Employment status
    "B23025_001E":   "employment_base_pop",
    "B23025_002E":   "in_labor_force",
    "B23025_003E":   "civilian_labor_force",
    "B23025_004E":   "employed_civilian",
    "B23025_005E":   "unemployed",
    "B23025_006E":   "armed_forces",
    "B23025_007E":   "not_in_labor_force",
    # Industry (what people work in — crucial for issue detection)
    "C24050_001E":   "industry_base",
    "C24050_002E":   "agriculture_forestry_fishing",
    "C24050_003E":   "construction",
    "C24050_004E":   "manufacturing",
    "C24050_005E":   "wholesale_trade",
    "C24050_006E":   "retail_trade",
    "C24050_007E":   "transportation_warehousing",
    "C24050_008E":   "information",
    "C24050_009E":   "finance_insurance_real_estate",
    "C24050_010E":   "professional_scientific",
    "C24050_011E":   "educational_health_social",
    "C24050_012E":   "arts_entertainment_recreation",
    "C24050_013E":   "public_administration",
    # Class of worker
    "B24080_002E":   "private_wage_workers",
    "B24080_006E":   "government_workers",
    "B24080_007E":   "self_employed",
}

CALL_6_HOUSING = {
    # Housing overview
    "B25001_001E":   "total_housing_units",
    "B25002_002E":   "occupied_units",
    "B25002_003E":   "vacant_units",
    "B25003_002E":   "owner_occupied",
    "B25003_003E":   "renter_occupied",
    # Home values
    "B25077_001E":   "median_home_value",
    "B25064_001E":   "median_gross_rent",
    "B25071_001E":   "median_rent_as_pct_income",
    # Mortgage burden
    "B25091_008E":   "mortgage_30_35pct_income",
    "B25091_009E":   "mortgage_35_40pct_income",
    "B25091_010E":   "mortgage_40_50pct_income",
    "B25091_011E":   "mortgage_over_50pct_income",
    # Housing year built (older housing = infrastructure issues)
    "B25035_001E":   "median_year_structure_built",
    # Overcrowding
    "B25014_005E":   "owner_overcrowded",
    "B25014_011E":   "renter_overcrowded",
}

CALL_7_HEALTH_SOCIAL = {
    # Health insurance
    "B27001_001E":   "health_insurance_base",
    "B27001_005E":   "male_19_25_no_insurance",
    "B27001_008E":   "male_26_34_no_insurance",
    "B27001_011E":   "male_35_44_no_insurance",
    "B27001_014E":   "male_45_54_no_insurance",
    "B27001_017E":   "male_55_64_no_insurance",
    "B27001_033E":   "female_19_25_no_insurance",
    "B27001_036E":   "female_26_34_no_insurance",
    "B27001_039E":   "female_35_44_no_insurance",
    "B27001_042E":   "female_45_54_no_insurance",
    "B27001_045E":   "female_55_64_no_insurance",
    # Disability
    "B18101_001E":   "disability_base",
    "B18101_004E":   "male_under_18_disability",
    "B18101_023E":   "female_under_18_disability",
    "B18101_016E":   "male_65_74_disability",
    "B18101_035E":   "female_65_74_disability",
    # Single parent households
    "B11001_006E":   "female_householder_no_spouse",
    "B11001_005E":   "male_householder_no_spouse",
    "B11001_001E":   "household_type_base",
}

CALL_8_IMMIGRATION_CITIZENSHIP = {
    # Citizenship status
    "B05001_001E":   "citizenship_base",
    "B05001_002E":   "born_in_us",
    "B05001_003E":   "born_in_us_territory",
    "B05001_004E":   "born_abroad_us_parent",
    "B05001_005E":   "naturalized_citizen",
    "B05001_006E":   "not_a_citizen",
    # Place of birth
    "B05002_001E":   "place_of_birth_base",
    "B05002_002E":   "born_in_us_state",
    "B05002_013E":   "foreign_born",
    # Language spoken at home
    "B16001_001E":   "language_base",
    "B16001_002E":   "speaks_english_only",
    "B16001_003E":   "speaks_spanish",
    "B16001_006E":   "speaks_other_indo_european",
    "B16001_009E":   "speaks_asian_pacific",
    # English proficiency
    "B16004_001E":   "english_proficiency_base",
    "B16004_003E":   "speaks_english_very_well",
    "B16004_005E":   "speaks_english_not_well",
    "B16004_006E":   "speaks_english_not_at_all",
    # Year of entry
    "B05005_002E":   "entered_2010_or_later",
    "B05005_003E":   "entered_2000_2009",
}

# ── FIX: Replaced invalid B21007_003E with correct B21001_002E (veterans_total)
#         and B21007_001E with B21001_001E (veteran_base_18plus).
#         Veteran poverty now uses B17001_040E (females below poverty, approximated)
#         via the correct poverty table B21100 or simply omitted as unavailable at CD level.
#         Using B21001 series for the core veteran counts (always available).
#         For veteran poverty: B21100_004E = veterans below poverty (ACS table, CD level).
CALL_9_VETERANS_MILITARY = {
    # Veterans — core counts (B21001 is available for congressional districts)
    "B21001_001E":   "veteran_base_18plus",
    "B21001_002E":   "veterans_total",
    "B21001_003E":   "nonveterans",
    "B21001_005E":   "male_veterans",
    "B21001_023E":   "female_veterans",
    # Veterans by period of service
    "B21002_002E":   "gulf_war_2001_later",
    "B21002_003E":   "gulf_war_2001_later_also_gulf90",
    "B21002_005E":   "gulf_war_1990_2001",
    "B21002_007E":   "vietnam_war_veterans",
    "B21002_009E":   "korean_war_veterans",
    "B21002_011E":   "wwii_veterans",
    # FIX: Veteran poverty — B21100_004E is the correct CD-level variable
    #      (Veterans for whom poverty status determined — below poverty)
    "B21100_004E":   "veterans_below_poverty",
    "B21100_001E":   "veteran_poverty_base",
    # Veteran employment
    "B21005_002E":   "veterans_18_64_employed",
    "B21005_004E":   "veterans_18_64_unemployed",
    "B21005_001E":   "veterans_employment_base",
}

CALL_10_INTERNET_TECH_TRANSPORT = {
    # Internet access
    "B28002_001E":   "internet_base",
    "B28002_002E":   "has_internet_subscription",
    "B28002_004E":   "has_broadband",
    "B28002_013E":   "no_internet_access",
    # Computer access
    "B28001_001E":   "computer_base",
    "B28001_002E":   "has_computer",
    "B28001_011E":   "no_computer",
    # Commute / transportation
    "B08301_001E":   "commute_base",
    "B08301_003E":   "drives_alone",
    "B08301_004E":   "carpools",
    "B08301_010E":   "public_transport",
    "B08301_019E":   "works_from_home",
    "B08301_021E":   "walks_to_work",
    # Commute time
    "B08303_001E":   "commute_time_base",
    "B08303_012E":   "commute_60_89min",
    "B08303_013E":   "commute_90min_plus",
    # Vehicles
    "B25044_003E":   "owner_no_vehicle",
    "B25044_010E":   "renter_no_vehicle",
}


STATE_FIPS = {
    "01":"AL","02":"AK","04":"AZ","05":"AR","06":"CA","08":"CO","09":"CT",
    "10":"DE","12":"FL","13":"GA","15":"HI","16":"ID","17":"IL","18":"IN",
    "19":"IA","20":"KS","21":"KY","22":"LA","23":"ME","24":"MD","25":"MA",
    "26":"MI","27":"MN","28":"MS","29":"MO","30":"MT","31":"NE","32":"NV",
    "33":"NH","34":"NJ","35":"NM","36":"NY","37":"NC","38":"ND","39":"OH",
    "40":"OK","41":"OR","42":"PA","44":"RI","45":"SC","46":"SD","47":"TN",
    "48":"TX","49":"UT","50":"VT","51":"VA","53":"WA","54":"WV","55":"WI",
    "56":"WY"
}

def safe_div(numerator, denominator, scale=1):
    """Safe division that returns NaN instead of errors, avoids div-by-zero."""
    denom = denominator.replace(0, float("nan"))
    return (numerator / denom * scale).round(2)

def pull_variables(var_dict, state="*", label=""):
    """Pull one group of variables from Census API"""
    variables = "NAME," + ",".join(var_dict.keys())
    params = {
        "get": variables,
        "for": "congressional district:*",
        "in": f"state:{state}",
        # "key": API_KEY   # uncomment when you have your key
    }
    print(f"  Pulling {label} ({len(var_dict)} variables)...")
    resp = requests.get(BASE_URL, params=params, timeout=30)
    if resp.status_code != 200:
        print(f"  ERROR {resp.status_code}: {resp.text[:200]}")
        return None
    raw = resp.json()
    df = pd.DataFrame(raw[1:], columns=raw[0])
    df = df.rename(columns=var_dict)
    # Convert to numeric
    for col in var_dict.values():
        if col in df.columns and col != "district_name":
            df[col] = pd.to_numeric(df[col], errors="coerce")
    time.sleep(1)   # be polite to Census API
    return df


def merge_calls(dfs):
    """Merge all variable groups on state + district"""
    base = dfs[0]
    for df in dfs[1:]:
        # Exclude join keys from cols_to_merge to prevent duplication
        cols_to_merge = [c for c in df.columns
                         if c not in base.columns
                         and c not in ["state", "congressional district"]]
        base = base.merge(
            df[["state", "congressional district"] + cols_to_merge],
            on=["state", "congressional district"],
            how="left"
        )
    return base


def col(df, name, fallback=0):
    """Safely retrieve a column, returning a zero Series if missing."""
    if name in df.columns:
        return df[name]
    print(f"  [WARN] Column '{name}' not found — substituting {fallback}")
    return pd.Series(fallback, index=df.index, dtype=float)


def add_derived_metrics(df):
    """Calculate percentage-based and derived features — fully guarded against missing columns."""
    pop = col(df, "total_population").replace(0, float("nan"))

    # ── Race % ───────────────────────────────────────────────────
    df["white_pct"]              = safe_div(col(df, "white_alone"),            pop, 100)
    df["black_pct"]              = safe_div(col(df, "black_alone"),            pop, 100)
    df["hispanic_pct"]           = safe_div(col(df, "hispanic_latino_total"),  pop, 100)
    df["asian_pct"]              = safe_div(col(df, "asian_alone"),            pop, 100)
    df["native_american_pct"]    = safe_div(col(df, "native_american_alone"),  pop, 100)
    df["white_non_hispanic_pct"] = safe_div(col(df, "white_non_hispanic"),     pop, 100)
    df["minority_pct"]           = (100 - df["white_non_hispanic_pct"]).round(2)

    # ── Age groups % ─────────────────────────────────────────────
    youth_cols = ["male_18_19","male_20","male_21","male_22_24","male_25_29",
                  "female_18_19","female_20","female_21","female_22_24","female_25_29"]
    df["youth_18_29_pct"] = safe_div(
        df[[c for c in youth_cols if c in df.columns]].sum(axis=1), pop, 100)

    senior_cols = ["male_65_66","male_67_69","male_70_74","male_75_79","male_80_84","male_85_plus"]
    df["senior_65plus_pct"] = safe_div(
        df[[c for c in senior_cols if c in df.columns]].sum(axis=1), pop, 100)

    # ── Economic % ───────────────────────────────────────────────
    df["poverty_rate_pct"] = safe_div(
        col(df, "population_below_poverty"), col(df, "poverty_base_pop").replace(0, float("nan")), 100)
    df["unemployment_rate_pct"] = safe_div(
        col(df, "unemployed"), col(df, "civilian_labor_force").replace(0, float("nan")), 100)
    df["labor_force_participation_pct"] = safe_div(
        col(df, "in_labor_force"), col(df, "employment_base_pop").replace(0, float("nan")), 100)
    df["snap_households_pct"] = safe_div(
        col(df, "households_with_snap"), col(df, "snap_base_households").replace(0, float("nan")), 100)

    df["high_inequality"] = (col(df, "gini_index") > 0.45).astype(int)

    income_lower_cols = ["income_under_10k","income_10k_15k","income_15k_20k","income_20k_25k","income_25k_30k"]
    income_middle_cols = ["income_50k_60k","income_60k_75k","income_75k_100k"]
    income_upper_cols = ["income_100k_125k","income_125k_150k","income_150k_200k","income_over_200k"]

    df["lower_income_pct"]  = safe_div(df[[c for c in income_lower_cols  if c in df.columns]].sum(axis=1), pop, 100)
    df["middle_income_pct"] = safe_div(df[[c for c in income_middle_cols if c in df.columns]].sum(axis=1), pop, 100)
    df["upper_income_pct"]  = safe_div(df[[c for c in income_upper_cols  if c in df.columns]].sum(axis=1), pop, 100)

    # ── Education % ──────────────────────────────────────────────
    edu_base = col(df, "education_base_pop").replace(0, float("nan"))
    df["college_grad_pct"]       = safe_div(col(df, "bachelors_degree"), edu_base, 100)
    df["postgrad_pct"]           = safe_div(
        col(df, "masters_degree") + col(df, "doctorate_degree") + col(df, "professional_degree"),
        edu_base, 100)
    df["high_school_or_less_pct"] = safe_div(
        col(df, "high_school_diploma") + col(df, "ged_alternative") + col(df, "no_schooling"),
        edu_base, 100)

    # ── Employment/Industry % ────────────────────────────────────
    industry_base = col(df, "industry_base").replace(0, float("nan"))
    labor_force   = col(df, "in_labor_force").replace(0, float("nan"))
    commute_base  = col(df, "commute_base").replace(0, float("nan"))

    df["manufacturing_pct"]      = safe_div(col(df, "manufacturing"),      industry_base, 100)
    df["government_workers_pct"] = safe_div(col(df, "government_workers"), labor_force,   100)
    df["self_employed_pct"]      = safe_div(col(df, "self_employed"),       labor_force,   100)
    df["work_from_home_pct"]     = safe_div(col(df, "works_from_home"),    commute_base,  100)

    # ── Housing % ────────────────────────────────────────────────
    housing_units  = col(df, "total_housing_units").replace(0, float("nan"))
    owner_occupied = col(df, "owner_occupied").replace(0, float("nan"))

    df["owner_occupied_pct"]  = safe_div(col(df, "owner_occupied"), housing_units, 100)
    df["renter_occupied_pct"] = safe_div(col(df, "renter_occupied"), housing_units, 100)
    df["vacant_housing_pct"]  = safe_div(col(df, "vacant_units"),   housing_units, 100)

    mortgage_burden_cols = ["mortgage_30_35pct_income","mortgage_35_40pct_income",
                            "mortgage_40_50pct_income","mortgage_over_50pct_income"]
    df["housing_cost_burdened_pct"] = safe_div(
        df[[c for c in mortgage_burden_cols if c in df.columns]].sum(axis=1),
        owner_occupied, 100)

    # ── Health % ─────────────────────────────────────────────────
    uninsured_cols = [c for c in df.columns if "no_insurance" in c]
    health_base = col(df, "health_insurance_base").replace(0, float("nan"))
    df["uninsured_pct"]  = safe_div(df[uninsured_cols].sum(axis=1) if uninsured_cols else pd.Series(0, index=df.index), health_base, 100)
    df["disability_pct"] = safe_div(col(df, "disability_base"), pop, 100)

    # ── Veteran % ────────────────────────────────────────────────
    veteran_base   = col(df, "veteran_base_18plus").replace(0, float("nan"))
    veterans_total = col(df, "veterans_total").replace(0, float("nan"))
    vet_pov_base   = col(df, "veteran_poverty_base").replace(0, float("nan"))

    df["veteran_pct"]         = safe_div(col(df, "veterans_total"),        veteran_base, 100)
    df["veteran_poverty_pct"] = safe_div(col(df, "veterans_below_poverty"), vet_pov_base, 100)
    df["female_veteran_pct"]  = safe_div(col(df, "female_veterans"),        veterans_total, 100)

    # ── Immigration % ────────────────────────────────────────────
    citizenship_base    = col(df, "citizenship_base").replace(0, float("nan"))
    eng_prof_base       = col(df, "english_proficiency_base").replace(0, float("nan"))

    df["foreign_born_pct"]    = safe_div(col(df, "foreign_born"),       pop,              100)
    df["non_citizen_pct"]     = safe_div(col(df, "not_a_citizen"),      citizenship_base, 100)
    df["limited_english_pct"] = safe_div(
        col(df, "speaks_english_not_well") + col(df, "speaks_english_not_at_all"),
        eng_prof_base, 100)

    # ── Tech/Internet % ──────────────────────────────────────────
    internet_base = col(df, "internet_base").replace(0, float("nan"))
    computer_base = col(df, "computer_base").replace(0, float("nan"))

    df["no_internet_pct"] = safe_div(col(df, "no_internet_access"), internet_base, 100)
    df["no_computer_pct"] = safe_div(col(df, "no_computer"),        computer_base, 100)
    df["broadband_pct"]   = safe_div(col(df, "has_broadband"),      internet_base, 100)

    # ── Political Composite Indicators ───────────────────────────
    df["working_class_index"] = (
        (df.get("manufacturing_pct",     pd.Series(0, index=df.index)) * 0.4) +
        (df.get("high_school_or_less_pct", pd.Series(0, index=df.index)) * 0.3) +
        (df.get("lower_income_pct",      pd.Series(0, index=df.index)) * 0.3)
    ).round(2)

    df["college_town_index"] = (
        (df.get("college_grad_pct",  pd.Series(0, index=df.index)) * 0.5) +
        (df.get("youth_18_29_pct",   pd.Series(0, index=df.index)) * 0.3) +
        (safe_div(col(df, "enrolled_in_school"), pop, 100) * 0.2)
    ).round(2)

    gulf_war_recent = col(df, "gulf_war_2001_later")
    df["military_community_index"] = (
        (df.get("veteran_pct",           pd.Series(0, index=df.index)) * 0.5) +
        (df.get("government_workers_pct", pd.Series(0, index=df.index)) * 0.3) +
        (safe_div(gulf_war_recent, veterans_total, 100) * 0.2)
    ).round(2)

    df["diversity_index"] = (
        (df.get("minority_pct",      pd.Series(0, index=df.index)) * 0.5) +
        (df.get("foreign_born_pct",  pd.Series(0, index=df.index)) * 0.3) +
        (df.get("limited_english_pct", pd.Series(0, index=df.index)) * 0.2)
    ).round(2)

    df["economic_anxiety_index"] = (
        (df.get("unemployment_rate_pct",      pd.Series(0, index=df.index)) * 0.30) +
        (df.get("poverty_rate_pct",           pd.Series(0, index=df.index)) * 0.25) +
        (df.get("snap_households_pct",        pd.Series(0, index=df.index)) * 0.20) +
        (df.get("housing_cost_burdened_pct",  pd.Series(0, index=df.index)).fillna(0) * 0.25)
    ).round(2)

    return df


def clean_district_id(df):
    """Create clean AZ-06 style district IDs"""
    df["state_abbr"]  = df["state"].map(STATE_FIPS)
    df["district_id"] = df["state_abbr"] + "-" + df["congressional district"].str.zfill(2)
    return df


# ── MAIN PULL ─────────────────────────────────────────────────────

def pull_all_districts(state="*"):
    print(f"\nPulling ACS 2024 5-Year for {'all states' if state=='*' else 'state '+state}")
    print("="*60)

    calls = [
        (CALL_1_POPULATION_AGE,          "Population & Age"),
        (CALL_2_RACE_ETHNICITY,           "Race & Ethnicity"),
        (CALL_3_INCOME_POVERTY,           "Income & Poverty"),
        (CALL_4_EDUCATION,                "Education"),
        (CALL_5_EMPLOYMENT_INDUSTRY,      "Employment & Industry"),
        (CALL_6_HOUSING,                  "Housing"),
        (CALL_7_HEALTH_SOCIAL,            "Health & Social"),
        (CALL_8_IMMIGRATION_CITIZENSHIP,  "Immigration & Citizenship"),
        (CALL_9_VETERANS_MILITARY,        "Veterans & Military"),
        (CALL_10_INTERNET_TECH_TRANSPORT, "Internet, Tech & Transport"),
    ]

    dfs = []
    for var_dict, label in calls:
        df = pull_variables(var_dict, state=state, label=label)
        if df is not None:
            dfs.append(df)
        else:
            print(f"  [SKIP] {label} failed — will proceed without it")

    if not dfs:
        raise RuntimeError("All API calls failed. Check your internet connection or API key.")

    print("\nMerging all variable groups...")
    merged = merge_calls(dfs)

    print("Cleaning district IDs...")
    merged = clean_district_id(merged)

    print("Calculating derived metrics...")
    merged = add_derived_metrics(merged)

    print(f"\nDone. Total districts: {len(merged)}")
    print(f"Total columns: {len(merged.columns)}")
    return merged


if __name__ == "__main__":
    # Pull all 435 districts
    df = pull_all_districts(state="*")

    # Preview
    preview_cols = [
        "district_id", "district_name", "total_population",
        "median_household_income", "poverty_rate_pct",
        "unemployment_rate_pct", "college_grad_pct",
        "hispanic_pct", "black_pct", "white_non_hispanic_pct",
        "veteran_pct", "uninsured_pct", "foreign_born_pct",
        "economic_anxiety_index", "working_class_index",
        "military_community_index", "diversity_index"
    ]
    print("\n=== SAMPLE OUTPUT ===")
    print(df[[c for c in preview_cols if c in df.columns]].head(10).to_string())

    # Save
    df.to_csv("census_2024_all_districts.csv", index=False)
    print(f"\nSaved: census_2024_all_districts.csv")
    print(f"Shape: {df.shape}")
    print(f"Columns: {sorted(df.columns.tolist())}")