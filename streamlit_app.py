import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path

st.title("🗳️ YVote Live Monitor")

# Try to load latest data file
data_file = Path("latest_data.csv")
if data_file.exists():
    df = pd.read_csv(data_file)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Get latest data
    latest_time = df['timestamp'].max()
    latest_data = df[df['timestamp'] == latest_time].sort_values('rank')

    st.success(f"✅ Data loaded successfully! Last update: {latest_time}")

    # Show metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🗳️ Total Votes", f"{latest_data['votes'].sum():,}")
    with col2:
        st.metric("👥 Candidates", len(latest_data))
    with col3:
        st.metric("⏱️ Last Update", latest_time.strftime('%H:%M'))

    # Show rankings
    st.subheader("🏆 Current Rankings")
    for _, row in latest_data.iterrows():
        rank = row['rank']
        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"#{rank}"
        st.write(f"{medal} **{row['name']}** - {row['votes']:,} votes ({row['percent']:.2f}%)")

    # Show chart
    st.subheader("📊 Vote Distribution")
    chart_data = latest_data.set_index('name')['votes']
    st.bar_chart(chart_data)

else:
    st.error("No data file found. Please upload latest_data.csv")
