# Data Sources, KG Architecture & Key Indicators
## Political Intelligence Platform — Data Strategy Document

---

## 1. KG Architecture — Three-Layer Design

```
┌─────────────────────────────────────────┐
│         NATIONAL KG (Layer 1)           │
│  Country-level context                  │
│  Wars, economy, president approval      │
│  National issues, party standings       │
│  Major events affecting all districts   │
└──────────────────┬──────────────────────┘
                   │ feeds into
┌──────────────────▼──────────────────────┐
│         STATE KG (Layer 2)              │
│  State-level context                    │
│  Governor, state legislature            │
│  State-specific issues                  │
│  Swing state indicators                 │
└──────────────────┬──────────────────────┘
                   │ feeds into
┌──────────────────▼──────────────────────┐
│        DISTRICT KG (Layer 3)            │
│  District-level intelligence            │
│  Incumbent data, local issues           │
│  Gerrymandering score                   │
│  Historical voting (20 years)           │
│  Demographics + sentiment               │
└─────────────────────────────────────────┘
```

### Why Three Layers?

```
National event (e.g., US enters conflict abroad)
        ↓
Affects ALL districts — captured in National KG
        ↓
Hits swing states harder — State KG weights it
        ↓
In veteran-heavy districts — District KG amplifies it
        ↓
Model sees full causal chain — explainable prediction
```

This is your biggest architectural contribution.
No existing public model explicitly models this cascade.

---

## 2. Key Static Indicators — Build These First

These are your foundational node properties and relationships.
Every district KG node must have all of these before anything else.

### 2.1 Incumbent Indicators
```
Is there an incumbent running?          (boolean)
Incumbent party                         (R/D/I)
Incumbent approval rating               (0-100)
Incumbent years in office               (integer)
Incumbent fundraising total (FEC)       (dollars)
Incumbent key votes (for/against)       (list)
Incumbent scandal flags                 (boolean)
Challenger quality score                (weak/strong/wave)
Open seat?                              (boolean — no incumbent)
```

> Open seats are the most volatile — weight these heavily in your model.
> Incumbents win 90%+ of the time. Open seats flip 3x more often.

### 2.2 Swing Indicators
```
Cook Political Report rating            (Safe R → Toss-up → Safe D)
Sabato Crystal Ball rating              (same scale)
Dave's Redistricting competitiveness    (0-100 score)
Past 3 election margin average          (percentage)
Margin trend direction                  (narrowing/widening)
Presidential vs midterm swing delta     (how much it changes)
Ticket splitting rate                   (voters who split R/D)
```

### 2.3 Gerrymandering Indicators
```
PlanScore partisan bias score           (-1 to +1)
Princeton Gerrymandering grade          (A-F)
Last redistricting year                 (2021/2022 most recent)
Who controlled redistricting            (R legislature/D legislature/court)
District compactness score              (geometric measure)
Population deviation %                  (how equal are districts)
Legal challenges filed?                 (boolean)
```

### 2.4 Historical Voting (20 Years)
```
Presidential results 2004-2024          (R%, D%, margin)
House results 2004-2024                 (R%, D%, margin)
Midterm vs presidential turnout delta   (percentage)
Average R margin last 5 cycles          (percentage)
Trend direction                         (redder/bluer/stable)
Wave election behavior                  (did it flip in 2010/2018?)
```

### 2.5 War & Foreign Policy Indicators
```
Active conflict period flag             (boolean, which conflict)
Veteran population %                    (Census)
Active military base in district        (boolean)
Defense contractor employment %         (Bureau of Labor Stats)
Gold Star family concentration          (proxy: veteran orgs density)
Casualty impact index                   (if available)
Foreign policy salience score           (from news volume)
```

> War effects are asymmetric:
> - Veteran-heavy districts: foreign policy matters 3x more
> - Urban districts: war matters less than economy
> Your KG captures this via district-demographic relationships

### 2.6 Economic Indicators
```
Unemployment rate                       (BLS API)
Median household income                 (Census)
Income growth/decline trend             (year over year)
Industry concentration                  (manufacturing/tech/agriculture)
Union membership %                      (BLS)
Cost of living index                    (BLS CPI by metro)
Recent major layoffs                    (news scraping)
Small business density                  (Census Business Patterns)
```

### 2.7 Demographic Indicators
```
Total population                        (Census)
Age distribution (18-34, 35-54, 55+)   (Census)
Race/ethnicity breakdown                (Census)
Education level (college grad %)        (Census)
Urban/suburban/rural classification     (Census)
Population growth rate                  (Census)
Foreign born %                          (Census)
Religious affiliation (proxy)           (PRRI data)
```

