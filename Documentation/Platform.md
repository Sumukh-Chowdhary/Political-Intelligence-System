# Political Intelligence & Decision Support Platform
## Full Project Documentation v1.0
> Share this with your teammate. This is your single source of truth.

---

## 1. What We Are Building

A production-grade Political Intelligence Platform that:
- Ingests large-scale structured + unstructured political data
- Builds a hybrid Knowledge Base + Knowledge Graph of districts, issues, candidates
- Tracks how political narratives and voter sentiment evolve over time
- Generates explainable district-level intelligence summaries
- Updates dynamically every week with new events
- Gets evaluated against November 2026 US Midterm real results
- Produces a research paper on KG-grounded explainable political intelligence

### The One-Line Pitch
> "We built a system that understands WHY districts vote the way they do — not just predicts WHO wins — using a dynamic Knowledge Graph that updates with real-world events and explains its reasoning."

---

## 2. Research Direction — Option C (Chosen)

### Why Option C: KG-Grounded Explainability

**Option A** (Temporal KG improving prediction accuracy) risks this reviewer response:
> "Your accuracy improvement is marginal — why use a complex KG?"

**Option C** (KG makes predictions explainable AND accurate) answers that directly:
> "Because without KG, you get a number. With KG, you get a reason."

### The Core Research Argument

```
Black-box ML model:
  Input: 50 demographic features
  Output: "District 7 leans Democrat — 67% confidence"
  Explanation: ❌ None. You trust the model blindly.

Your KG-grounded system:
  Input: Same features + Knowledge Graph
  Output: "District 7 leans Democrat — 67% confidence"
  Explanation: ✅
    "Because:
     - Healthcare concern increased 34% (tracked via KG issue nodes)
     - Incumbent voted against Medicare expansion (KG relation)
     - Hispanic demographic grew 12% — historically health-sensitive (KG)
     - Similar districts FL-09 and TX-28 shifted Democrat on same issue pattern"
```

Same prediction. Completely different value. That's your contribution.

### Research Question (Final)

> "Can a Knowledge Graph-grounded reasoning layer produce more accurate AND
>  explainable district-level political intelligence than black-box ML baselines,
>  when evaluated against real US Midterm election outcomes?"

### What You Compare Against (Baselines)

| Baseline | System | What it represents |
|---|---|---|
| **B1** | XGBoost + demographic features only | Standard ML approach |
| **B2** | Vanilla RAG over news articles | Unstructured retrieval |
| **B3** | FiveThirtyEight / RCP public models | Real-world SOTA comparison |
| **Yours** | KG-grounded explainable system | Your contribution |

Metrics to compare:
- Issue detection accuracy (did you identify the right issues per district?)
- Sentiment tracking accuracy (vs actual polling data)
- Prediction alignment with actual midterm results
- Explainability quality (human evaluation — did the reasons make sense?)

### Why KG Needs to Win — The Argument

KGs are complicated. They're only worth it if they do something simpler systems can't.
Your paper argues three things simpler systems cannot do:

```
1. CONNECTIVITY
   XGBoost sees features independently.
   KG sees: Healthcare issue → impacts → Hispanic demographic →
            concentrated in → District 7 →
            candidate → voted_against → Medicare bill
   That chain of reasoning is impossible without a graph.

2. TEMPORAL TRACKING
   Static ML doesn't know an issue GREW over 3 months.
   Your KG tracks issue node weights changing weekly.
   "Immigration concern in AZ-06 increased 40% in 8 weeks" = KG advantage.

3. TRANSFERABILITY
   When a new district appears, KG can reason by analogy:
   "AZ-06 looks like TX-28 did in 2022 — same issue pattern emerged."
   ML needs retraining. KG reasons from structure.
```

---

## 3. Websites That Make Daily US Political Predictions

These are your real-world comparison targets:

| Website | What They Do | Update Frequency | URL |
|---|---|---|---|
| **FiveThirtyEight** | Probabilistic forecasting, polling aggregation | Daily | fivethirtyeight.com |
| **RealClearPolitics** | Poll aggregation + race ratings | Daily | realclearpolitics.com |
| **Cook Political Report** | Expert race ratings by district | Weekly | cookpolitical.com |
| **Sabato's Crystal Ball** | UVA expert district ratings | Weekly | centerforpolitics.org/crystalball |
| **The Economist** | Statistical election model | Daily pre-election | economist.com/interactive/us-2026-elections |

### How You Compare Against Them in Your Paper

```
These sites give:   "District X — Lean Democrat"
Your system gives:  "District X — Lean Democrat
                     Reason: Healthcare dominates discourse (KG),
                     incumbent approval dropped 12% (sentiment),
                     similar to FL-09 pattern 2022 (graph analogy)"

Accuracy:  Compare your district calls vs their calls vs actual results
Novelty:   They give predictions. You give predictions + explanations + issue tracking.
```

---

## 4. Full Technology Stack

### 4.1 Data Engineering Layer
| Tool | Purpose | Free? |
|---|---|---|
| **Python 3.11** | Core language | ✅ |
| **Apache Airflow** | Pipeline orchestration, weekly updates | ✅ |
| **Pandas / Polars** | Data processing | ✅ |
| **SQLAlchemy** | Database ORM | ✅ |
| **Pydantic** | Data validation | ✅ |
| **Beautiful Soup / Scrapy** | Web scraping | ✅ |
| **PRAW** | Reddit API wrapper | ✅ |
| **Tweepy** | Twitter/X API | ✅ free tier |

### 4.2 Storage Layer
| Tool | Purpose | Free? |
|---|---|---|
| **PostgreSQL** | Structured data — districts, demographics, elections | ✅ |
| **Neo4j** | Knowledge Graph | ✅ free tier |
| **FAISS** | Vector embeddings for semantic search | ✅ |
| **Redis** | Caching API responses | ✅ |

### 4.3 NLP & ML Layer
| Tool | Purpose | Free? |
|---|---|---|
| **HuggingFace Transformers** | BERT-based models | ✅ |
| **spaCy** | Entity extraction, NER | ✅ |
| **BERTopic** | Topic modeling | ✅ |
| **sentence-transformers** | Text embeddings | ✅ |
| **XGBoost / LightGBM** | Baseline ML models | ✅ |
| **SHAP** | Explainability for ML baselines | ✅ |
| **Ollama + Llama3.2** | Local LLM for summarization | ✅ |

### 4.4 Knowledge Graph Layer
| Tool | Purpose | Free? |
|---|---|---|
| **Neo4j** | Graph database | ✅ |
| **PyKEEN** | Knowledge Graph embeddings + link prediction | ✅ |
| **AMIE3** | Rule mining on KG | ✅ |
| **py2neo** | Python-Neo4j connector | ✅ |
| **LangChain** | KG retrieval chains | ✅ |

### 4.5 API Layer
| Tool | Purpose | Free? |
|---|---|---|
| **FastAPI** | REST API framework | ✅ |
| **Uvicorn** | ASGI server | ✅ |
| **Celery** | Background task queue (weekly updates) | ✅ |

### 4.6 Frontend / Dashboard
| Tool | Purpose | Free? |
|---|---|---|
| **Streamlit** | Phase 1 dashboard — fast to build | ✅ |
| **React + Tailwind** | Phase 2 production dashboard | ✅ |
| **Plotly / Recharts** | Interactive charts | ✅ |
| **Leaflet.js** | US district maps | ✅ |
| **Neo4j Bloom** | KG visualization | ✅ |

### 4.7 Production Engineering
| Tool | Purpose | Free? |
|---|---|---|
| **Docker + Docker Compose** | Containerization | ✅ |
| **GitHub Actions** | CI/CD | ✅ |
| **Prometheus + Grafana** | Monitoring | ✅ |
| **Loguru** | Logging | ✅ |

