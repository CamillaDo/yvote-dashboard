#!/usr/bin/env python3
"""
YVote Dashboard - Streamlit Cloud Version
========================================

Modified version for Streamlit Cloud deployment.
Uses sample data when live data is not available.
"""

import streamlit as st
import pandas as pd
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np

# Handle plotly imports with error handling
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError as e:
    st.error(f"""
    **Plotly Import Error**: {e}
    
    This might be a dependency issue. The dashboard will use basic charts instead.
    """)
    PLOTLY_AVAILABLE = False
    # Create dummy plotly objects to prevent further errors
    class DummyPlotly:
        def bar(*args, **kwargs): return None
        def pie(*args, **kwargs): return None
        def line(*args, **kwargs): return None
    px = DummyPlotly()
    go = DummyPlotly()

# === PAGE CONFIGURATION ===
st.set_page_config(
    page_title="YVote Live Monitor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === STYLING ===
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .candidate-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .status-demo {
        color: #ff6b35;
        font-weight: bold;
    }
    .status-live {
        color: #28a745;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# === DATA LOADING FUNCTIONS ===
@st.cache_data(ttl=30)
def load_voting_data():
    """Load voting data with fallback to sample data"""
    # Try to load live data first
    live_csv = Path("yvote_v3_log.csv")
    sample_csv = Path("sample_data.csv")
    
    if live_csv.exists():
        try:
            df = pd.read_csv(live_csv)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df, True  # True = live data
        except:
            pass
    
    # Fallback to sample data
    if sample_csv.exists():
        try:
            df = pd.read_csv(sample_csv)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df, False  # False = demo data
        except:
            pass
    
    # Return empty if no data available
    return pd.DataFrame(), False

def get_latest_data(df):
    """Get the most recent voting data"""
    if df.empty:
        return pd.DataFrame()
    
    latest_time = df['timestamp'].max()
    return df[df['timestamp'] == latest_time].sort_values('rank')

def calculate_trends(df, hours=24):
    """Calculate voting trends over the specified time period"""
    if df.empty:
        return pd.DataFrame()
    
    cutoff_time = datetime.now() - timedelta(hours=hours)
    recent_df = df[df['timestamp'] >= cutoff_time]
    
    if recent_df.empty:
        return pd.DataFrame()
    
    trends = []
    for name in recent_df['name'].unique():
        candidate_data = recent_df[recent_df['name'] == name].sort_values('timestamp')
        if len(candidate_data) >= 2:
            first_votes = candidate_data.iloc[0]['votes']
            last_votes = candidate_data.iloc[-1]['votes']
            vote_change = last_votes - first_votes
            
            first_percent = candidate_data.iloc[0]['percent']
            last_percent = candidate_data.iloc[-1]['percent']
            percent_change = last_percent - first_percent
            
            trends.append({
                'name': name,
                'vote_change': vote_change,
                'percent_change': percent_change,
                'current_votes': last_votes,
                'current_percent': last_percent,
                'current_rank': candidate_data.iloc[-1]['rank']
            })
    
    return pd.DataFrame(trends)

# === DASHBOARD COMPONENTS ===
def render_header(is_live_data):
    """Render the main header and status"""
    st.markdown('<div class="main-header">🗳️ YVote Live Monitor</div>', unsafe_allow_html=True)
    
    # Status indicator
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if is_live_data:
            status_class = "status-live"
            status_icon = "🟢"
            status_msg = "Live Data"
        else:
            status_class = "status-demo"
            status_icon = "🔶"
            status_msg = "Demo Mode (Sample Data)"
        
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background-color: #f8f9fa; border-radius: 0.5rem;">
            <span class="{status_class}">{status_icon} Status: {status_msg}</span>
        </div>
        """, unsafe_allow_html=True)
        
        if not is_live_data:
            st.info("📋 This is a demo using sample data. Deploy with your live data to see real-time results.")

def render_key_metrics(df, is_live_data):
    """Render key voting metrics"""
    if df.empty:
        st.warning("No data available.")
        return
    
    latest_data = get_latest_data(df)
    total_votes = latest_data['votes'].sum() if not latest_data.empty else 0
    
    # Calculate some basic statistics
    total_candidates = len(latest_data) if not latest_data.empty else 0
    last_update = df['timestamp'].max() if not df.empty else None
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🗳️ Total Votes",
            value=f"{total_votes:,}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="👥 Candidates",
            value=total_candidates,
            delta=None
        )
    
    with col3:
        if last_update:
            if is_live_data:
                time_since = datetime.now() - last_update
                minutes_ago = int(time_since.total_seconds() / 60)
                st.metric(
                    label="⏱️ Last Update",
                    value=f"{minutes_ago}m ago",
                    delta=None
                )
            else:
                st.metric(
                    label="⏱️ Demo Data",
                    value="Sample",
                    delta=None
                )
        else:
            st.metric(
                label="⏱️ Last Update",
                value="Never",
                delta=None
            )
    
    with col4:
        if is_live_data and not df.empty:
            # Calculate votes per minute based on recent data
            recent_hours = 2
            recent_data = df[df['timestamp'] >= datetime.now() - timedelta(hours=recent_hours)]
            if len(recent_data) > 1:
                time_span = (recent_data['timestamp'].max() - recent_data['timestamp'].min()).total_seconds() / 60
                total_votes_change = recent_data.groupby('timestamp')['votes'].sum().max() - recent_data.groupby('timestamp')['votes'].sum().min()
                votes_per_min = total_votes_change / time_span if time_span > 0 else 0
                st.metric(
                    label="📈 Votes/min",
                    value=f"{votes_per_min:.1f}",
                    delta=None
                )
            else:
                st.metric(
                    label="📈 Votes/min",
                    value="N/A",
                    delta=None
                )
        else:
            st.metric(
                label="📈 Demo Mode",
                value="Sample",
                delta=None
            )

def render_current_rankings(df):
    """Render current candidate rankings"""
    if df.empty:
        return
    
    st.subheader("🏆 Current Rankings")
    
    latest_data = get_latest_data(df)
    if latest_data.empty:
        st.warning("No current ranking data available.")
        return
    
    # Create a nice ranking display
    for _, candidate in latest_data.iterrows():
        rank = candidate['rank']
        name = candidate['name']
        votes = candidate['votes']
        percent = candidate['percent']
        
        # Determine medal emoji
        if rank == 1:
            medal = "🥇"
        elif rank == 2:
            medal = "🥈"
        elif rank == 3:
            medal = "🥉"
        else:
            medal = f"#{rank}"
        
        st.markdown(f"""
        <div class="candidate-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; align-items: center;">
                    <span style="font-size: 1.5rem; margin-right: 1rem;">{medal}</span>
                    <strong style="font-size: 1.2rem;">{name}</strong>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 1.1rem; font-weight: bold;">{votes:,} votes</div>
                    <div style="color: #666;">{percent:.2f}%</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_voting_trends(df):
    """Render voting trend charts"""
    if df.empty:
        return
    
    st.subheader("📊 Voting Trends")
    
    latest_data = get_latest_data(df)
    if latest_data.empty:
        st.warning("No data available for charts.")
        return
    
    if PLOTLY_AVAILABLE:
        # Create tabs for different views with Plotly
        tab1, tab2 = st.tabs(["📈 Vote Distribution", "📊 Percentage Share"])
        
        with tab1:
            # Vote distribution chart
            fig = px.bar(
                latest_data,
                x='name',
                y='votes',
                title='Current Vote Distribution',
                labels={'votes': 'Votes', 'name': 'Candidate'},
                color='votes',
                color_continuous_scale='viridis'
            )
            fig.update_layout(
                height=500,
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            # Percentage share pie chart
            fig = px.pie(
                latest_data,
                values='percent',
                names='name',
                title='Vote Percentage Share'
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
    else:
        # Fallback to Streamlit native charts
        st.subheader("📈 Vote Distribution")
        chart_data = latest_data.set_index('name')['votes']
        st.bar_chart(chart_data)
        
        st.subheader("📊 Data Table")
        st.dataframe(
            latest_data[['rank', 'name', 'votes', 'percent']].style.format({
                'votes': '{:,}',
                'percent': '{:.2f}%'
            }),
            use_container_width=True
        )

def render_sidebar(df, is_live_data):
    """Render sidebar with information"""
    st.sidebar.title("⚙️ Dashboard Info")
    
    # Data status
    st.sidebar.subheader("📊 Data Status")
    status_emoji = "🟢" if is_live_data else "🔶"
    status_text = "Live Data" if is_live_data else "Demo Mode"
    st.sidebar.write(f"{status_emoji} **{status_text}**")
    
    if not df.empty:
        st.sidebar.write(f"📊 Records: {len(df):,}")
        st.sidebar.write(f"👥 Candidates: {df['name'].nunique()}")
        st.sidebar.write(f"📅 Latest: {df['timestamp'].max().strftime('%Y-%m-%d %H:%M')}")
    
    st.sidebar.divider()
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    st.sidebar.divider()
    
    # Information
    with st.sidebar.expander("ℹ️ About"):
        st.write("""
        **YVote Live Monitor**
        
        Real-time voting dashboard for tracking candidate performance.
        
        **Features:**
        - Live vote tracking
        - Candidate rankings
        - Interactive visualizations
        - Mobile-responsive design
        
        **Data:**
        - Updates every 5 minutes (live mode)
        - Shows all candidates
        - Historical trends
        """)
    
    # GitHub link
    st.sidebar.markdown("---")
    st.sidebar.markdown("**🔗 Links**")
    st.sidebar.markdown("[📊 Dashboard Source](https://github.com/yourusername/yvote-dashboard)")
    st.sidebar.markdown("[📈 Live Data API](https://yvoting-service.onfan.vn)")

# === MAIN DASHBOARD ===
def main():
    """Main dashboard function"""
    # Load data
    df, is_live_data = load_voting_data()
    
    # Render sidebar
    render_sidebar(df, is_live_data)
    
    # Render header
    render_header(is_live_data)
    
    # Main content
    if df.empty:
        st.error("""
        🚫 **No Data Available**
        
        Could not load voting data. Please check:
        1. Data files are available
        2. File permissions are correct
        3. Data format is valid
        """)
        return
    
    # Render dashboard components
    render_key_metrics(df, is_live_data)
    st.divider()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        render_current_rankings(df)
    
    with col2:
        render_voting_trends(df)

# === RUN DASHBOARD ===
if __name__ == "__main__":
    main()