### 2.8 Issue Salience Indicators (Static Baseline)
```
Healthcare concern score                (from survey data)
Immigration concern score               (from survey data)
Economy/inflation concern score         (from survey data)
Education concern score                 (from survey data)
Crime/safety concern score              (from survey data)
Climate concern score                   (from survey data)
Gun policy concern score                (from survey data)
```

---

## 3. Static Phase — All Data Sources

### 3.1 Election & Political Data

| Source | What to Scrape/Pull | Method | Free? |
|---|---|---|---|
| **MIT Election Lab** | House results 2000-2024 by district | Direct download CSV | ✅ |
| **Harvard Dataverse** | Historical election datasets | Direct download | ✅ |
| **FEC API** | Campaign finance by candidate/district | REST API | ✅ |
| **Ballotpedia** | Candidate bios, race ratings, incumbents | Web scrape + API | ✅ |
| **Congress.gov API** | Voting records, bills sponsored | REST API key (free) | ✅ |
| **GovTrack** | Legislator scores, voting records | Web scrape + data downloads | ✅ |
| **VoteSmart** | Candidate positions on issues | Web scrape | ✅ |
| **OpenSecrets** | PAC funding, dark money | Web scrape | ✅ |
| **Wikipedia** | Historical election results pages | Web scrape | ✅ |

### 3.2 Swing / Competitiveness Ratings

| Source | What to Pull | Method | Free? |
|---|---|---|---|
| **Cook Political Report** | Race ratings by district | Web scrape (HTML table) | ✅ |
| **Sabato's Crystal Ball** | Race ratings | Web scrape | ✅ |
| **Dave's Redistricting** | Competitiveness scores | Web scrape + data export | ✅ |
| **PlanScore** | Gerrymandering scores | API + web scrape | ✅ |
| **Princeton Gerrymandering Project** | District grades | Web scrape | ✅ |
| **FiveThirtyEight data repo** | Historical ratings + polls | GitHub CSV download | ✅ |

```bash
# FiveThirtyEight data — direct download, no scraping needed
git clone https://github.com/fivethirtyeight/data
```

### 3.3 Demographics & Census

| Source | What to Pull | Method | Free? |
|---|---|---|---|
| **US Census ACS 5-Year** | Demographics by district | REST API | ✅ |
| **Census TIGER** | District shapefiles/boundaries | Direct download | ✅ |
| **Census Business Patterns** | Industry employment | REST API | ✅ |
| **BLS API** | Unemployment by county | REST API | ✅ |
| **BEA API** | GDP, income by region | REST API | ✅ |
| **PRRI** | Religious landscape data | Web scrape | ✅ |

```python
# Census API example — get demographics for all congressional districts
import requests

url = "https://api.census.gov/data/2022/acs/acs5"
params = {
    "get": "NAME,B01003_001E,B19013_001E,B15003_022E,B02001_003E",
    # population, median income, bachelor's degree, Black population
    "for": "congressional district:*",
    "in": "state:*",
    "key": "YOUR_FREE_KEY"  # get at api.census.gov/data/key_signup.html
}
data = requests.get(url, params=params).json()
```

### 3.4 War & Military Data

| Source | What to Pull | Method | Free? |
|---|---|---|---|
| **DoD Base Structure Report** | Military bases by state/county | PDF download + parse | ✅ |
| **VA Data** | Veteran population by district | Direct download | ✅ |
| **Defense Contract Database** | Defense jobs by district | USASpending.gov API | ✅ |
| **USASpending.gov API** | Federal spending by district | REST API | ✅ |
| **Casualties data** | Historical war casualties by state | Wikipedia scrape | ✅ |

### 3.5 News (Static Baseline — Historical)

| Source | What to Pull | Method | Free? |
|---|---|---|---|
| **GDELT 2.0** | All political news 2015-present | BigQuery or direct API | ✅ |
| **CommonCrawl** | Full web archive | S3 download | ✅ |
| **Internet Archive** | Historical news pages | API | ✅ |
| **NewsAPI (historical)** | 1 month free historical | REST API | Limited |
| **MediaCloud** | Political media tracking | API | ✅ |

```python
# GDELT — completely free, no key, massive coverage
import requests

url = "https://api.gdeltproject.org/api/v2/doc/doc"
params = {
    "query": "Arizona 4th congressional district healthcare 2024",
    "mode": "artlist",
    "maxrecords": 250,
    "startdatetime": "20240101000000",
    "enddatetime": "20241101000000",
    "format": "json"
}
articles = requests.get(url, params=params).json()
```

### 3.6 Social Media (Static Historical)