---

## 5. Data Sources — Complete List

### 5.1 Structured Political Data (Free APIs)

| Source | Data | API / Link |
|---|---|---|
| **US Census Bureau** | Demographics by district | api.census.gov |
| **FEC API** | Campaign finance data | api.open.fec.gov/v1 |
| **Congress.gov API** | Bills, votes, legislators | api.congress.gov |
| **BallotPedia** | Candidate info, race data | ballotpedia.org/API |
| **MIT Election Lab** | Historical election results | electionlab.mit.edu/data |
| **OpenStates API** | State legislature data | openstates.org/api/v3 |
| **Google Civic API** | District + representative info | developers.google.com/civic-information |

### 5.2 News & Media Data (Free Tiers)

| Source | Data | API / Link |
|---|---|---|
| **NewsAPI** | 100 req/day free, major news sources | newsapi.org |
| **GDELT Project** | Global news events database, completely free | gdeltproject.org |
| **MediaCloud** | Political media tracking | mediacloud.org |
| **CommonCrawl** | Full web crawl data, free | commoncrawl.org |

> **GDELT is your best friend here** — it's fully free, updated every 15 minutes,
> covers all major US political news, and has a BigQuery interface.

### 5.3 Social Media Data (Free Tiers)

| Source | Data | API / Link |
|---|---|---|
| **Reddit (PRAW)** | Political subreddits (r/politics, r/conservative, state subs) | reddit.com/dev/api |
| **Twitter/X Academic** | Political discourse | developer.twitter.com |
| **YouTube Data API** | Political video comments | developers.google.com/youtube |
| **Pushshift (Reddit archive)** | Historical Reddit data | pushshift.io |

### 5.4 Polling Data (Free)

| Source | Data | Link |
|---|---|---|
| **FiveThirtyEight polls** | Aggregated polls CSV | github.com/fivethirtyeight/data |
| **RealClearPolitics** | Scraped poll averages | realclearpolitics.com |
| **Wikipedia election pages** | Historical results | Scrape directly |

### 5.5 Datasets to Download Directly

```bash
# MIT Election Lab — Historical results
wget https://dataverse.harvard.edu/api/access/datafile/3641280

# FiveThirtyEight data repo
git clone https://github.com/fivethirtyeight/data

# Census district data
# Use censusdis Python library
pip install censusdis
```

---

## 6. Knowledge Graph Schema

### Node Types
```
(:District {id, name, state, population, median_income, urban_rural})
(:Candidate {name, party, incumbent, district_id})
(:Issue {name, category, description})
(:DemographicGroup {name, size_pct, district_id})
(:Policy {name, bill_id, status})
(:Event {title, date, type, impact_score})
(:PAC {name, total_funding, ideology})
```

### Relationship Types
```
(:District)-[:CONCERNED_ABOUT {weight, trend, updated_at}]->(:Issue)
(:Candidate)-[:REPRESENTS]->(:District)
(:Candidate)-[:BELONGS_TO]->(:Party)
(:Candidate)-[:VOTED_FOR / :VOTED_AGAINST]->(:Policy)
(:Policy)-[:ADDRESSES]->(:Issue)
(:Issue)-[:IMPACTS]->(:DemographicGroup)
(:Event)-[:AFFECTS_ISSUE {sentiment_delta}]->(:Issue)
(:PAC)-[:FUNDS]->(:Candidate)
(:District)-[:SIMILAR_TO {similarity_score}]->(:District)
```

### Example KG Query
```cypher
// What issues dominate District 7 and why?
MATCH (d:District {name: "AZ-07"})-[r:CONCERNED_ABOUT]->(i:Issue)
MATCH (i)-[:IMPACTS]->(dg:DemographicGroup)
MATCH (c:Candidate)-[:REPRESENTS]->(d)
OPTIONAL MATCH (c)-[:VOTED_AGAINST]->(p:Policy)-[:ADDRESSES]->(i)
RETURN d.name, i.name, r.weight, r.trend, dg.name, c.name, p.name
ORDER BY r.weight DESC
```

