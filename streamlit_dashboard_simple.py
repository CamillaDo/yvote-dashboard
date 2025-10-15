#!/usr/bin/env python3
"""
YVote Dashboard - Simple Version (No Plotly)
============================================

Simplified version without Plotly dependency for easier deployment.
"""

import streamlit as st
import pandas as pd
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np

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
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .status-demo {
        color: #ff6b35;
        font-weight: bold;
    }
    .status-live {
        color: #28a745;
        font-weight: bold;
    }
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
        margin: 0.5rem 0;
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
        except Exception as e:
            st.error(f"Error loading live data: {e}")
    
    # Fallback to sample data
    if sample_csv.exists():
        try:
            df = pd.read_csv(sample_csv)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df, False  # False = demo data
        except Exception as e:
            st.error(f"Error loading sample data: {e}")
    
    # Return empty if no data available
    return pd.DataFrame(), False

def get_latest_data(df):
    """Get the most recent voting data"""
    if df.empty:
        return pd.DataFrame()
    
    latest_time = df['timestamp'].max()
    return df[df['timestamp'] == latest_time].sort_values('rank')

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
            status_msg = "Live Data Connected"
        else:
            status_class = "status-demo"
            status_icon = "🔶"
            status_msg = "Demo Mode (Sample Data)"
        
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background-color: #f8f9fa; border-radius: 0.5rem; border: 2px solid #dee2e6;">
            <span class="{status_class}">{status_icon} {status_msg}</span>
        </div>
        """, unsafe_allow_html=True)
        
        if not is_live_data:
            st.info("📋 This demo shows sample voting data. Connect live data source for real-time results.")

def render_key_metrics(df, is_live_data):
    """Render key voting metrics"""
    if df.empty:
        st.warning("⚠️ No voting data available.")
        return
    
    latest_data = get_latest_data(df)
    total_votes = latest_data['votes'].sum() if not latest_data.empty else 0
    total_candidates = len(latest_data) if not latest_data.empty else 0
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-container">
            <h3>🗳️ Total Votes</h3>
            <h1>{total_votes:,}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-container">
            <h3>👥 Candidates</h3>
            <h1>{total_candidates}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if not df.empty:
            last_update = df['timestamp'].max()
            if is_live_data:
                time_since = datetime.now() - last_update
                minutes_ago = int(time_since.total_seconds() / 60)
                update_text = f"{minutes_ago}m ago"
            else:
                update_text = "Demo Data"
        else:
            update_text = "No Data"
            
        st.markdown(f"""
        <div class="metric-container">
            <h3>⏱️ Last Update</h3>
            <h1>{update_text}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        if is_live_data and total_votes > 0:
            # Calculate voting rate
            latest_time = df['timestamp'].max()
            first_time = df['timestamp'].min()
            hours_span = (latest_time - first_time).total_seconds() / 3600
            votes_per_hour = total_votes / hours_span if hours_span > 0 else 0
            rate_text = f"{votes_per_hour:.0f}/hr"
        else:
            rate_text = "Demo Mode"
            
        st.markdown(f"""
        <div class="metric-container">
            <h3>📈 Vote Rate</h3>
            <h1>{rate_text}</h1>
        </div>
        """, unsafe_allow_html=True)

