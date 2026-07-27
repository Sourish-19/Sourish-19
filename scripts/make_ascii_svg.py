import os
import sys
import numpy as np
from PIL import Image

RAMP = " .`:-=+*cs#%@"

def image_to_ascii(img_path, width=100, height=53):
    img = Image.open(img_path).convert("L")
    img_resized = img.resize((width, height), Image.Resampling.LANCZOS)
    arr = np.array(img_resized)
    
    ascii_rows = []
    ramp_len = len(RAMP)
    for y in range(height):
        row_chars = []
        for x in range(width):
            val = arr[y, x]
            idx = int((255 - val) / 255.0 * (ramp_len - 1))
            row_chars.append(RAMP[idx])
        ascii_rows.append("".join(row_chars))
    return ascii_rows

def make_ascii_svg(input_path="source-prepped.png", output_path="sourish-ascii.svg", width=100, height=53):
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found. Run prep_photo.py first.")
        sys.exit(1)

    ascii_rows = image_to_ascii(input_path, width=width, height=height)
    
    char_w = 3.65
    line_h = 5.6
    margin_x = 10
    margin_y = 15
    
    svg_width = int(margin_x * 2 + width * char_w)
    svg_height = int(margin_y * 2 + height * line_h)
    
    row_dur = 0.04  # duration per row wipe
    start_delay = 0.2
    
    svg_lines = []
    svg_lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="{svg_width}" height="{svg_height}">')
    svg_lines.append('<style>')
    svg_lines.append('  .ascii-text { font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace; font-size: 4.2px; fill: #8b949e; white-space: pre; }')
    svg_lines.append('  .bg { fill: #0d1117; rx: 6px; }')
    svg_lines.append('  .cursor { fill: #58a6ff; }')
    svg_lines.append('</style>')
    svg_lines.append(f'<rect width="{svg_width}" height="{svg_height}" class="bg" />')
    
    svg_lines.append('<defs>')
    for i in range(height):
        y_pos = margin_y + i * line_h - 4
        begin_t = round(start_delay + i * row_dur, 2)
        svg_lines.append(f'  <clipPath id="clip-{i}">')
        svg_lines.append(f'    <rect x="0" y="{y_pos:.1f}" width="0" height="{line_h:.1f}">')
        svg_lines.append(f'      <animate attributeName="width" from="0" to="{svg_width}" dur="{row_dur}s" begin="{begin_t}s" fill="freeze" />')
        svg_lines.append('    </rect>')
        svg_lines.append('  </clipPath>')
    svg_lines.append('</defs>')

    # ASCII text rows with clipPaths
    for i, row_str in enumerate(ascii_rows):
        y_pos = margin_y + (i + 1) * line_h - 1.2
        # Escape XML characters in row_str
        row_escaped = row_str.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        svg_lines.append(f'<g clip-path="url(#clip-{i})">')
        svg_lines.append(f'  <text x="{margin_x}" y="{y_pos:.1f}" class="ascii-text">{row_escaped}</text>')
        svg_lines.append('</g>')

    # Cursor riding the animation edge
    for i in range(height):
        y_pos = margin_y + i * line_h + 0.5
        begin_t = round(start_delay + i * row_dur, 2)
        svg_lines.append(f'<rect y="{y_pos:.1f}" width="4" height="{line_h:.1f}" class="cursor">')
        svg_lines.append(f'  <animate attributeName="x" from="{margin_x}" to="{svg_width - margin_x}" dur="{row_dur}s" begin="{begin_t}s" fill="freeze" />')
        svg_lines.append(f'  <animate attributeName="opacity" values="1;1;0" keyTimes="0;0.99;1" dur="{row_dur}s" begin="{begin_t}s" fill="freeze" />')
        svg_lines.append('</rect>')

    svg_lines.append('</svg>')
    
    content = "\n".join(svg_lines)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    # Also write to avi-ascii.svg for exact compatibility with article filename
    with open("avi-ascii.svg", "w", encoding="utf-8") as f:
        f.write(content)

    print(f"ASCII SVG saved to {output_path} and avi-ascii.svg")

if __name__ == "__main__":
    inp = sys.argv[1] if len(sys.argv) > 1 else "source-prepped.png"
    make_ascii_svg(inp)
