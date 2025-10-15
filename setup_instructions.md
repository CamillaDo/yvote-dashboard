# YVote Dashboard Setup Instructions

## 🎯 Quick Setup (3 Steps)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the System
```bash
python start_monitoring.py
```

### Step 3: Open Dashboard
Navigate to: http://localhost:8501

---

## 📋 Detailed Setup Guide

### Prerequisites
- Python 3.8 or higher
- Your existing `track_yvote_v3_1.py` script
- Internet connection (for initial package installation)

### Installation Steps

**1. Check Python Version**
```bash
python --version
# Should show Python 3.8+
```

**2. Install Required Packages**
```bash
# Option A: Install from requirements file
pip install -r requirements.txt

# Option B: Install individually
pip install streamlit plotly pandas numpy requests urllib3
```

**3. Verify Installation**
```bash
python -c "import streamlit, plotly, pandas; print('✅ All packages installed')"
```

**4. Check File Structure**
Ensure you have these files in the same directory:
```
├── track_yvote_v3_1.py      # Your existing tracker
├── yvote_dashboard.py       # Main dashboard
├── dashboard_standalone.py  # Standalone version
├── start_monitoring.py      # Launcher script
├── requirements.txt         # Dependencies
└── README.md               # Documentation
```

### Running Options

**Option 1: Automatic (Recommended)**
```bash
python start_monitoring.py
```
- Starts both tracker and dashboard automatically
- Provides status monitoring
- Handles shutdown gracefully

**Option 2: Manual**
```bash
# Terminal 1: Start tracker
python track_yvote_v3_1.py

# Terminal 2: Start dashboard (after tracker has run for a few minutes)
streamlit run yvote_dashboard.py
```

**Option 3: Dashboard Only (Historical Data)**
```bash
streamlit run dashboard_standalone.py
```
- Use this if you already have CSV data
- Works without running the tracker

### First Run Experience

**1. Start the System**
```bash
python start_monitoring.py
```

**2. Wait for Initial Data**
- The tracker needs to collect at least one data point
- This takes about 5 minutes (tracker runs every 300 seconds)
- You'll see "No Data Available" until first collection

**3. Access Dashboard**
- Open browser to http://localhost:8501
- The dashboard will auto-refresh every 30 seconds
- Use sidebar controls to customize display

---

## 🔧 Configuration Options

### Dashboard Settings

**Auto-Refresh Configuration:**
- 30 seconds (default)
- 60 seconds
- 2 minutes
- 5 minutes

**Time Range Options:**
- Last 6 hours
- Last 12 hours
- Last 24 hours (default)
- Last 48 hours
- Last 72 hours

**Display Customization:**
- Toggle auto-refresh on/off
- Select specific candidates to display
- Choose different chart time ranges
- Download data as CSV

### Tracker Integration

The dashboard reads from files created by your tracker:
- `yvote_v3_log.csv` - Main voting data
- `state_v3.json` - Current state and totals
- `dumps/raw_latest.txt` - Latest API response

**No modifications needed** to your existing tracker script!

---

## 🐛 Troubleshooting

### Common Issues & Solutions

**Issue: "No Data Available"**
```
Causes:
- Tracker hasn't run yet
- CSV file doesn't exist
- Tracker encountered errors

Solutions:
1. Wait 5-10 minutes for first data collection
2. Check if track_yvote_v3_1.py is running
3. Look for yvote_v3_log.csv file
4. Check tracker console for errors
```

**Issue: "ModuleNotFoundError"**
```
Cause: Missing required packages

Solution:
pip install -r requirements.txt

If still failing:
pip install --upgrade pip
pip install streamlit plotly pandas numpy
```

**Issue: "Dashboard won't start"**
```
Causes:
- Port 8501 already in use
- Streamlit not installed properly

Solutions:
1. Kill other Streamlit processes:
   pkill -f streamlit
   
2. Use different port:
   streamlit run yvote_dashboard.py --server.port 8502
   
3. Reinstall Streamlit:
   pip uninstall streamlit
   pip install streamlit
```

**Issue: "Permission denied" on files**
```
Cause: File permission issues

Solution:
chmod 644 yvote_v3_log.csv state_v3.json
chmod 755 *.py
```

