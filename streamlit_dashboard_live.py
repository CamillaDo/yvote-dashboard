#!/usr/bin/env python3
"""
YVote Dashboard - Live API Version
==================================

Connects directly to YVote API for real-time data.
"""

import streamlit as st
import pandas as pd
import requests
import json
import time
from datetime import datetime, timedelta
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
    .status-live {
        color: #28a745;
        font-weight: bold;
    }
    .status-error {
        color: #dc3545;
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

# === API CONFIGURATION ===
API_ENDPOINT = "https://r.jina.ai/https://yvoting-service.onfan.vn/api/v1/nominations/spotlight"
AWARD_ID = "58e78a33-c7c9-4bd4-b536-f25fa75b68c2"

# === DATA LOADING FUNCTIONS ===
@st.cache_data(ttl=30)  # Cache for 30 seconds
def fetch_live_data():
    """Fetch live data from YVote API"""
    try:
        # Make API request
        response = requests.get(
            API_ENDPOINT,
            params={"awardId": AWARD_ID},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract nominations data
            if 'data' in data and 'nominations' in data['data']:
                nominations = data['data']['nominations']
                
                # Convert to DataFrame
                rows = []
                current_time = datetime.now()
                
                for i, nomination in enumerate(nominations, 1):
                    rows.append({
                        'timestamp': current_time,
                        'rank': i,
                        'name': nomination.get('name', 'Unknown'),
                        'votes': nomination.get('voteCount', 0),
                        'percent': nomination.get('percent', 0.0)
                    })
                
                df = pd.DataFrame(rows)
                total_votes = df['votes'].sum()
                
                return df, total_votes, True, "Live data connected"
            else:
                return pd.DataFrame(), 0, False, "No nominations data in API response"
        else:
            return pd.DataFrame(), 0, False, f"API error: {response.status_code}"
            
    except requests.exceptions.RequestException as e:
        return pd.DataFrame(), 0, False, f"Connection error: {str(e)}"
    except Exception as e:
        return pd.DataFrame(), 0, False, f"Data processing error: {str(e)}"

def load_fallback_data():
    """Load sample data as fallback"""
    try:
        sample_data = {
            'timestamp': [datetime.now()] * 11,
            'rank': list(range(1, 12)),
            'name': [
                'HỒ ĐÔNG QUAN', 'CƯỜNG BẠCH', 'PHÚC NGUYÊN', 
                'LÂM ANH', 'WONBI', 'THÁI LÊ MINH HIẾU',
                'SWAN NGUYỄN', 'MINHTIN', 'ĐỨC DUY', 
                'LONG HOÀNG', 'DUY LÂN'
            ],
            'votes': [592810, 110097, 100132, 55467, 49266, 25771, 
                     21149, 20358, 14800, 11155, 9561],
            'percent': [58.65, 10.90, 9.92, 5.49, 4.87, 2.55,
                       2.09, 2.02, 1.46, 1.10, 0.95]
        }
        df = pd.DataFrame(sample_data)
        total_votes = df['votes'].sum()
        return df, total_votes, False, "Using sample data (API unavailable)"
    except:
        return pd.DataFrame(), 0, False, "No data available"

# === DASHBOARD COMPONENTS ===
def render_header(is_live, status_message):
    """Render the main header and status"""
    st.markdown('<div class="main-header">🗳️ YVote Live Monitor</div>', unsafe_allow_html=True)
    
    # Status indicator
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if is_live:
            status_class = "status-live"
            status_icon = "🟢"
        else:
            status_class = "status-error"
            status_icon = "🔴"
        
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background-color: #f8f9fa; border-radius: 0.5rem; border: 2px solid #dee2e6;">
            <span class="{status_class}">{status_icon} {status_message}</span>
        </div>
        """, unsafe_allow_html=True)
        
        if not is_live:
            st.warning("⚠️ Unable to connect to live API. Showing fallback data.")

def render_key_metrics(df, total_votes, is_live):
    """Render key voting metrics"""
    if df.empty:
        st.error("⚠️ No voting data available.")
        return
    
    total_candidates = len(df)
    
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
        if is_live:
            update_text = "Live"
        else:
            update_text = "Sample"
            
        st.markdown(f"""
        <div class="metric-container">
            <h3>⏱️ Data Status</h3>
            <h1>{update_text}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        data_source = "API" if is_live else "Demo"
        st.markdown(f"""
        <div class="metric-container">
            <h3>📡 Source</h3>
            <h1>{data_source}</h1>
        </div>
        """, unsafe_allow_html=True)

def render_current_rankings(df):
    """Render current candidate rankings"""
    if df.empty:
        return
    
    st.subheader("🏆 Current Rankings")
    
    # Create ranking display
    for i, (_, candidate) in enumerate(df.iterrows()):
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
        max_percent = df['percent'].max()
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
    
    # Create two columns for charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Vote Distribution")
        # Use Streamlit's native bar chart
        chart_data = df.set_index('name')['votes']
        st.bar_chart(chart_data, height=400)
    
    with col2:
        st.subheader("📋 Detailed Rankings")
        # Display formatted table
        display_data = df[['rank', 'name', 'votes', 'percent']].copy()
        display_data.columns = ['Rank', 'Candidate', 'Votes', 'Percentage (%)']
        
        st.dataframe(
            display_data.style.format({
                'Votes': '{:,}',
                'Percentage (%)': '{:.2f}'
            }).background_gradient(subset=['Votes'], cmap='viridis'),
            use_container_width=True,
            height=400
        )

def render_sidebar(df, is_live, status_message):
    """Render sidebar with information"""
    st.sidebar.title("⚙️ Dashboard Controls")
    
    # Data status
    st.sidebar.subheader("📊 Data Status")
    status_emoji = "🟢" if is_live else "🔴"
    status_text = "Live API" if is_live else "Sample Data"
    st.sidebar.markdown(f"**{status_emoji} {status_text}**")
    st.sidebar.caption(status_message)
    
    if not df.empty:
        st.sidebar.metric("📊 Total Records", f"{len(df):,}")
        st.sidebar.metric("👥 Candidates", df['name'].nunique())
        st.sidebar.metric("📅 Last Update", datetime.now().strftime('%H:%M:%S'))
    
    st.sidebar.divider()
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    # Auto-refresh toggle
    auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh (30s)", value=True)
    
    if auto_refresh:
        time.sleep(30)
        st.rerun()
    
    st.sidebar.divider()
    
    # API Information
    with st.sidebar.expander("🔗 API Information"):
        st.write(f"""
        **Endpoint:** `{API_ENDPOINT}`
        
        **Award ID:** `{AWARD_ID}`
        
        **Update Frequency:** Every 30 seconds
        
        **Status:** {"🟢 Connected" if is_live else "🔴 Offline"}
        """)
    
    # Quick stats
    if not df.empty:
        with st.sidebar.expander("📈 Quick Stats"):
            leader = df.iloc[0]
            st.write(f"**👑 Leading:** {leader['name']}")
            st.write(f"**🗳️ Lead Votes:** {leader['votes']:,}")
            st.write(f"**📊 Lead Margin:** {leader['percent']:.1f}%")
            
            if len(df) > 1:
                gap = leader['votes'] - df.iloc[1]['votes']
                st.write(f"**📏 Vote Gap:** {gap:,}")

# === MAIN DASHBOARD ===
def main():
    """Main dashboard function"""
    # Try to fetch live data first
    df, total_votes, is_live, status_message = fetch_live_data()
    
    # If live data fails, use fallback
    if df.empty:
        df, total_votes, is_live, status_message = load_fallback_data()
    
    # Render sidebar
    render_sidebar(df, is_live, status_message)
    
    # Render header
    render_header(is_live, status_message)
    
    # Main content
    if df.empty:
        st.error("""
        🚫 **No Data Available**
        
        Could not load voting data from either:
        - Live API endpoint
        - Sample data fallback
        
        Please check your internet connection and try refreshing.
        """)
        return
    
    # Render dashboard components
    render_key_metrics(df, total_votes, is_live)
    st.divider()
    
    # Main content area
    render_current_rankings(df)
    st.divider()
    render_simple_charts(df)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #7f8c8d;'>"
        f"🗳️ YVote Live Monitor | {'🟢 Live Data' if is_live else '🔴 Demo Mode'} | "
        f"Last Updated: {datetime.now().strftime('%H:%M:%S')}"
        "</div>", 
        unsafe_allow_html=True
    )

# === RUN DASHBOARD ===
if __name__ == "__main__":
    main()
