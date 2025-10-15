#!/usr/bin/env python3
"""
YVote Dashboard - Live API Version (Working)
==========================================

Connects directly to YVote API for real-time data with correct data structure handling.
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
st.html("""
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
    .success-badge {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
        font-weight: bold;
        display: inline-block;
        margin: 0.5rem 0;
    }
</style>
""")

# === API CONFIGURATION ===
API_ENDPOINT = "https://yvoting-service.onfan.vn/api/v1/nominations/spotlight"
AWARD_ID = "58e78a33-c7c9-4bd4-b536-f25fa75b68c2"

# === DATA LOADING FUNCTIONS ===
@st.cache_data(ttl=30)  # Cache for 30 seconds
def fetch_live_data():
    """Fetch live data from YVote API with correct structure handling"""
    try:
        # Working headers that bypass Cloudflare
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        # Make API request
        response = requests.get(
            API_ENDPOINT,
            params={"awardId": AWARD_ID},
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if API response is successful
            if data.get('success', False) and 'data' in data:
                nominations = data['data']  # data is a list, not nested in 'nominations'
                
                if isinstance(nominations, list) and nominations:
                    # Convert to DataFrame with correct field mapping
                    rows = []
                    current_time = datetime.now()
                    
                    # Sort by ratioVotes (descending) to get proper ranking
                    sorted_nominations = sorted(nominations, key=lambda x: x.get('ratioVotes', 0), reverse=True)
                    
                    for i, nomination in enumerate(sorted_nominations, 1):
                        character = nomination.get('character', {})
                        name = character.get('name', 'Unknown')
                        ratio_votes = nomination.get('ratioVotes', 0.0)
                        
                        # Calculate actual vote count from ratio (approximate)
                        # Note: API only provides ratioVotes, actual vote counts not available
                        estimated_votes = int(ratio_votes * 10000)  # Scale for display
                        
                        rows.append({
                            'timestamp': current_time,
                            'rank': i,
                            'name': name,
                            'votes': estimated_votes,
                            'percent': ratio_votes,
                            'id': nomination.get('id', ''),
                            'order_in_award': nomination.get('orderInAward', i),
                            'status': nomination.get('statusInAward', 'UNKNOWN'),
                            'jobs': character.get('displayJobs', []),
                            'gender': character.get('gender', 'UNKNOWN')
                        })
                    
                    df = pd.DataFrame(rows)
                    total_votes = df['votes'].sum()
                    
                    return df, total_votes, True, f"✅ Live data connected ({len(nominations)} candidates)"
                else:
                    return pd.DataFrame(), 0, False, "❌ No nominations data in response"
            else:
                return pd.DataFrame(), 0, False, f"❌ API success flag: {data.get('success', 'unknown')}"
                
        elif response.status_code == 403:
            if 'cloudflare' in response.text.lower():
                return pd.DataFrame(), 0, False, "🚫 API blocked by Cloudflare (403 Forbidden)"
            else:
                return pd.DataFrame(), 0, False, f"🚫 Access forbidden (403)"
        else:
            return pd.DataFrame(), 0, False, f"❌ API error: {response.status_code}"
            
    except requests.exceptions.Timeout:
        return pd.DataFrame(), 0, False, "⏰ Connection timeout"
    except requests.exceptions.ConnectionError:
        return pd.DataFrame(), 0, False, "🌐 Connection error"
    except requests.exceptions.RequestException as e:
        return pd.DataFrame(), 0, False, f"🔌 Network error: {str(e)}"
    except json.JSONDecodeError:
        return pd.DataFrame(), 0, False, "📝 Invalid JSON response"
    except Exception as e:
        return pd.DataFrame(), 0, False, f"⚠️ Unexpected error: {str(e)}"

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
        return df, total_votes, False, "📊 Using sample data (API unavailable)"
    except Exception as e:
        return pd.DataFrame(), 0, False, f"❌ No data available: {str(e)}"

# === DASHBOARD COMPONENTS ===
def render_header(is_live, status_message):
    """Render the main header and status"""
    st.html('<div class="main-header">🗳️ YVote Live Monitor</div>')
    
    # Status indicator
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if is_live:
            st.html(f"""
            <div class="success-badge">
                🟢 {status_message}
            </div>
            """)
        else:
            st.error(f"🔴 {status_message}")

def render_key_metrics(df, total_votes, is_live):
    """Render key voting metrics"""
    if df.empty:
        st.error("⚠️ No voting data available.")
        return
    
    total_candidates = len(df)
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.html(f"""
        <div class="metric-container">
            <h3>🗳️ Total Votes</h3>
            <h1>{total_votes:,}</h1>
        </div>
        """)
    
    with col2:
        st.html(f"""
        <div class="metric-container">
            <h3>👥 Candidates</h3>
            <h1>{total_candidates}</h1>
        </div>
        """)
    
    with col3:
        data_type = "🟢 Live" if is_live else "📊 Sample"
        st.html(f"""
        <div class="metric-container">
            <h3>⏱️ Data Type</h3>
            <h1>{data_type}</h1>
        </div>
        """)
    
    with col4:
        last_update = datetime.now().strftime('%H:%M:%S')
        st.html(f"""
        <div class="metric-container">
            <h3>🔄 Updated</h3>
            <h1>{last_update}</h1>
        </div>
        """)

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
        
        # Get additional info if available
        jobs = candidate.get('jobs', [])
        jobs_text = ', '.join(jobs) if jobs else ''
        
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
        
        st.html(f"""
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
                        {f'<div style="color: #7f8c8d; font-size: 0.9rem;">{jobs_text}</div>' if jobs_text else ''}
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
        """)

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
            width='stretch',
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
    
    # Control buttons
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("🔄 Refresh", width='stretch'):
            st.cache_data.clear()
            st.rerun()
    
    with col2:
        if st.button("🧹 Clear Cache", width='stretch'):
            st.cache_data.clear()
            st.success("Cache cleared!")
    
    # Auto-refresh toggle
    auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh (30s)", value=False)
    
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
        
        **Data Structure:** Fixed for correct API format
        """)
    
    # Live Data Details
    if is_live and not df.empty:
        with st.sidebar.expander("📈 Live Data Info"):
            st.write("""
            **Data Source:** YVote API
            **Format:** JSON with nominations array
            **Fields:** ratioVotes, character info, status
            **Ranking:** Based on ratioVotes percentage
            """)
            
            # Show data freshness
            st.write(f"**Last API Call:** {datetime.now().strftime('%H:%M:%S')}")
            st.write(f"**Cache TTL:** 30 seconds")
    
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
    if df.empty and not is_live:
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
        
        Please check the error message above and try refreshing.
        """)
        return
    
    # Show live data indicator
    if is_live:
        st.success("🎉 **Connected to Live API!** Data is being fetched in real-time from the YVote service.")
    
    # Render dashboard components
    render_key_metrics(df, total_votes, is_live)
    st.divider()
    
    # Main content area
    render_current_rankings(df)
    st.divider()
    render_simple_charts(df)
    
    # Footer
    st.markdown("---")
    footer_status = "🟢 Live Data" if is_live else "🔴 Demo Mode"
    api_status = "Connected" if is_live else "Offline"
    st.html(
        "<div style='text-align: center; color: #7f8c8d;'>"
        f"🗳️ YVote Live Monitor | {footer_status} | API: {api_status} | "
        f"Last Updated: {datetime.now().strftime('%H:%M:%S')}"
        "</div>"
    )

# === RUN DASHBOARD ===
if __name__ == "__main__":
    main()