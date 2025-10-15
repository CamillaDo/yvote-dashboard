#!/usr/bin/env python3
"""
YVote Monitoring System Launcher
===============================

This script helps you start both the data tracker and the dashboard
simultaneously for complete monitoring solution.

Usage:
    python start_monitoring.py
"""

import subprocess
import sys
import time
import signal
import threading
from pathlib import Path

def check_requirements():
    """Check if all required packages are installed"""
    required_packages = ['streamlit', 'plotly', 'pandas', 'numpy']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstall missing packages with:")
        print("   pip install -r requirements.txt")
        return False
    
    print("✅ All required packages are installed")
    return True

def check_tracker_script():
    """Check if the tracker script exists"""
    tracker_path = Path("track_yvote_v3_1.py")
    if not tracker_path.exists():
        print(f"❌ Tracker script not found: {tracker_path}")
        print("Make sure 'track_yvote_v3_1.py' is in the current directory")
        return False
    
    print("✅ Tracker script found")
    return True

def start_tracker():
    """Start the YVote tracker in a separate process"""
    print("🚀 Starting YVote tracker...")
    try:
        process = subprocess.Popen(
            [sys.executable, "track_yvote_v3_1.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return process
    except Exception as e:
        print(f"❌ Failed to start tracker: {e}")
        return None

def start_dashboard():
    """Start the Streamlit dashboard"""
    print("🚀 Starting dashboard...")
    try:
        # Give the tracker a moment to start
        time.sleep(2)
        
        process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "yvote_dashboard.py", "--server.headless", "true"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return process
    except Exception as e:
        print(f"❌ Failed to start dashboard: {e}")
        return None

def monitor_process(process, name):
    """Monitor a process and log its output"""
    try:
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(f"[{name}] {output.strip()}")
    except Exception as e:
        print(f"[{name}] Monitoring error: {e}")

def main():
    """Main launcher function"""
    print("=" * 60)
    print("🗳️  YVote Live Monitoring System Launcher")
    print("=" * 60)
    
    # Check prerequisites
    if not check_requirements():
        sys.exit(1)
    
    if not check_tracker_script():
        sys.exit(1)
    
    print("\n📋 Starting monitoring system...")
    
    tracker_process = None
    dashboard_process = None
    
    try:
        # Start tracker
        tracker_process = start_tracker()
        if not tracker_process:
            print("❌ Failed to start tracker")
            sys.exit(1)
        
        # Start dashboard
        dashboard_process = start_dashboard()
        if not dashboard_process:
            print("❌ Failed to start dashboard")
            if tracker_process:
                tracker_process.terminate()
            sys.exit(1)
        
        print("\n✅ Monitoring system started successfully!")
        print("\n📊 Dashboard: http://localhost:8501")
        print("🔧 Tracker: Running in background")
        print("\nPress Ctrl+C to stop both services\n")
        
        # Start monitoring threads
        tracker_thread = threading.Thread(
            target=monitor_process, 
            args=(tracker_process, "TRACKER"), 
            daemon=True
        )
        tracker_thread.start()
        
        # Keep main process alive and monitor dashboard
        while True:
            # Check if processes are still running
            if tracker_process.poll() is not None:
                print("❌ Tracker process stopped unexpectedly")
                break
            
            if dashboard_process.poll() is not None:
                print("❌ Dashboard process stopped unexpectedly")
                break
            
            time.sleep(5)
    
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping monitoring system...")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    finally:
        # Clean shutdown
        if tracker_process:
            print("🔄 Stopping tracker...")
            tracker_process.terminate()
            try:
                tracker_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                tracker_process.kill()
        
        if dashboard_process:
            print("🔄 Stopping dashboard...")
            dashboard_process.terminate()
            try:
                dashboard_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                dashboard_process.kill()
        
        print("✅ Monitoring system stopped")

if __name__ == "__main__":
    main()