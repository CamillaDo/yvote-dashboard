# 🚀 YVote Dashboard Setup Guide - Documents/Yvote8

## Step-by-Step Instructions

### Step 1: Navigate to the Project Directory
```bash
cd ~/Documents/Yvote8
```

### Step 2: Install Required Packages
```bash
pip install -r requirements.txt
```

If you get permission errors, try:
```bash
pip install --user -r requirements.txt
```

### Step 3: Verify Installation
```bash
python -c "import streamlit, plotly, pandas; print('✅ All packages installed successfully!')"
```

### Step 4: Choose Your Launch Method

#### Option A: Automatic Launch (Recommended)
```bash
python start_monitoring.py
```
This will:
- Start your existing tracker in the background
- Launch the dashboard automatically
- Show you the dashboard URL

#### Option B: Dashboard Only (View Existing Data)
Since you already have `yvote_v3_log.csv` with data:
```bash
streamlit run dashboard_standalone.py
```

#### Option C: Manual Launch
```bash
# Terminal 1: Start tracker
python track_yvote_v3_1.py

# Terminal 2: Start dashboard (in a new terminal)
streamlit run yvote_dashboard.py
```

### Step 5: Access the Dashboard
- Open your web browser
- Go to: **http://localhost:8501**
- The dashboard should load with your existing voting data

## 📊 What You'll See

Since you already have data in `yvote_v3_log.csv`, you should immediately see:
- ✅ Total vote counts
- 🏆 Candidate rankings with medal indicators
- 📈 Interactive charts showing vote trends
- 🔍 Trend analysis for different time periods

## 🔧 Quick Troubleshooting

**If you see "ModuleNotFoundError":**
```bash
pip install streamlit plotly pandas numpy
```

**If port 8501 is busy:**
```bash
streamlit run yvote_dashboard.py --server.port 8502
```
Then use http://localhost:8502

**If dashboard shows "No Data Available":**
- You have data files, so this shouldn't happen
- Try refreshing the page
- Check the browser console for errors

## 🎯 Quick Test

Run this to verify everything works:
```bash
# Check your current directory
pwd
# Should show: /Users/dooanh/Documents/Yvote8

# List files to confirm
ls -la
# Should show: track_yvote_v3_1.py, yvote_dashboard.py, yvote_v3_log.csv, etc.

# Start the dashboard with existing data
streamlit run dashboard_standalone.py
```

## ✅ Success Indicators

You'll know it's working when you see:
- 📊 Vote numbers displaying in the dashboard
- 🏆 Candidate names and rankings
- 📈 Charts with your historical voting data
- 🔄 Auto-refresh working (if using the main dashboard)

## 🎉 You're Ready!

Your YVote monitoring dashboard is now set up in ~/Documents/Yvote8 and ready to use!

**Dashboard URL:** http://localhost:8501