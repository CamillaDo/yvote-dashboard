# YVote Live Monitoring Dashboard

A real-time web-based dashboard for monitoring YVote tracking data with live updates, trend analysis, and comprehensive visualizations.

## 🌟 Features

### Real-Time Monitoring
- **Live Vote Tracking**: Real-time display of total votes and candidate rankings
- **Auto-Refresh**: Configurable auto-refresh intervals (30s, 60s, 2min, 5min)
- **Status Monitoring**: Visual indicators showing tracker status and last update time

### Data Visualization
- **Interactive Charts**: Vote progression and percentage trends over time
- **Ranking Display**: Live candidate rankings with medal indicators
- **Trend Analysis**: Historical analysis for 1hr, 6hr, and 24hr periods
- **Responsive Design**: Works on desktop, tablet, and mobile devices

### Analytics & Insights
- **Vote Progression Tracking**: Monitor vote changes over time
- **Percentage Share Analysis**: Track how candidate percentages evolve
- **Top Gainers/Losers**: Identify candidates with biggest changes
- **Performance Metrics**: Votes per minute and growth rates

## 📋 Requirements

- Python 3.8+
- Streamlit 1.28.0+
- Plotly 5.15.0+
- Pandas 2.0.0+
- Existing YVote tracker script (`track_yvote_v3_1.py`)

## 🚀 Quick Start

### Option 1: Automatic Setup (Recommended)
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start both tracker and dashboard
python start_monitoring.py
```

The dashboard will be available at: http://localhost:8501

### Option 2: Manual Setup
```bash
# 1. Install dependencies
pip install streamlit plotly pandas numpy

# 2. Start the tracker (in one terminal)
python track_yvote_v3_1.py