| Source | What to Pull | Method | Free? |
|---|---|---|---|
| **Pushshift Reddit** | Historical Reddit posts by subreddit | API + dumps | ✅ |
| **Reddit PRAW** | Current + recent posts | Python library | ✅ |
| **YouTube Data API** | Political video comments | REST API key (free) | ✅ |
| **Twitter Academic** | Historical political tweets | Apply for academic access | ✅ |

### 3.7 Polling Data

| Source | What to Pull | Method | Free? |
|---|---|---|---|
| **FiveThirtyEight polls** | All historical polls by race | GitHub CSV | ✅ |
| **RealClearPolitics** | Poll averages by race | Web scrape | ✅ |
| **Polling USA** | District-level polls | Web scrape | ✅ |

---

## 4. Dynamic Phase — Sources & Strategy

### 4.1 What Changes Weekly

```
Every week your pipelines should update:

National KG:
  ├── President approval rating (Gallup weekly)
  ├── Economic indicators (BLS monthly release)
  ├── Major national events (GDELT)
  ├── Congressional votes (Congress.gov)
  └── National polling averages (FiveThirtyEight)

State KG (Swing States Priority):
  ├── State polling (RCP)
  ├── Governor approval
  ├── State-level news volume by issue
  └── Fundraising updates (FEC quarterly)

District KG:
  ├── Local news sentiment (GDELT filtered by district)
  ├── Reddit discussion volume by issue
  ├── Issue salience scores (updated from news)
  └── Candidate activity + announcements
```

### 4.2 Swing States — Focus List 2026

These get priority in your dynamic phase:
```
Arizona        Pennsylvania    Wisconsin
Georgia        Michigan        Nevada
North Carolina New Hampshire   Minnesota
Florida        Ohio            Virginia
```

For these states: pull data **daily** not weekly.
For safe states: weekly is enough.

### 4.3 Dynamic Data Sources

| Source | Update Frequency | What It Gives | Method |
|---|---|---|---|
| **GDELT 2.0** | Every 15 minutes | All political news | API — no key |
| **NewsAPI** | Daily | Top news by query | REST API |
| **Reddit PRAW** | Daily | Issue discussions | Python library |
| **FEC API** | Quarterly | Fundraising updates | REST API |
| **Congress.gov** | Weekly | New bills and votes | REST API |
| **BLS releases** | Monthly | Jobs, inflation | REST API |
| **Gallup** | Weekly | Presidential approval | Web scrape |
| **RealClearPolitics** | Daily | Poll averages | Web scrape |
| **FiveThirtyEight** | Daily | Forecast updates | Web scrape + GitHub |
| **Google Trends API** | Daily | Issue search volume | pytrends library |
| **YouTube Data API** | Weekly | Political video comments | REST API |

```python
# Google Trends — free, shows what issues people are searching
from pytrends.request import TrendReq

pytrends = TrendReq()
pytrends.build_payload(
    ["healthcare", "inflation", "immigration", "crime"],
    geo="US-AZ",        # Arizona
    timeframe="today 3-m"
)
df = pytrends.interest_over_time()
# Returns weekly search volume per issue per state
# Feed directly into issue salience scores in your KG
```

```python
# Airflow DAG — weekly update pipeline
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

def update_district_kg():
    # 1. Pull new GDELT articles
    # 2. Extract issues via NLP
    # 3. Update issue node weights in Neo4j
    # 4. Run PyKEEN link prediction
    # 5. Add inferred relations to KG
    pass

dag = DAG(
    "weekly_kg_update",
    schedule_interval="@weekly",
    start_date=datetime(2026, 6, 1)
)

update_task = PythonOperator(
    task_id="update_kg",
    python_callable=update_district_kg,
    dag=dag
)
```

### 4.4 Event Detection — What Triggers a KG Update

Not every piece of news warrants a KG update.
Your pipeline should flag events that change district dynamics:

```python
# Event types that trigger KG weight updates
TRIGGER_EVENTS = {
    "economic": [
        "unemployment rate", "inflation report",
        "factory closure", "major layoffs", "plant opening"
    ],
    "political": [
        "candidate drops out", "endorsement",
        "scandal", "debate", "ad campaign launch"
    ],
    "national": [
        "military action", "supreme court ruling",
        "presidential approval drop", "major legislation passed"
    ],
    "local": [
        "district-specific crime surge", "local disaster",
        "school shooting", "healthcare facility closure"
    ]
}

# When detected → update relevant issue node weight in KG
# Example: "factory closure in AZ-07" →
#          Economy issue node weight += 0.15 in AZ-07 district KG
```

---

## 5. Final KG Schema With All Indicators

