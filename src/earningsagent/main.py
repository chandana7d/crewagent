#!/usr/bin/env python
import os
import json
import asyncio
import pandas as pd
import sqlite3
from pydantic import BaseModel, Field
from crew import EarningsCrew
from dotenv import load_dotenv
import os

load_dotenv()

class EarningsInput(BaseModel):
    company: str
    ticker: str
    quarter: str
    year: int
    include_transcript: bool = True
    include_guidance: bool = True
    include_sentiment: bool = False

def save_outputs(results):
    with open("earnings_summaries.json", "w") as f:
        json.dump(results, f, indent=2)
    df = pd.DataFrame(results)
    df.to_csv("earnings_summaries.csv", index=False)
    conn = sqlite3.connect("earnings_reports.db")
    df.to_sql("summaries", conn, if_exists="replace", index=False)
    conn.close()

async def run_summary(crew, stock, quarter, year):
    inputs = EarningsInput(
        company=stock["company"],
        ticker=stock["ticker"],
        quarter=quarter,
        year=year,
        include_transcript=True,
        include_guidance=True,
        include_sentiment=True
    )
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        crew.kickoff,
        inputs.dict()
    )
    return result.pydantic.dict()

async def main():
    stocks = [
        {"company": "Apple Inc.", "ticker": "AAPL"},
        {"company": "Microsoft Corp.", "ticker": "MSFT"},
        {"company": "Amazon.com Inc.", "ticker": "AMZN"},
        {"company": "Alphabet Inc.", "ticker": "GOOGL"},
        {"company": "Meta Platforms Inc.", "ticker": "META"},
        {"company": "Tesla Inc.", "ticker": "TSLA"},
        {"company": "NVIDIA Corp.", "ticker": "NVDA"},
        {"company": "Berkshire Hathaway", "ticker": "BRK.A"},
        {"company": "JPMorgan Chase & Co.", "ticker": "JPM"},
        {"company": "Johnson & Johnson", "ticker": "JNJ"},
    ]
    quarter = "Q2"
    year = 2025

    earnings_crew = EarningsCrew()
    tasks = [run_summary(earnings_crew, stock, quarter, year) for stock in stocks]
    results = await asyncio.gather(*tasks)

    save_outputs(results)
    print("✅ Earnings summaries saved to JSON, CSV, and SQLite database.")

if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore")
    os.environ['OPENAI_MODEL_NAME'] = 'gpt-4o-mini'

    # Robust async compatibility: works in scripts and Jupyter!
    try:
        import nest_asyncio
        nest_asyncio.apply()
    except ImportError:
        pass
    try:
        asyncio.run(main())
    except RuntimeError as e:
        # Fallback for running event loop
        import sys
        if "asyncio.run() cannot be called from a running event loop" in str(e):
            if hasattr(asyncio, 'get_running_loop'):
                loop = asyncio.get_running_loop()
            else:
                loop = asyncio.get_event_loop()
            import nest_asyncio
            nest_asyncio.apply()
            loop.create_task(main())
        else:
            raise