# 3. Start the dashboard (in another terminal)
streamlit run yvote_dashboard.py
```

### Option 3: View Historical Data Only
```bash
# Run standalone dashboard (works with existing CSV data)
streamlit run dashboard_standalone.py
```

## 📁 File Structure

```
yvote-monitoring/
├── track_yvote_v3_1.py      # Original tracker script
├── yvote_dashboard.py       # Main real-time dashboard
├── dashboard_standalone.py  # Historical data analyzer
├── start_monitoring.py      # Automated launcher
├── requirements.txt         # Python dependencies
├── README.md               # This file
│
├── Data Files (auto-generated):
├── yvote_v3_log.csv        # Voting data log
├── state_v3.json           # Tracker state
└── dumps/                  # API response dumps
```

## 🎛️ Dashboard Components

### 1. Header & Status
- **Real-time Status**: Shows if tracker is running or stopped
- **Last Update Time**: Time since last data collection
- **Visual Indicators**: Green (running) / Red (stopped) status

### 2. Key Metrics Panel
- **Total Votes**: Current total vote count
- **Candidates**: Number of tracked candidates
- **Last Update**: Time since last data refresh
- **Votes/min**: Average voting rate

### 3. Current Rankings
- **Live Rankings**: Real-time candidate positions
- **Medal System**: 🥇🥈🥉 for top 3, numbers for others
- **Vote Counts**: Individual and percentage shares
- **Visual Progress**: Progress bars for vote distribution

### 4. Trend Analysis
- **Multiple Time Periods**: 1hr, 6hr, 24hr analysis
- **Top Gainers**: Candidates with biggest vote increases
- **Percentage Changes**: Tracking share shifts
- **Historical Comparison**: Compare different time periods

### 5. Interactive Charts
- **Vote Progression**: Line charts showing vote growth
- **Percentage Trends**: Share evolution over time
- **Total Votes**: Overall voting activity
- **Time Range Selector**: Filter data by time periods

## ⚙️ Configuration

### Auto-Refresh Settings
- **Intervals**: 30s, 60s, 2min, 5min
- **Toggle**: Enable/disable auto-refresh
- **Manual Refresh**: Force refresh button

### Data Filters
- **Time Range**: Last 6, 12, 24, 48, 72 hours
- **Candidate Selection**: Show/hide specific candidates
- **Data Export**: Download filtered data as CSV

### Display Options
- **Chart Types**: Line charts, bar charts, progress indicators
- **Color Themes**: Automatic color assignment for candidates
- **Responsive Layout**: Adapts to screen size

## 🔧 Troubleshooting

### Common Issues

**Dashboard shows "No Data Available":**
- Ensure `track_yvote_v3_1.py` is running
- Check that `yvote_v3_log.csv` exists
- Verify the tracker has collected at least one data point

**Auto-refresh not working:**
- Check browser console for errors
- Try manual refresh button
- Restart the dashboard

**Charts not displaying:**
- Ensure Plotly is installed: `pip install plotly`
- Check data format in CSV file
- Clear browser cache

**Tracker status shows "Stopped":**
- The tracker hasn't updated files in >10 minutes
- Restart the tracker script
- Check tracker logs for errors

### Performance Tips

**For Better Performance:**
- Use shorter auto-refresh intervals only when needed
- Limit time range for large datasets
- Close unused browser tabs
- Use the standalone version for historical analysis

**For Large Datasets:**
- Consider filtering by date range
- Use the standalone dashboard for historical analysis
- Regularly archive old data files

## 📊 Data Format

The dashboard reads from `yvote_v3_log.csv` with this structure:
```csv
timestamp,total,rank,name,percent,votes
2024-01-15 10:30:00,1017428,1,Candidate A,25.456789,259123
2024-01-15 10:30:00,1017428,2,Candidate B,23.123456,235234
```

State information is stored in `state_v3.json`:
```json
{
  "current_total": 1017428,
  "candidate_votes": {
    "Candidate A": 259123,
    "Candidate B": 235234
  }
}
```

## 🔌 Integration with Existing Tracker

The dashboard is designed to work seamlessly with your existing `track_yvote_v3_1.py` script:

- **Non-intrusive**: No modifications needed to the tracker
- **File-based**: Reads from existing CSV and JSON files
- **Real-time**: Detects new data automatically
- **Backward Compatible**: Works with existing data

## 📱 Mobile Support

The dashboard is fully responsive and works on:
- **Desktop**: Full feature set with multi-column layout
- **Tablet**: Optimized layout with touch-friendly controls
- **Mobile**: Single-column layout with collapsible sections

## 🛡️ Security & Privacy

- **Local Only**: Runs locally, no external data transmission
- **Read-Only**: Dashboard only reads data, doesn't modify tracker
- **No Authentication**: Designed for local/trusted network use
- **Data Privacy**: All voting data stays on your machine

## 📈 Advanced Usage

### Custom Time Ranges
Modify the dashboard to add custom time ranges by editing the time range selector in `yvote_dashboard.py`.

### Additional Metrics
Add custom calculations by modifying the `calculate_trends()` function.

### Export Options
The dashboard supports CSV export. For other formats, modify the download section.

### Styling Customization
Update the CSS in the `st.markdown()` sections to change colors, fonts, and layout.

## 🔄 Updates & Maintenance

### Regular Maintenance
- **Monitor Disk Space**: CSV files grow over time
- **Archive Old Data**: Move old data to backup folders
- **Update Dependencies**: Keep packages up to date
- **Check Performance**: Monitor memory usage for long runs

### Version Updates
- **Backup Data**: Before updating any scripts
- **Test Changes**: Use the standalone version first
- **Monitor Compatibility**: Ensure CSV format compatibility

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify all requirements are met
3. Check the tracker is running and collecting data
4. Review browser console for JavaScript errors

## 🎯 Future Enhancements

Potential improvements for future versions:
- **Real-time WebSocket updates** (instead of file polling)
- **Database storage** (SQLite/PostgreSQL)
- **User authentication and multi-user support**
- **Email/SMS alerts** for significant changes
- **API integration** for external monitoring tools
- **Advanced analytics** and prediction models