```cypher
// National level node
CREATE (:National {
    president_approval: 42.3,
    gdp_growth: 2.1,
    inflation_rate: 3.4,
    active_conflicts: ["Ukraine support", "Middle East"],
    national_issue_top3: ["Economy", "Immigration", "Healthcare"],
    updated_at: datetime()
})

// State node
CREATE (:State {
    name: "Arizona",
    code: "AZ",
    governor: "Katie Hobbs",
    governor_party: "Democrat",
    governor_approval: 48.2,
    is_swing_state: true,
    electoral_votes: 11,
    state_legislature_control: "Split",
    last_presidential_result: "Democrat +0.3",
    updated_at: datetime()
})

// District node — full indicators
CREATE (:District {
    id: "AZ-06",
    name: "Arizona 6th Congressional District",
    state: "AZ",

    // Incumbent
    incumbent_name: "Juan Ciscomani",
    incumbent_party: "Republican",
    incumbent_approval: 44.1,
    incumbent_years: 2,
    incumbent_fundraising: 2100000,
    open_seat: false,
    incumbent_scandal: false,

    // Swing indicators
    cook_rating: "Toss-up",
    sabato_rating: "Toss-up",
    competitiveness_score: 0.89,
    avg_margin_3cycles: 1.2,
    margin_trend: "narrowing",

    // Gerrymandering
    gerrymander_score: 0.12,
    princeton_grade: "B",
    redistricted_year: 2022,
    redistricting_control: "Republican legislature",
    district_compactness: 0.61,

    // Historical voting
    presidential_2020: "Democrat +2.1",
    presidential_2016: "Republican +3.4",
    presidential_2012: "Republican +8.2",
    house_2022: "Republican +0.8",
    house_2020: "Republican +5.2",
    avg_r_margin_5cycles: 3.9,
    trend_direction: "bluer",

    // Demographics
    population: 761169,
    median_income: 68420,
    college_grad_pct: 34.2,
    hispanic_pct: 38.1,
    white_pct: 51.3,
    age_median: 38.4,
    urban_pct: 72.1,
    veteran_pct: 9.8,

    // Military/War
    military_base_present: false,
    defense_employment_pct: 4.2,
    veteran_population: 74594,

    // Economic
    unemployment_rate: 4.1,
    income_trend: "declining",
    major_industries: ["Healthcare", "Retail", "Construction"],
    union_membership_pct: 8.3,

    updated_at: datetime()
})

// Issue nodes
CREATE (:Issue {
    name: "Healthcare",
    category: "Domestic",
    national_salience: 72.3,    // % of people who care nationally
    updated_at: datetime()
})

// Key relationships
MATCH (d:District {id: "AZ-06"}), (i:Issue {name: "Healthcare"})
CREATE (d)-[:CONCERNED_ABOUT {
    weight: 0.78,              // how much this district cares
    trend: "increasing",       // growing or shrinking concern
    source: "GDELT+Reddit",
    sentiment: -0.34,          // negative = unhappy with current state
    updated_at: datetime()
}]->(i)
```

---

## 6. What Your Model Actually Predicts

```
Not just: "District X → Republican wins"

But:
"District X — Toss-up leaning Republican (54%)"
  Reason 1: Incumbent has 2yr advantage (KG: incumbent node)
  Reason 2: But margin narrowing — was +8 now +0.8 (KG: historical)
  Reason 3: Healthcare concern surged 34% (KG: issue weight ↑)
  Reason 4: Incumbent voted against ACA expansion (KG: vote relation)
  Reason 5: Similar to FL-26 in 2018 — flipped Democrat (KG: analogy)
  Risk flag: HIGH — issue dynamics moving against incumbent
```

That's a 538 prediction + Cook rating + your KG reasoning chain.
All three together. That's your contribution.

---

## 7. Build Priority Order

```
Week 1-2:   Census + FEC + MIT Election Lab → PostgreSQL
            Build district nodes with all static indicators

Week 3-4:   Historical voting 2004-2024 → KG relationships
            Gerrymandering scores → PlanScore + Princeton scrape
            Incumbent data → Ballotpedia scrape

Week 5-6:   GDELT static pull (2024 news) → issue extraction
            Baseline NLP: sentiment + issue detection per district
            XGBoost baseline model with all indicators

Week 7-8:   Full static KG built for 50 key districts
            Neo4j visualization working
            Basic Streamlit dashboard

Week 9-10:  Add Airflow → weekly GDELT + Reddit pipeline
            Dynamic KG weight updates
            Google Trends integration

Week 11+:   Swing state focus — daily updates
            PyKEEN link prediction layer
            API + full dashboard
```

---

*Data Strategy Document v1.0 — May 2026*