---

## 7. System Architecture

```
┌─────────────────────────────────────────────────────┐
│                  DATA SOURCES                        │
│  Census API  FEC  NewsAPI  GDELT  Reddit  Congress   │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│              DATA INGESTION LAYER                    │
│         (Python scripts + Airflow DAGs)              │
│    Batch ingestion + Weekly scheduled updates        │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│               STORAGE LAYER                          │
│  PostgreSQL (structured) + FAISS (vectors)           │
│  Neo4j (Knowledge Graph) + Redis (cache)             │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│            NLP + ML PROCESSING LAYER                 │
│  spaCy (NER) → BERTopic (issues) → BERT (sentiment) │
│  XGBoost (baseline) → PyKEEN (KG embeddings)         │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│          KNOWLEDGE GRAPH REASONING LAYER             │
│  Static KG → Dynamic update → Link prediction        │
│  Rule mining → Explainable reasoning chains          │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│                  API LAYER (FastAPI)                 │
│  /district /issues /sentiment /predict /explain      │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│              DASHBOARD (Streamlit → React)           │
│  District maps, issue heatmaps, sentiment trends     │
│  KG visualization, explainability panels             │
└─────────────────────────────────────────────────────┘
```

---

## 8. Build Phases

### Phase 1 — Static Foundation (May – July 2026)
```
✅ Data pipelines for Census, FEC, MIT Election Lab
✅ PostgreSQL schema + data loading
✅ Static KG built for 20 districts (not all 435 yet)
✅ Baseline NLP: sentiment + issue extraction
✅ XGBoost baseline model
✅ Basic Streamlit dashboard
✅ Neo4j KG visualization
```

### Phase 2 — Dynamic Layer (Aug – Sep 2026)
```
✅ Weekly Airflow DAGs pulling GDELT + NewsAPI
✅ New events → update KG issue weights automatically
✅ PyKEEN link prediction — infer new KG relations
✅ Sentiment tracking over time per district
✅ API layer with FastAPI
```

### Phase 3 — Intelligence Layer (Oct 2026)
```
✅ KG-grounded explainability (reasoning chains)
✅ District similarity reasoning
✅ Issue trend forecasting
✅ Compare vs FiveThirtyEight / RCP predictions
✅ Full dashboard with maps + heatmaps
```

### Phase 4 — Evaluation + Paper (Nov – Jan 2027)
```
✅ November 4 2026 — Midterm election day
✅ Collect actual results by district
✅ Compare: your predictions vs B1/B2/B3 baselines
✅ Analyze: where did KG reasoning add value?
✅ Write paper — submit to arXiv + workshop
```

---

## 9. Paper Structure

```
Title:
"Knowledge Graph-Grounded Political Intelligence:
 Explainable District-Level Analysis for US Midterm Elections"

Abstract
  Problem + your approach + key result (evaluated on 2026 midterms)

1. Introduction
   Why political intelligence needs explainability
   Why KGs are better than black-box ML for this

2. Related Work
   FiveThirtyEight methodology
   Political NLP papers
   Knowledge Graph reasoning papers
   Explainable AI in social science

3. System Architecture
   Data pipeline + KG schema + dynamic update mechanism

4. Methodology
   KG construction
   Dynamic induction (PyKEEN + AMIE3)
   Explainability reasoning chains
   Baseline comparisons

5. Experiments
   Dataset: 50-100 key districts
   Baselines: XGBoost, Vanilla RAG, FiveThirtyEight
   Metrics: Issue accuracy, sentiment accuracy,
            prediction alignment, explainability quality

6. Results
   Quantitative: your system vs baselines
   Qualitative: example reasoning chains
   Real evaluation: vs actual November 2026 results

7. Analysis
   Where KG helped most (swing districts, issue-heavy races)
   Failure cases + why
   Ablation: KG vs no KG

8. Conclusion
   Contribution + future work
```

