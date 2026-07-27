import os
import sys

def make_info_card(output_path="info-card.svg"):
    is_static = os.environ.get("STATIC", "0") == "1"
    
    width = 490
    height = 320
    
    items = [
        ("sourish@github", "--------------------------------------", "#58a6ff", True),
        ("OS", "Computer Engineering @ B.Tech", "#bc8cff", False),
        ("Role", "UI/UX Designer & GenAI Developer", "#79c0ff", False),
        ("Languages", "Python, TypeScript, JavaScript, Java", "#7ee787", False),
        ("GenAI/ML", "Qwen2.5, RAG, PyTorch, Gemini API, QLoRA", "#ffa657", False),
        ("Frameworks", "React.js, FastAPI, Node.js, MongoDB, Azure", "#d2a8ff", False),
        ("Design", "Figma Design Systems, Usability Prototyping", "#ff7b72", False),
        ("Highlights", "Crafting Serverless AI & Seamless Interfaces", "#e3b341", False),
        ("Motto", '"Creative design, engineered with logical precision."', "#8b949e", False)
    ]
    
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">')
    svg.append('<style>')
    svg.append('  .card-bg { fill: #0d1117; stroke: #30363d; stroke-width: 1px; rx: 6px; }')
    svg.append('  .title-bar { fill: #161b22; rx: 6px 6px 0 0; }')
    svg.append('  .title-text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace; font-size: 12px; fill: #8b949e; font-weight: 600; }')
    svg.append('  .dot { r: 5.5px; }')
    svg.append('  .dot-red { fill: #ff5f56; }')
    svg.append('  .dot-yellow { fill: #ffbd2e; }')
    svg.append('  .dot-green { fill: #27c93f; }')
    svg.append('  .code-text { font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace; font-size: 11.5px; }')
    svg.append('  .key { font-weight: 600; fill: #58a6ff; }')
    svg.append('  .separator { fill: #8b949e; }')
    
    if not is_static:
        svg.append('  @keyframes lineIn {')
        svg.append('    0% { opacity: 0; transform: translateX(-8px); }')
        svg.append('    100% { opacity: 1; transform: translateX(0); }')
        svg.append('  }')
        svg.append('  .animated-line { opacity: 0; animation: lineIn 0.35s cubic-bezier(0.16, 1, 0.3, 1) forwards; }')

    svg.append('</style>')
    
    # Card container
    svg.append(f'<rect width="{width}" height="{height}" class="card-bg" />')
    
    # Title bar
    svg.append(f'<rect width="{width}" height="32" class="title-bar" />')
    svg.append('<circle cx="18" cy="16" class="dot dot-red" />')
    svg.append('<circle cx="34" cy="16" class="dot dot-yellow" />')
    svg.append('<circle cx="50" cy="16" class="dot dot-green" />')
    svg.append(f'<text x="{width / 2}" y="20" text-anchor="middle" class="title-text">sourish@github: ~ (neofetch)</text>')
    
    # Lines content
    start_y = 58
    line_spacing = 26
    
    for i, (key, value, val_color, is_header) in enumerate(items):
        y = start_y + i * line_spacing
        delay = round(0.15 + i * 0.08, 2)
        anim_class = "" if is_static else f' class="animated-line" style="animation-delay: {delay}s;"'
        
        svg.append(f'<g{anim_class}>')
        if is_header:
            svg.append(f'  <text x="20" y="{y}" class="code-text" fill="{val_color}" font-weight="bold">{key}</text>')
            svg.append(f'  <text x="20" y="{y + 14}" class="code-text" fill="#30363d">{value}</text>')
        else:
            svg.append(f'  <text x="20" y="{y}" class="code-text">')
            svg.append(f'    <tspan class="key">{key}</tspan>')
            svg.append(f'    <tspan class="separator"> -&gt; </tspan>')
            svg.append(f'    <tspan fill="{val_color}">{value}</tspan>')
            svg.append('  </text>')
        svg.append('</g>')

    svg.append('</svg>')
    
    content = "\n".join(svg)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"Info card SVG written to {output_path}")

if __name__ == "__main__":
    make_info_card()