**Issue: "Charts not displaying"**
```
Causes:
- Browser compatibility
- JavaScript disabled
- Plotly installation issues

Solutions:
1. Try different browser (Chrome, Firefox, Safari)
2. Enable JavaScript
3. Clear browser cache
4. Reinstall Plotly: pip install --upgrade plotly
```

### Verification Steps

**1. Check Dependencies**
```bash
python -c "
import streamlit
import plotly
import pandas
import numpy
print('✅ All packages working')
print(f'Streamlit: {streamlit.__version__}')
print(f'Plotly: {plotly.__version__}')
print(f'Pandas: {pandas.__version__}')
"
```

**2. Test Tracker**
```bash
# Run tracker for one cycle
timeout 10 python track_yvote_v3_1.py
# Should create yvote_v3_log.csv
```

**3. Test Dashboard**
```bash
# Start dashboard in test mode
streamlit run dashboard_standalone.py --server.headless true
```

### Performance Optimization

**For Better Performance:**
- Close unnecessary browser tabs
- Use longer auto-refresh intervals
- Limit historical data range
- Archive old CSV data periodically

**Memory Usage:**
- Dashboard uses ~50-100MB RAM
- Tracker uses ~20-50MB RAM
- CSV files grow ~1KB per candidate per update

---

## 🚀 Advanced Setup

### Running on Different Port
```bash
streamlit run yvote_dashboard.py --server.port 8502
```

### Running with Custom Config
Create `.streamlit/config.toml`:
```toml
[server]
port = 8501
headless = true

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
```

### Auto-Start on System Boot (Linux/Mac)

**Create systemd service (Linux):**
```bash
# Create service file
sudo nano /etc/systemd/system/yvote-monitor.service

# Service content:
[Unit]
Description=YVote Monitoring System
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/yvote/directory
ExecStart=/usr/bin/python3 start_monitoring.py
Restart=always

[Install]
WantedBy=multi-user.target

# Enable service
sudo systemctl enable yvote-monitor.service
sudo systemctl start yvote-monitor.service
```

**Create LaunchAgent (macOS):**
```xml
<!-- ~/Library/LaunchAgents/com.yvote.monitor.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.yvote.monitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/start_monitoring.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/path/to/yvote/directory</string>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
```

### Remote Access Setup

**Warning:** Only do this on trusted networks!

```bash
# Allow external connections
streamlit run yvote_dashboard.py --server.address 0.0.0.0

# With basic auth (create .streamlit/secrets.toml):
# [passwords]
# admin = "your-password-here"
```

---

## 📊 Data Management

### Backup Strategy
```bash
# Create backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p backups
cp yvote_v3_log.csv backups/yvote_v3_log_$DATE.csv
cp state_v3.json backups/state_v3_$DATE.json
```

### Data Archival
```bash
# Archive data older than 30 days
python -c "
import pandas as pd
from datetime import datetime, timedelta

df = pd.read_csv('yvote_v3_log.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])
cutoff = datetime.now() - timedelta(days=30)

old_data = df[df['timestamp'] < cutoff]
new_data = df[df['timestamp'] >= cutoff]

old_data.to_csv('archive_data.csv', index=False)
new_data.to_csv('yvote_v3_log.csv', index=False)
print(f'Archived {len(old_data)} records')
"
```

---

## ✅ Final Checklist

Before considering setup complete:

- [ ] Python 3.8+ installed
- [ ] All packages installed successfully
- [ ] `track_yvote_v3_1.py` exists and works
- [ ] Dashboard files are in place
- [ ] Tracker can collect at least one data point
- [ ] Dashboard opens in browser
- [ ] Real-time updates work
- [ ] Charts display correctly
- [ ] Auto-refresh functions
- [ ] CSV export works
- [ ] No error messages in console

## 🎉 Success!

If all checklist items pass, your YVote monitoring system is ready!

**Default URLs:**
- Dashboard: http://localhost:8501
- Alternative: http://127.0.0.1:8501

**Next Steps:**
1. Let the tracker run for a few hours to collect data
2. Explore different dashboard features
3. Set up data backup routine
4. Consider auto-start setup for continuous monitoring