Target venue: **arXiv preprint (Dec 2026) + ACL/EMNLP 2027 Workshop**

---

## 10. Repository Structure

```
political-intelligence-platform/
├── data/
│   ├── ingestion/
│   │   ├── census_pipeline.py
│   │   ├── fec_pipeline.py
│   │   ├── gdelt_pipeline.py
│   │   └── reddit_pipeline.py
│   ├── processing/
│   │   ├── cleaner.py
│   │   ├── feature_engineer.py
│   │   └── district_normalizer.py
│   └── airflow/
│       └── dags/
│           └── weekly_update_dag.py
├── knowledge_graph/
│   ├── schema.py
│   ├── builder.py
│   ├── updater.py
│   ├── induction.py          ← PyKEEN dynamic layer
│   └── reasoning.py          ← Explainability chains
├── nlp/
│   ├── sentiment.py
│   ├── issue_extractor.py
│   └── topic_model.py
├── ml/
│   ├── baseline_xgboost.py
│   └── kg_classifier.py
├── api/
│   ├── main.py
│   └── routers/
│       ├── district.py
│       ├── issues.py
│       ├── sentiment.py
│       └── predict.py
├── dashboard/
│   ├── streamlit_app.py
│   └── components/
├── paper/
│   └── draft.tex
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 11. Week 1 — Start Here

### Both of you do this together:

**Day 1-2:**
```bash
# Setup environment
python -m venv polint-env
source polint-env/bin/activate
pip install pandas requests neo4j spacy transformers
python -m spacy download en_core_web_sm
```

**Day 3-4:**
Pull your first real data:
```python
# census_test.py — get district demographics
import requests

# Census API — free, no key needed for basic queries
url = "https://api.census.gov/data/2020/acs/acs5"
params = {
    "get": "NAME,B01003_001E,B19013_001E",  # population, median income
    "for": "congressional district:*",
    "in": "state:04"  # Arizona = 04
}
response = requests.get(url, params=params)
data = response.json()
for row in data[:5]:
    print(row)
```

```python
# gdelt_test.py — pull political news free
import requests
from datetime import datetime, timedelta

# GDELT 2.0 — completely free, no API key
url = "https://api.gdeltproject.org/api/v2/doc/doc"
params = {
    "query": "congressional district election 2026",
    "mode": "artlist",
    "maxrecords": 10,
    "format": "json"
}
response = requests.get(url, params=params)
articles = response.json().get("articles", [])
for a in articles:
    print(a.get("title"), "|", a.get("url"))
```

**Day 5-7:**
- Design your Neo4j KG schema (use the schema in Section 6)
- Create nodes for 5 districts manually first
- Run a Cypher query and see the graph

---

## 12. Quick Reference — Key Commands

```bash
# Start Neo4j (after installing Neo4j Desktop)
# Just click Start in Neo4j Desktop UI

# Start your API
uvicorn api.main:app --reload

# Start Streamlit dashboard
streamlit run dashboard/streamlit_app.py

# Run Airflow locally
airflow standalone

# Pull GDELT data (no API key needed)
curl "https://api.gdeltproject.org/api/v2/doc/doc?query=election+2026&mode=artlist&maxrecords=10&format=json"
```

---

## 13. Research Contribution Summary (For Paper)

What you contribute that doesn't exist yet:

```
1. First system to combine dynamic KG induction
   with district-level political intelligence — novel architecture

2. Explainability via KG reasoning chains
   — not SHAP numbers, actual human-readable political reasons

3. Real-world evaluation on actual election results
   — most papers use historical/synthetic data

4. Multi-source fusion (census + finance + news + social + KG)
   evaluated as a unified system — not done cleanly before

5. District similarity reasoning via KG
   — "AZ-06 shows same issue pattern as TX-28 in 2022"
   — genuinely new capability
```

---

*Document version 1.0 — May 2026*
*Share freely with your project partner*