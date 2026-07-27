import os
import sys
import json
from datetime import datetime

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

def render_heatmap_svg(json_path="data/contributions.json", output_path="contrib-heatmap.svg"):
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found. Run fetch_contributions.py first.")
        sys.exit(1)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    days = data.get("days", [])
    total_contribs = data.get("total_contributions", 0)
    current_streak = data.get("current_streak", 0)
    longest_streak = data.get("longest_streak", 0)
    best_day = data.get("best_day", {"count": 0})

    svg_w = 860
    svg_h = 215

    margin_left = 45
    margin_top = 48
    box_size = 11
    box_gap = 3.2
    step = box_size + box_gap

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">')
    svg.append('<style>')
    svg.append('  .bg { fill: #0d1117; stroke: #30363d; stroke-width: 1px; rx: 6px; }')
    svg.append('  .title { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace; font-size: 13px; font-weight: 600; fill: #58a6ff; }')
    svg.append('  .label { font-family: "SFMono-Regular", Consolas, monospace; font-size: 10px; fill: #8b949e; }')
    svg.append('  .stats { font-family: "SFMono-Regular", Consolas, monospace; font-size: 11px; fill: #c9d1d9; }')
    svg.append('  .highlight { fill: #39d353; font-weight: bold; }')
    svg.append('  @keyframes diagFade {')
    svg.append('    0% { opacity: 0; transform: scale(0.4) translateY(-10px); }')
    svg.append('    100% { opacity: 1; transform: scale(1) translateY(0); }')
    svg.append('  }')
    svg.append('  .cell { opacity: 0; animation: diagFade 0.35s cubic-bezier(0.16, 1, 0.3, 1) forwards; transform-origin: center; }')
    svg.append('</style>')

    # Background card
    svg.append(f'<rect width="{svg_w}" height="{svg_h}" class="bg" />')

    # Card title
    svg.append(f'<text x="20" y="26" class="title">contrib-heatmap.svg — {total_contribs:,} contributions in the last year</text>')

    # Month labels calculation
    cols = 53
    rows = 7

    # Map days into (col, row)
    # 53 weeks x 7 days
    num_days = len(days)
    grid = [[None for _ in range(rows)] for _ in range(cols)]
    
    # Place days into grid columns
    last_month = -1
    month_positions = []

    for idx, day_info in enumerate(days):
        col = idx // 7
        row = idx % 7
        if col < cols:
            grid[col][row] = day_info
            
            # Detect month label positions
            dt = datetime.strptime(day_info["date"], "%Y-%m-%d")
            if dt.month != last_month:
                last_month = dt.month
                if col not in [m[0] for m in month_positions]:
                    month_positions.append((col, MONTH_NAMES[dt.month - 1]))

    # Render month labels
    for col_idx, m_name in month_positions:
        x_pos = margin_left + col_idx * step
        if x_pos < svg_w - 60:
            svg.append(f'<text x="{x_pos:.1f}" y="{margin_top - 10}" class="label">{m_name}</text>')

    # Render weekday labels (Mon, Wed, Fri)
    weekdays = [(1, "Mon"), (3, "Wed"), (5, "Fri")]
    for r_idx, w_name in weekdays:
        y_pos = margin_top + r_idx * step + 9
        svg.append(f'<text x="{margin_left - 30}" y="{y_pos:.1f}" class="label">{w_name}</text>')

    # Render calendar cells
    for c in range(cols):
        for r in range(rows):
            d_info = grid[c][r]
            x = margin_left + c * step
            y = margin_top + r * step

            if d_info:
                level = d_info.get("level", 0)
                color = PALETTE[min(level, len(PALETTE) - 1)]
                date_str = d_info.get("date", "")
                cnt = d_info.get("count", 0)
                title_str = f"{cnt} contribution{'s' if cnt != 1 else ''} on {date_str}"
            else:
                color = PALETTE[0]
                title_str = "No contributions"

            diag_index = c + r
            delay = round(0.08 + diag_index * 0.009, 3)

            svg.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{box_size}" height="{box_size}" rx="2.5" fill="{color}" class="cell" style="animation-delay: {delay}s;">')
            svg.append(f'  <title>{title_str}</title>')
            svg.append('</rect>')

    # Footer: Stats & Legend
    footer_y = margin_top + rows * step + 24
    
    # Legend (Less -> More)
    legend_x_end = svg_w - 20
    svg.append(f'<text x="{legend_x_end - 130}" y="{footer_y}" class="label">Less</text>')
    for i, color in enumerate(PALETTE):
        lx = legend_x_end - 105 + i * (box_size + 3)
        ly = footer_y - 9
        svg.append(f'<rect x="{lx}" y="{ly}" width="{box_size}" height="{box_size}" rx="2" fill="{color}" />')
    svg.append(f'<text x="{legend_x_end - 15}" y="{footer_y}" class="label">More</text>')

    # Summary Stats on left
    stats_str = f'Streak: <tspan class="highlight">{current_streak} days</tspan> (Best: {longest_streak} days) | Best Day: <tspan class="highlight">{best_day.get("count", 0)} contribs</tspan>'
    svg.append(f'<text x="20" y="{footer_y}" class="stats">{stats_str}</text>')

    svg.append('</svg>')

    content = "\n".join(svg)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Heatmap SVG generated: {output_path}")

if __name__ == "__main__":
    render_heatmap_svg()