def render_current_rankings(df):
    """Render current candidate rankings"""
    if df.empty:
        return
    
    st.subheader("🏆 Current Rankings")
    
    latest_data = get_latest_data(df)
    if latest_data.empty:
        st.warning("No ranking data available.")
        return
    
    # Create ranking display
    for i, (_, candidate) in enumerate(latest_data.iterrows()):
        rank = candidate['rank']
        name = candidate['name']
        votes = candidate['votes']
        percent = candidate['percent']
        
        # Determine medal emoji and colors
        if rank == 1:
            medal = "🥇"
            border_color = "#FFD700"
        elif rank == 2:
            medal = "🥈"
            border_color = "#C0C0C0"
        elif rank == 3:
            medal = "🥉"
            border_color = "#CD7F32"
        else:
            medal = f"#{rank}"
            border_color = "#1f77b4"
        
        # Progress bar width
        max_percent = latest_data['percent'].max()
        progress_width = (percent / max_percent * 100) if max_percent > 0 else 0
        
        st.markdown(f"""
        <div style="
            background-color: #ffffff;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid {border_color};
            margin: 0.5rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; align-items: center; flex: 1;">
                    <span style="font-size: 1.5rem; margin-right: 1rem; min-width: 50px;">{medal}</span>
                    <div style="flex: 1;">
                        <strong style="font-size: 1.2rem; color: #2c3e50;">{name}</strong>
                        <div style="background-color: #ecf0f1; height: 8px; border-radius: 4px; margin-top: 5px;">
                            <div style="background-color: {border_color}; height: 8px; border-radius: 4px; width: {progress_width}%;"></div>
                        </div>
                    </div>
                </div>
                <div style="text-align: right; margin-left: 1rem;">
                    <div style="font-size: 1.1rem; font-weight: bold; color: #2c3e50;">{votes:,}</div>
                    <div style="color: #7f8c8d; font-size: 0.9rem;">{percent:.2f}%</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_simple_charts(df):
    """Render simple charts using Streamlit native functionality"""
    if df.empty:
        return
    
    st.subheader("📊 Data Visualization")
    
    latest_data = get_latest_data(df)
    if latest_data.empty:
        st.warning("No data available for visualization.")
        return
    
    # Create two columns for charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Vote Distribution")
        # Use Streamlit's native bar chart
        chart_data = latest_data.set_index('name')['votes']
        st.bar_chart(chart_data, height=400)
    
    with col2:
        st.subheader("📋 Detailed Rankings")
        # Display formatted table
        display_data = latest_data[['rank', 'name', 'votes', 'percent']].copy()
        display_data.columns = ['Rank', 'Candidate', 'Votes', 'Percentage (%)']
        
        st.dataframe(
            display_data.style.format({
                'Votes': '{:,}',
                'Percentage (%)': '{:.2f}'
            }).background_gradient(subset=['Votes'], cmap='viridis'),
            use_container_width=True,
            height=400
        )

def render_sidebar(df, is_live_data):
    """Render sidebar with information"""
    st.sidebar.title("⚙️ Dashboard Controls")
    
    # Data status
    st.sidebar.subheader("📊 Data Status")
    status_emoji = "🟢" if is_live_data else "🔶"
    status_text = "Live Data" if is_live_data else "Demo Mode"
    st.sidebar.markdown(f"**{status_emoji} {status_text}**")
    
    if not df.empty:
        st.sidebar.metric("📊 Total Records", f"{len(df):,}")
        st.sidebar.metric("👥 Candidates", df['name'].nunique())
        st.sidebar.metric("📅 Latest Update", df['timestamp'].max().strftime('%m/%d %H:%M'))
    
    st.sidebar.divider()
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    # Auto-refresh toggle
    auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh (30s)", value=False)
    
    if auto_refresh:
        time.sleep(30)
        st.rerun()
    
    st.sidebar.divider()
    
    # Information
    with st.sidebar.expander("ℹ️ About This Dashboard"):
        st.write("""
        **YVote Live Monitor**
        
        Real-time voting dashboard for tracking candidate performance.
        
        **Features:**
        - Live vote tracking
        - Candidate rankings
        - Visual progress bars
        - Mobile-responsive design
        - Auto-refresh capability
        
        **Data Source:**
        - Live: Real-time API updates
        - Demo: Sample voting data
        """)
    
    # Quick stats
    if not df.empty:
        with st.sidebar.expander("📈 Quick Stats"):
            latest_data = get_latest_data(df)
            if not latest_data.empty:
                leader = latest_data.iloc[0]
                st.write(f"**👑 Leading:** {leader['name']}")
                st.write(f"**🗳️ Lead Votes:** {leader['votes']:,}")
                st.write(f"**📊 Lead Margin:** {leader['percent']:.1f}%")
                
                if len(latest_data) > 1:
                    gap = leader['votes'] - latest_data.iloc[1]['votes']
                    st.write(f"**📏 Vote Gap:** {gap:,}")

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
        
        Could not load voting data. This might be because:
        - No data files are present
        - File permissions issue
        - Data format is invalid
        
        **For deployment:** Make sure `sample_data.csv` is included in your repository.
        """)
        return
    
    # Render dashboard components
    render_key_metrics(df, is_live_data)
    st.divider()
    
    # Main content area
    render_current_rankings(df)
    st.divider()
    render_simple_charts(df)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #7f8c8d;'>"
        "🗳️ YVote Live Monitor | Built with Streamlit ❤️"
        "</div>", 
        unsafe_allow_html=True
    )

# === RUN DASHBOARD ===
if __name__ == "__main__":
    main()