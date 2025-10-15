#!/usr/bin/env python3
"""
Debug version to test API connection
"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import traceback

st.title("🔍 YVote API Debug Dashboard")

# API Configuration
API_ENDPOINT = "https://yvoting-service.onfan.vn/api/v1/nominations/spotlight"
AWARD_ID = "58e78a33-c7c9-4bd4-b536-f25fa75b68c2"

st.write(f"**API Endpoint:** {API_ENDPOINT}")
st.write(f"**Award ID:** {AWARD_ID}")

# Test API Connection
if st.button("🔗 Test API Connection"):
    with st.spinner("Testing API connection..."):
        try:
            response = requests.get(
                API_ENDPOINT,
                params={"awardId": AWARD_ID},
                timeout=10
            )
            
            st.write(f"**Status Code:** {response.status_code}")
            
            if response.status_code == 200:
                st.success("✅ API connection successful!")
                
                data = response.json()
                st.write("**Raw API Response:**")
                st.json(data)
                
                # Extract nominations
                if 'data' in data and 'nominations' in data['data']:
                    nominations = data['data']['nominations']
                    st.write(f"**Found {len(nominations)} candidates:**")
                    
                    # Convert to DataFrame
                    candidates_data = []
                    for i, nom in enumerate(nominations, 1):
                        candidates_data.append({
                            'Rank': i,
                            'Name': nom.get('name', 'Unknown'),
                            'Votes': nom.get('voteCount', 0),
                            'Percent': nom.get('percent', 0.0)
                        })
                    
                    df = pd.DataFrame(candidates_data)
                    st.dataframe(df)
                    
                    # Show chart
                    if not df.empty:
                        st.bar_chart(df.set_index('Name')['Votes'])
                        
                else:
                    st.error("❌ No nominations data found in API response")
                    
            else:
                st.error(f"❌ API Error: {response.status_code}")
                st.write("**Error Response:**")
                st.code(response.text)
                
        except requests.exceptions.Timeout:
            st.error("❌ API request timed out")
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to API server")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.write("**Full Error Details:**")
            st.code(traceback.format_exc())

# Manual data entry for testing
st.divider()
st.subheader("📝 Manual Data Entry (for testing)")

if st.checkbox("Use manual test data"):
    test_data = {
        'Rank': [1, 2, 3, 4, 5],
        'Name': ['HỒ ĐÔNG QUAN', 'CƯỜNG BẠCH', 'PHÚC NGUYÊN', 'LÂM ANH', 'WONBI'],
        'Votes': [592810, 110097, 100132, 55467, 49266],
        'Percent': [58.65, 10.90, 9.92, 5.49, 4.87]
    }
    
    df = pd.DataFrame(test_data)
    st.dataframe(df)
    st.bar_chart(df.set_index('Name')['Votes'])

# Show current time
st.write(f"**Current time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")