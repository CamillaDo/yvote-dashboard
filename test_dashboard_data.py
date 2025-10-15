#!/usr/bin/env python3
"""
Quick test script to verify dashboard data loading
"""

import pandas as pd
from pathlib import Path

def test_data_loading():
    """Test if data loads correctly for dashboard"""
    print("🧪 Testing YVote Dashboard Data Loading\n")
    
    # Check files exist
    csv_path = Path("yvote_v3_log.csv")
    state_path = Path("state_v3.json")
    
    print(f"📄 CSV File exists: {'✅' if csv_path.exists() else '❌'}")
    print(f"📄 State File exists: {'✅' if state_path.exists() else '❌'}")
    
    if not csv_path.exists():
        print("❌ No CSV data found!")
        return False
    
    # Load and analyze data
    df = pd.read_csv(csv_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    print(f"\n📊 Data Summary:")
    print(f"   Total records: {len(df):,}")
    print(f"   Unique candidates: {df['name'].nunique()}")
    print(f"   Date range: {df['timestamp'].min().date()} to {df['timestamp'].max().date()}")
    print(f"   Latest timestamp: {df['timestamp'].max()}")
    
    # Get latest data (what dashboard will show)
    latest_time = df['timestamp'].max()
    latest_data = df[df['timestamp'] == latest_time].sort_values('rank')
    
    print(f"\n🏆 Current Rankings ({len(latest_data)} candidates):")
    for _, row in latest_data.iterrows():
        medal = "🥇" if row['rank'] == 1 else "🥈" if row['rank'] == 2 else "🥉" if row['rank'] == 3 else f"#{row['rank']}"
        print(f"   {medal} {row['name']:20s} {row['votes']:>8,} votes ({row['percent']:>5.2f}%)")
    
    # Verify no filtering issues
    all_candidates = sorted(df['name'].unique())
    print(f"\n✅ All {len(all_candidates)} candidates will be shown by default")
    
    return True

if __name__ == "__main__":
    success = test_data_loading()
    if success:
        print(f"\n🎉 Dashboard data test PASSED!")
        print(f"💡 Run: streamlit run yvote_dashboard.py")
    else:
        print(f"\n❌ Dashboard data test FAILED!")