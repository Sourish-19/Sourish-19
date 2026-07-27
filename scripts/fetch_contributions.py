import os
import sys
import json
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def fetch_contributions(username="Sourish-19", output_path="data/contributions.json"):
    url = f"https://github.com/users/{username}/contributions"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    print(f"Fetching contribution calendar for {username} from {url}...")
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print(f"Failed to fetch contributions HTML (status code {resp.status_code})")
        sys.exit(1)

    soup = BeautifulSoup(resp.text, "html.parser")
    
    # GitHub renders days as <rect> or <td> with class ContributionCalendar-day
    day_elements = soup.find_all(attrs={"class": re.compile(r"ContributionCalendar-day")})
    
    if not day_elements:
        # Fallback search for data-date attributes
        day_elements = soup.find_all(lambda tag: tag.has_attr("data-date"))

    days = []
    total_contributions = 0

    for el in day_elements:
        date_str = el.get("data-date")
        if not date_str:
            continue
        
        # level: 0..4
        level_str = el.get("data-level", "0")
        try:
            level = int(level_str)
        except ValueError:
            level = 0

        # count: try data-count attribute or tooltips
        count = 0
        if el.has_attr("data-count"):
            try:
                count = int(el["data-count"])
            except ValueError:
                count = 0
        else:
            # Fallback: check inner text or aria-label / tooltip
            id_attr = el.get("id")
            if id_attr:
                tooltip = soup.find(attrs={"for": id_attr})
                if tooltip:
                    match = re.search(r"(\d+)\s+contribution", tooltip.text)
                    if match:
                        count = int(match.group(1))
            
            if count == 0 and level > 0:
                count = level * 2  # estimated fallback if count omitted

        total_contributions += count
        days.append({
            "date": date_str,
            "count": count,
            "level": level
        })

    # Sort by date
    days.sort(key=lambda d: d["date"])

    # Compute streaks
    current_streak = 0
    longest_streak = 0
    temp_streak = 0
    best_day = {"date": "", "count": 0}

    for d in days:
        cnt = d["count"]
        if cnt > best_day["count"]:
            best_day = {"date": d["date"], "count": cnt}
            
        if cnt > 0:
            temp_streak += 1
            if temp_streak > longest_streak:
                longest_streak = temp_streak
        else:
            temp_streak = 0

    # Calculate current streak working backwards from today/latest
    for d in reversed(days):
        if d["count"] > 0:
            current_streak += 1
        else:
            break

    # Calculate total in header text if present
    header = soup.find(re.compile(r"h[23]"), text=re.compile(r"contributions", re.I))
    if header:
        h_match = re.search(r"([\d,]+)\s+contributions", header.text)
        if h_match:
            total_contributions = int(h_match.group(1).replace(",", ""))

    data = {
        "username": username,
        "total_contributions": total_contributions,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "updated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ"),
        "days": days
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"Scraped {len(days)} days ({total_contributions} contributions total). Saved to {output_path}")

if __name__ == "__main__":
    uname = sys.argv[1] if len(sys.argv) > 1 else "Sourish-19"
    fetch_contributions(uname)
