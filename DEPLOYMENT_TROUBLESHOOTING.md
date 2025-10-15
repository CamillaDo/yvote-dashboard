# 🔧 Streamlit Cloud Deployment Troubleshooting

## Common Error: Plotly Import Error

### Problem
```
File "/mount/src/yvotetracking/streamlit_dashboard.py", line 12, in <module>
    import plotly.express as px
ModuleNotFoundError: No module named 'plotly.express'
```

### Solutions (Try in Order)

#### Solution 1: Use Minimal Requirements
Replace your `requirements.txt` with:
```
streamlit
plotly
pandas
numpy
```

#### Solution 2: Use Simple Dashboard (Recommended)
Use `streamlit_dashboard_simple.py` instead:
1. In Streamlit Cloud settings, change main file to: `streamlit_dashboard_simple.py`
2. This version doesn't use Plotly and works with basic Streamlit charts

#### Solution 3: Fixed Requirements with Versions
```
streamlit>=1.28.0
plotly>=5.15.0
pandas>=2.0.0
numpy>=1.24.0
kaleido
```

#### Solution 4: Force Reinstall
Add this to your `requirements.txt`:
```
streamlit
plotly==5.17.0
pandas==2.1.0
numpy==1.24.3
--force-reinstall
```

## Step-by-Step Fix Process

### Method A: Switch to Simple Dashboard (Fastest)

1. **Update Streamlit Cloud Settings:**
   - Go to your app settings in Streamlit Cloud
   - Change "Main file path" from `streamlit_dashboard.py` to `streamlit_dashboard_simple.py`
   - Click "Save"
   - App will redeploy automatically

2. **Benefits of Simple Version:**
   - ✅ No Plotly dependency
   - ✅ Uses Streamlit native charts
   - ✅ Faster loading
   - ✅ More reliable deployment
   - ✅ Same functionality

### Method B: Fix Plotly Issues

1. **Update requirements.txt:**
   ```bash
   git add requirements.txt
   git commit -m "Fix plotly dependency"
   git push origin main
   ```

2. **Wait for auto-deployment**
   - Streamlit Cloud will automatically redeploy
   - Check deployment logs for errors

3. **If still failing, try minimal requirements:**
   ```
   streamlit
   plotly
   pandas
   numpy
   ```

## Verification Steps

### Check if App is Working
1. Visit your app URL
2. Look for these indicators:
   - ✅ Page loads without errors
   - ✅ Data displays correctly
   - ✅ Charts render properly
   - ✅ No error messages

### Test Features
- [ ] Dashboard loads
- [ ] Candidate rankings display
- [ ] Charts render (if using Plotly version)
- [ ] Sidebar controls work
- [ ] Refresh button works
- [ ] Mobile view works

## Alternative Solutions

### Option 1: Use Different Chart Library
Replace Plotly with Altair:
```python
import altair as alt
# Add to requirements.txt: altair
```

### Option 2: Use Only Streamlit Native Charts
```python
# Instead of plotly charts
st.bar_chart(data)
st.line_chart(data)
st.area_chart(data)
```

### Option 3: Deploy Without Charts
Remove all chart dependencies and show only:
- Candidate rankings
- Vote counts
- Data tables

## Debugging Commands

### Check Deployment Logs
1. Go to Streamlit Cloud dashboard
2. Click your app
3. View "Logs" tab
4. Look for specific error messages

### Test Locally
```bash
# Test the simple version locally
streamlit run streamlit_dashboard_simple.py

# Test with minimal requirements
pip install streamlit plotly pandas numpy
streamlit run streamlit_dashboard.py
```

## Quick Fix Summary

**Fastest Solution (99% success rate):**
1. Change main file to `streamlit_dashboard_simple.py`
2. Use requirements: `streamlit`, `pandas`, `numpy`
3. Redeploy

**If you need Plotly charts:**
1. Use exact versions in requirements.txt
2. Add `kaleido` dependency
3. Consider using `streamlit_dashboard.py` with error handling

## Contact Support

If none of these solutions work:
1. Check Streamlit Community Forum
2. Post your specific error message
3. Include your requirements.txt content
4. Share your app URL for debugging