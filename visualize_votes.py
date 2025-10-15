#!/usr/bin/env python3
"""
Visualization script for voting data
Plots votes and percent by timestamp with color-coded names
"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# Read the CSV file
df = pd.read_csv('yvote_v3_log.csv')

# Convert timestamp to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Get unique names for color mapping
names = df['name'].unique()

# Create figure with two subplots (one for votes, one for percent)
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

# Define a color palette
colors = plt.cm.tab20(range(len(names)))
color_map = dict(zip(names, colors))

# Plot 1: Votes over time
for name in names:
    name_data = df[df['name'] == name]
    ax1.plot(name_data['timestamp'], name_data['votes'],
             label=name, color=color_map[name], linewidth=2, marker='o', markersize=3)

ax1.set_ylabel('Votes', fontsize=12, fontweight='bold')
ax1.set_title('Votes by Timestamp', fontsize=14, fontweight='bold')
ax1.grid(True, alpha=0.3)
ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)

# Plot 2: Percent over time
for name in names:
    name_data = df[df['name'] == name]
    ax2.plot(name_data['timestamp'], name_data['percent'],
             label=name, color=color_map[name], linewidth=2, marker='o', markersize=3)

ax2.set_xlabel('Timestamp', fontsize=12, fontweight='bold')
ax2.set_ylabel('Percent (%)', fontsize=12, fontweight='bold')
ax2.set_title('Percent by Timestamp', fontsize=14, fontweight='bold')
ax2.grid(True, alpha=0.3)
ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)

# Format x-axis to show dates nicely
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
plt.xticks(rotation=45, ha='right')

# Adjust layout to prevent label cutoff
plt.tight_layout()

# Save the figure
output_file = 'votes_visualization.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"Visualization saved to: {output_file}")
