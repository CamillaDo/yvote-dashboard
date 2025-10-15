#!/usr/bin/env python3
# === YVOTE TRACKER V3 - Simplified Calibration ===
"""
New Algorithm:
1. Get ratioVotes from API
2. Calculate votes from ratioVotes × total
3. Enforce monotonic: votes[i] >= votes[i-1]
4. Update total = sum(all votes) / sum(all percentages) × 100

Key insight: Total should match the actual vote counts, not just percentage changes!
"""

import re
import csv
import time
import json
import requests
from datetime import datetime
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# === CONFIGURATION ===
INTERVAL = 300  # Seconds between polls
INITIAL_TOTAL_ESTIMATE = 1017428  # Starting estimate

# API endpoints
REAL_ENDPOINT = (
    "https://yvoting-service.onfan.vn/api/v1/nominations/spotlight"
    "?awardId=58e78a33-c7c9-4bd4-b536-f25fa75b68c2"
)
PROXY_ENDPOINT = (
    "https://r.jina.ai/https://yvoting-service.onfan.vn/api/v1/nominations/spotlight"
    "?awardId=58e78a33-c7c9-4bd4-b536-f25fa75b68c2"
)

# === Global State ===
Path("dumps").mkdir(exist_ok=True)
current_total = INITIAL_TOTAL_ESTIMATE
candidate_votes = {}  # {name: votes}

# === Session Setup ===
session = requests.Session()
retries = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
)
session.mount("https://", HTTPAdapter(max_retries=retries))

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/141",
    "referer": "https://yvote.vn/",
    "origin": "https://yvote.vn",
}

# === Step 1: Fetch Data ===
def fetch_raw():
    """Fetch from API with automatic fallback to proxy"""
    try:
        r = session.get(REAL_ENDPOINT, headers=HEADERS, timeout=20)
        if r.status_code == 200 and r.text.strip():
            Path("dumps/raw_latest.txt").write_text(r.text, encoding="utf-8")
            return r.text
        raise Exception(f"API thật thất bại: {r.status_code}")
    except Exception as e:
        print(f"[CẢNH BÁO] API thật thất bại ({e}), thử proxy...")
        rp = session.get(PROXY_ENDPOINT, headers=HEADERS, timeout=20)
        if rp.status_code != 200 or not rp.text.strip():
            raise Exception(f"Proxy cũng thất bại: {rp.status_code}")
        Path("dumps/raw_latest.txt").write_text(rp.text, encoding="utf-8")
        return rp.text

def extract_ratiovotes(text):
    """Extract candidate ratioVotes from API response"""
    pattern = re.compile(r'"name":"([^"]+)".*?"ratioVotes":([0-9.]+)', re.DOTALL)
    found = pattern.findall(text)

    candidates = {}
    for name, pct_str in found:
        name = name.strip()
        try:
            # Store with high precision (6 decimal places)
            pct = round(float(pct_str), 6)
        except:
            continue

        key = name.upper()
        # Keep highest percentage if duplicates
        if key not in candidates or pct > candidates[key]["percent"]:
            candidates[key] = {"name": name, "percent": pct}

    # Convert to sorted list
    result = list(candidates.values())
    result.sort(key=lambda x: x["percent"], reverse=True)

    # Add ranks
    for i, c in enumerate(result, 1):
        c["rank"] = i

    return result

# === Step 2 & 3: Calibration Algorithm ===
def calibrate_and_calculate_votes(candidates_data):
    """
    Main calibration algorithm:
    1. Calculate votes from percentage × total
    2. Enforce monotonic: votes >= previous_votes
    3. Update total based on actual vote sum
    """
    global current_total, candidate_votes

    # Step 2: Calculate votes from percentages
    calculated_votes = {}
    for c in candidates_data:
        name = c["name"]
        percent = c["percent"]

        # Calculate votes from percentage
        votes = int(round(percent / 100 * current_total))

        # Step 3: Enforce monotonic (votes always increase)
        previous_votes = candidate_votes.get(name, 0)
        votes = max(votes, previous_votes)

        calculated_votes[name] = {
            "rank": c["rank"],
            "name": name,
            "percent": percent,
            "votes": votes
        }

    # Update candidate_votes tracker
    for name, data in calculated_votes.items():
        candidate_votes[name] = data["votes"]

    # Step 3 continued: Update total to match actual vote sum
    # Since we enforced monotonic on individual votes, total must increase too
    total_votes = sum(data["votes"] for data in calculated_votes.values())
    total_percentages = sum(c["percent"] for c in candidates_data)

    if total_percentages > 0:
        # Calculate what total should be based on current vote distribution
        # total = sum(votes) / sum(percentages) × 100
        implied_total = int(round(total_votes / total_percentages * 100))

        # Always use the higher of current_total or implied_total (monotonic)
        if implied_total > current_total:
            old_total = current_total
            current_total = implied_total
            print(f"[HIỆU CHUẨN] Cập nhật tổng phiếu: {old_total:,} → {current_total:,}")
        else:
            # If implied_total is lower, keep current_total and recalculate votes to match
            # This ensures total stays monotonic even when percentages decrease
            current_total = max(current_total, implied_total)

            # Recalculate all votes with the guaranteed monotonic total
            for c in candidates_data:
                name = c["name"]
                percent = c["percent"]
                votes = int(round(percent / 100 * current_total))

                # Still enforce monotonic on individual votes
                previous_votes = candidate_votes.get(name, 0)
                votes = max(votes, previous_votes)

                calculated_votes[name]["votes"] = votes
                candidate_votes[name] = votes

    # Return sorted by rank
    result = list(calculated_votes.values())
    result.sort(key=lambda x: x["rank"])
    return result

