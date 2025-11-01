# data_loader.py
import streamlit as st
import pandas as pd

RAW_URL = "https://raw.githubusercontent.com/AleyaNazifa/AssignmentSV2025-1/refs/heads/main/hfdm_data%20-%20Upload.csv"

@st.cache_data(ttl=3600)
def load_daily(url: str = RAW_URL) -> pd.DataFrame:
    df = pd.read_csv(url)
    # standardize columns
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    if "date" not in df.columns:
        raise ValueError("No 'Date' column in CSV.")
    # parse date (CSV uses dd/mm/yyyy)
    df["date"] = pd.to_datetime(df["date"], format="%d/%m/%Y", errors="coerce")
    df = df.dropna(subset=["date"]).sort_values("date")
    # compute total cases
    regions = ["southern", "northern", "central", "east_coast", "borneo"]
    df["total_cases"] = df[regions].sum(axis=1, numeric_only=True)
    return df

@st.cache_data(ttl=3600)
def load_monthly(url: str = RAW_URL) -> pd.DataFrame:
    daily = load_daily(url)
    m = (
        daily.set_index("date")
             .resample("M")
             .mean(numeric_only=True)
             .reset_index()
             .rename(columns={"date": "Date"})
    )
    m["Year"] = m["Date"].dt.year
    m["Month"] = m["Date"].dt.month
    return m
