# AtmoSync: Micro-Climate Analytics

A data pipeline project to detect micro-climate shifts inside shipping containers in near real-time. The main idea is to calculate "Spoilage Arbitrage" — basically figuring out if cargo is degrading faster than expected so traders can reroute it to closer markets before the quality drops.

## Tech Stack
* **Processing:** Python 3.10, Pandas
* **Storage:** DuckDB
* **Dashboard:** Streamlit, Plotly
* **Validation:** Pydantic
* **Testing:** Pytest

## Folder Structure
* `src/` - main pipeline code
* `data/` - raw, staging, and mart tables (gitignored)
* `sql/` - sql models for transformation
* `tests/` - basic unit tests
* `.github/workflows/` - simple CI pipeline

## Local Setup
1. Create virtual environment: `python -m venv venv`
2. Activate it: `venv\Scripts\activate` (for Windows)
3. Install requirements: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env`

---
*Created by Jillani*