# === Step 4: Save to CSV ===
def log_to_csv(data, total, timestamp):
    """Save to CSV log with high precision percentages"""
    path = Path("yvote_v3_log.csv")
    new_file = not path.exists()

    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(["timestamp", "total", "rank", "name", "percent", "votes"])

        ts_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        for row in data:
            # Save percent with 6 decimal places for accuracy
            w.writerow([ts_str, total, row["rank"], row["name"],
                       f"{row['percent']:.6f}", row["votes"]])

def save_state():
    """Save current state to file"""
    state = {
        "current_total": current_total,
        "candidate_votes": candidate_votes
    }
    Path("state_v3.json").write_text(json.dumps(state, indent=2))

def load_state():
    """Load previous state if exists"""
    global current_total, candidate_votes

    state_file = Path("state_v3.json")
    if state_file.exists():
        try:
            state = json.loads(state_file.read_text())
            current_total = state.get("current_total", INITIAL_TOTAL_ESTIMATE)
            candidate_votes = state.get("candidate_votes", {})
            print(f"[THÔNG TIN] Đã tải trạng thái: tổng={current_total:,}, {len(candidate_votes)} ứng viên")
        except:
            print("[CẢNH BÁO] Không thể tải trạng thái, bắt đầu mới")

# === MAIN LOOP ===
def main():
    print("=" * 70)
    print("=== YVOTE TRACKER V3 - SIMPLIFIED CALIBRATION ===")
    print("=" * 70)
    print(f"\nCấu hình:")
    print(f"  - Khoảng thời gian: {INTERVAL} giây ({INTERVAL//60} phút)")
    print(f"  - Ước tính ban đầu: {INITIAL_TOTAL_ESTIMATE:,} phiếu")
    print(f"\nThuật toán:")
    print(f"  1. Lấy ratioVotes từ API")
    print(f"  2. Tính votes = ratioVotes × total")
    print(f"  3. Enforce monotonic: votes >= votes trước")
    print(f"  4. Cập nhật total = sum(votes) / sum(%) × 100")
    print(f"\nKết quả: yvote_v3_log.csv")
    print(f"\nNhấn Ctrl+C để dừng\n")
    print("=" * 70 + "\n")

    # Load previous state
    load_state()

    while True:
        try:
            timestamp = datetime.now()

            # Step 1: Get ratioVotes from API
            raw = fetch_raw()
            candidates_data = extract_ratiovotes(raw)

            if not candidates_data:
                print("[CẢNH BÁO] Không tìm thấy dữ liệu")
                continue

            # Steps 2 & 3: Calibrate and calculate votes
            results = calibrate_and_calculate_votes(candidates_data)

            # Display results (show 2 decimal places for readability)
            print(f"[{timestamp.strftime('%H:%M:%S')}] Tổng: {current_total:,} phiếu ({len(results)} ứng viên)")
            for r in results:
                # Display with 2 decimals, but internally we use 6 decimals
                print(f"  {r['rank']:>2}. {r['name']:20s} {r['percent']:>6.2f}% = {r['votes']:>8,} phiếu")

            # Step 4: Save to CSV
            log_to_csv(results, current_total, timestamp)

            # Save state
            save_state()

            print(f"\n[ĐỢI] Cập nhật tiếp theo sau {INTERVAL} giây...\n")

        except KeyboardInterrupt:
            print("\n\n[DỪNG] Đã dừng bởi người dùng")
            save_state()
            break
        except Exception as e:
            print(f"[LỖI] {e}")
            import traceback
            traceback.print_exc()

        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
