"""Site/directory dimension analyzer and plotter.

Reusable module: scans any directory tree, computes size/count/depth metrics,
and generates a self-contained interactive HTML report with SVG charts.

Usage:
    from src.dimensions import scan_directory, generate_dimension_report

    data = scan_directory("/path/to/site")
    generate_dimension_report(data, Path("reports/dimensions.html"))

CLI:
    uv run python -m src dimensions /path/to/dir [--output report.html] [--open]
"""
from __future__ import annotations

import os
import json
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import date


# ── Data model ──────────────────────────────────────────────

@dataclass
class FileInfo:
    path: str
    name: str
    extension: str
    size: int
    section: str  # top-level directory


@dataclass
class SectionInfo:
    name: str
    path: str
    total_size: int = 0
    file_count: int = 0
    files_by_ext: dict[str, int] = field(default_factory=dict)
    size_by_ext: dict[str, int] = field(default_factory=dict)
    largest_file: str = ""
    largest_file_size: int = 0


@dataclass
class DimensionData:
    root: str
    scan_date: str
    total_size: int = 0
    total_files: int = 0
    total_dirs: int = 0
    max_depth: int = 0
    sections: list[SectionInfo] = field(default_factory=list)
    files_by_ext: dict[str, int] = field(default_factory=dict)
    size_by_ext: dict[str, int] = field(default_factory=dict)
    largest_files: list[dict] = field(default_factory=list)
    all_files: list[FileInfo] = field(default_factory=list)


# ── Scanner ─────────────────────────────────────────────────

def scan_directory(root: str, exclude: list[str] | None = None) -> DimensionData:
    """Walk a directory tree and collect dimension metrics."""
    if exclude is None:
        exclude = [".git", ".venv", "node_modules", "__pycache__", ".DS_Store"]

    root_path = Path(root).resolve()
    data = DimensionData(root=str(root_path), scan_date=date.today().isoformat())

    section_map: dict[str, SectionInfo] = {}
    all_files: list[dict] = []

    for dirpath, dirnames, filenames in os.walk(root_path):
        # Filter excluded dirs in-place
        dirnames[:] = [d for d in dirnames if d not in exclude]

        rel_dir = Path(dirpath).relative_to(root_path)
        depth = len(rel_dir.parts)
        data.max_depth = max(data.max_depth, depth)
        data.total_dirs += 1

        # Determine section (top-level directory)
        section = rel_dir.parts[0] if rel_dir.parts else "(root)"

        if section not in section_map:
            section_map[section] = SectionInfo(
                name=section,
                path=str(rel_dir.parts[0]) if rel_dir.parts else ".",
            )

        for fname in filenames:
            if fname in exclude:
                continue

            fpath = Path(dirpath) / fname
            try:
                size = fpath.stat().st_size
            except OSError:
                continue

            ext = fpath.suffix.lstrip(".").lower() or "(none)"
            rel_path = str(fpath.relative_to(root_path))

            data.total_files += 1
            data.total_size += size

            # Global ext counts
            data.files_by_ext[ext] = data.files_by_ext.get(ext, 0) + 1
            data.size_by_ext[ext] = data.size_by_ext.get(ext, 0) + size

            # Section counts
            si = section_map[section]
            si.total_size += size
            si.file_count += 1
            si.files_by_ext[ext] = si.files_by_ext.get(ext, 0) + 1
            si.size_by_ext[ext] = si.size_by_ext.get(ext, 0) + size
            if size > si.largest_file_size:
                si.largest_file = rel_path
                si.largest_file_size = size

            all_files.append({"path": rel_path, "name": fname, "ext": ext, "size": size, "section": section})

    # Sort and finalize
    all_files.sort(key=lambda f: f["size"], reverse=True)
    data.largest_files = all_files[:25]
    data.sections = sorted(section_map.values(), key=lambda s: s.total_size, reverse=True)

    return data


# ── Chart HTML generator ────────────────────────────────────

def _fmt_size(b: int) -> str:
    if b >= 1_048_576:
        return f"{b / 1_048_576:.1f} MB"
    if b >= 1024:
        return f"{b / 1024:.1f} KB"
    return f"{b} B"


def generate_dimension_report(data: DimensionData, output: Path, title: str | None = None):
    """Generate a self-contained HTML report with interactive SVG charts."""
    if title is None:
        title = f"Dimensions — {Path(data.root).name}"

    # Prepare chart data as JSON for the JS
    sections_json = json.dumps([
        {"name": s.name, "size": s.total_size, "files": s.file_count,
         "size_fmt": _fmt_size(s.total_size), "largest": s.largest_file}
        for s in data.sections if s.total_size > 0
    ])

    ext_json = json.dumps(
        sorted(
            [{"ext": k, "size": v, "count": data.files_by_ext.get(k, 0), "size_fmt": _fmt_size(v)}
             for k, v in data.size_by_ext.items()],
            key=lambda x: x["size"], reverse=True,
        )
    )

    top_files_json = json.dumps([
        {"path": f["path"], "size": f["size"], "size_fmt": _fmt_size(f["size"]),
         "ext": f["ext"], "section": f["section"]}
        for f in data.largest_files
    ])

    # Section treemap data
    treemap_json = json.dumps([
        {"name": s.name, "size": s.total_size, "files": s.file_count, "size_fmt": _fmt_size(s.total_size)}
        for s in data.sections if s.total_size > 0
    ])

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
:root {{
  --bg: #07070f;
  --surface: rgba(255,255,255,0.035);
  --surface2: rgba(255,255,255,0.055);
  --border: rgba(255,255,255,0.07);
  --text: #e8e8f4;
  --muted: rgba(232,232,244,0.45);
  --dim: rgba(232,232,244,0.25);
  --accent: #7aa2f7;
  --accent2: #bb9af7;
  --green: #9ece6a;
  --amber: #e0af68;
  --red: #f7768e;
  --teal: #73daca;
  --mono: 'SF Mono', 'Fira Code', 'JetBrains Mono', Consolas, monospace;
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
  background: var(--bg);
  color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}}
h1 {{ font-size: 1.6rem; font-weight: 600; margin-bottom: 0.3rem; }}
.subtitle {{ color: var(--muted); font-size: 0.85rem; margin-bottom: 2rem; }}
.kpi-row {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 1rem;
  margin-bottom: 2.5rem;
}}
.kpi {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.2rem;
}}
.kpi-value {{
  font-size: 1.8rem;
  font-weight: 700;
  font-family: var(--mono);
  color: var(--accent);
}}
.kpi-label {{
  font-size: 0.75rem;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-top: 0.3rem;
}}
.chart-grid {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 2rem;
}}
@media (max-width: 900px) {{
  .chart-grid {{ grid-template-columns: 1fr; }}
}}
.chart-card {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.5rem;
}}
.chart-card h2 {{
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}}
.chart-card.full {{ grid-column: 1 / -1; }}
svg text {{ font-family: var(--mono); }}
.bar-label {{ fill: var(--text); font-size: 11px; }}
.bar-value {{ fill: var(--muted); font-size: 10px; }}
.treemap-cell {{
  stroke: var(--bg);
  stroke-width: 2;
  cursor: pointer;
  transition: opacity 0.15s;
}}
.treemap-cell:hover {{ opacity: 0.85; }}
.treemap-text {{
  fill: var(--bg);
  font-size: 11px;
  font-weight: 600;
  pointer-events: none;
}}
.treemap-size {{
  fill: rgba(0,0,0,0.6);
  font-size: 9px;
  pointer-events: none;
}}
.file-table {{
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8rem;
}}
.file-table th {{
  text-align: left;
  color: var(--muted);
  font-weight: 500;
  padding: 0.5rem 0.8rem;
  border-bottom: 1px solid var(--border);
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}}
.file-table td {{
  padding: 0.4rem 0.8rem;
  border-bottom: 1px solid rgba(255,255,255,0.03);
  font-family: var(--mono);
  font-size: 0.75rem;
}}
.file-table tr:hover td {{ background: var(--surface2); }}
.ext-badge {{
  display: inline-block;
  padding: 1px 6px;
  border-radius: 4px;
  font-size: 0.65rem;
  font-weight: 600;
}}
.size-bar {{
  height: 6px;
  border-radius: 3px;
  background: var(--accent);
  opacity: 0.6;
}}
.tooltip {{
  position: fixed;
  background: rgba(15,23,42,0.95);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.6rem 0.8rem;
  font-size: 0.75rem;
  pointer-events: none;
  z-index: 100;
  display: none;
  backdrop-filter: blur(8px);
}}
.tooltip .tt-label {{ color: var(--muted); font-size: 0.65rem; }}
.tooltip .tt-value {{ color: var(--text); font-family: var(--mono); }}
</style>
</head>
<body>

<h1>{title}</h1>
<div class="subtitle">{data.root} &mdash; scanned {data.scan_date}</div>

<div class="kpi-row">
  <div class="kpi">
    <div class="kpi-value">{_fmt_size(data.total_size)}</div>
    <div class="kpi-label">Total Content</div>
  </div>
  <div class="kpi">
    <div class="kpi-value">{data.total_files}</div>
    <div class="kpi-label">Files</div>
  </div>
  <div class="kpi">
    <div class="kpi-value">{data.total_dirs}</div>
    <div class="kpi-label">Directories</div>
  </div>
  <div class="kpi">
    <div class="kpi-value">{data.max_depth}</div>
    <div class="kpi-label">Max Depth</div>
  </div>
  <div class="kpi">
    <div class="kpi-value">{len(data.size_by_ext)}</div>
    <div class="kpi-label">File Types</div>
  </div>
  <div class="kpi">
    <div class="kpi-value">{len([s for s in data.sections if s.total_size > 0])}</div>
    <div class="kpi-label">Sections</div>
  </div>
</div>

<div class="chart-grid">
  <div class="chart-card full">
    <h2>Treemap &mdash; Size by Section</h2>
    <div id="treemap"></div>
  </div>

  <div class="chart-card">
    <h2>Size by Section</h2>
    <div id="section-bars"></div>
  </div>

  <div class="chart-card">
    <h2>Size by File Type</h2>
    <div id="ext-bars"></div>
  </div>

  <div class="chart-card">
    <h2>File Count by Type</h2>
    <div id="ext-count-bars"></div>
  </div>

  <div class="chart-card">
    <h2>Section File Count</h2>
    <div id="section-count-bars"></div>
  </div>

  <div class="chart-card full">
    <h2>Largest Files</h2>
    <table class="file-table" id="file-table">
      <thead><tr><th>File</th><th>Section</th><th>Type</th><th>Size</th><th></th></tr></thead>
      <tbody></tbody>
    </table>
  </div>
</div>

<div class="tooltip" id="tooltip">
  <div class="tt-label"></div>
  <div class="tt-value"></div>
</div>

<script>
// ── Data ──────────────────────────────────
const sections = {sections_json};
const extensions = {ext_json};
const topFiles = {top_files_json};
const treemapData = {treemap_json};
const totalSize = {data.total_size};

const COLORS = ['#7aa2f7','#bb9af7','#9ece6a','#e0af68','#f7768e','#73daca',
  '#ff9e64','#2ac3de','#c0caf5','#a9b1d6','#565f89','#414868'];

function extColor(ext) {{
  const map = {{html:'#7aa2f7', pdf:'#f7768e', md:'#9ece6a', js:'#e0af68',
    py:'#bb9af7', css:'#73daca', json:'#ff9e64', yaml:'#2ac3de',
    tex:'#c0caf5', ics:'#a9b1d6', sh:'#565f89'}};
  return map[ext] || '#414868';
}}

// ── Tooltip ───────────────────────────────
const tt = document.getElementById('tooltip');
function showTip(e, label, value) {{
  tt.style.display = 'block';
  tt.querySelector('.tt-label').textContent = label;
  tt.querySelector('.tt-value').textContent = value;
  tt.style.left = (e.clientX + 12) + 'px';
  tt.style.top = (e.clientY - 10) + 'px';
}}
function hideTip() {{ tt.style.display = 'none'; }}

// ── Horizontal bar chart (reusable) ──────
function hbar(container, data, labelKey, valueKey, fmtKey, colorFn, maxItems) {{
  const items = data.slice(0, maxItems || 15);
  const maxVal = Math.max(...items.map(d => d[valueKey]));
  const barH = 26, gap = 4, labelW = 120, valueW = 70;
  const w = 500, chartW = w - labelW - valueW;
  const h = items.length * (barH + gap);

  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('viewBox', `0 0 ${{w}} ${{h}}`);
  svg.setAttribute('width', '100%');
  svg.style.maxHeight = h + 'px';

  items.forEach((d, i) => {{
    const y = i * (barH + gap);
    const barW = maxVal > 0 ? (d[valueKey] / maxVal) * chartW : 0;
    const color = typeof colorFn === 'function' ? colorFn(d) : colorFn;

    // Label
    const lbl = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    lbl.setAttribute('x', labelW - 8);
    lbl.setAttribute('y', y + barH / 2 + 4);
    lbl.setAttribute('text-anchor', 'end');
    lbl.setAttribute('class', 'bar-label');
    lbl.textContent = d[labelKey].length > 16 ? d[labelKey].slice(0, 16) + '...' : d[labelKey];
    svg.appendChild(lbl);

    // Bar
    const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    rect.setAttribute('x', labelW);
    rect.setAttribute('y', y + 2);
    rect.setAttribute('width', Math.max(barW, 2));
    rect.setAttribute('height', barH - 4);
    rect.setAttribute('rx', 4);
    rect.setAttribute('fill', color);
    rect.setAttribute('opacity', '0.7');
    rect.addEventListener('mouseenter', e => showTip(e, d[labelKey], d[fmtKey]));
    rect.addEventListener('mousemove', e => showTip(e, d[labelKey], d[fmtKey]));
    rect.addEventListener('mouseleave', hideTip);
    svg.appendChild(rect);

    // Value
    const val = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    val.setAttribute('x', labelW + Math.max(barW, 2) + 6);
    val.setAttribute('y', y + barH / 2 + 4);
    val.setAttribute('class', 'bar-value');
    val.textContent = d[fmtKey];
    svg.appendChild(val);
  }});

  document.getElementById(container).appendChild(svg);
}}

// ── Treemap (squarified) ─────────────────
function treemap(container, data, totalSize) {{
  const el = document.getElementById(container);
  const W = el.clientWidth || 800;
  const H = Math.max(300, W * 0.4);

  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('viewBox', `0 0 ${{W}} ${{H}}`);
  svg.setAttribute('width', '100%');

  // Simple slice-and-dice layout
  const sorted = [...data].sort((a, b) => b.size - a.size);
  let x = 0, y = 0, w = W, h = H;
  const rects = [];

  function layout(items, x, y, w, h, horizontal) {{
    if (items.length === 0) return;
    if (items.length === 1) {{
      rects.push({{ ...items[0], x, y, w, h }});
      return;
    }}
    const total = items.reduce((s, d) => s + d.size, 0);
    let sum = 0;
    let split = 0;
    for (let i = 0; i < items.length; i++) {{
      sum += items[i].size;
      if (sum >= total / 2) {{ split = i + 1; break; }}
    }}
    if (split === 0) split = 1;
    const ratio = items.slice(0, split).reduce((s, d) => s + d.size, 0) / total;

    if (horizontal) {{
      layout(items.slice(0, split), x, y, w * ratio, h, !horizontal);
      layout(items.slice(split), x + w * ratio, y, w * (1 - ratio), h, !horizontal);
    }} else {{
      layout(items.slice(0, split), x, y, w, h * ratio, !horizontal);
      layout(items.slice(split), x, y + h * ratio, w, h * (1 - ratio), !horizontal);
    }}
  }}

  layout(sorted, 0, 0, W, H, W > H);

  rects.forEach((d, i) => {{
    const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    rect.setAttribute('x', d.x + 1);
    rect.setAttribute('y', d.y + 1);
    rect.setAttribute('width', Math.max(d.w - 2, 0));
    rect.setAttribute('height', Math.max(d.h - 2, 0));
    rect.setAttribute('rx', 4);
    rect.setAttribute('fill', COLORS[i % COLORS.length]);
    rect.setAttribute('class', 'treemap-cell');
    rect.addEventListener('mouseenter', e => showTip(e, d.name, d.size_fmt + ' / ' + d.files + ' files'));
    rect.addEventListener('mousemove', e => showTip(e, d.name, d.size_fmt + ' / ' + d.files + ' files'));
    rect.addEventListener('mouseleave', hideTip);
    svg.appendChild(rect);

    if (d.w > 60 && d.h > 30) {{
      const txt = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      txt.setAttribute('x', d.x + d.w / 2);
      txt.setAttribute('y', d.y + d.h / 2 - 2);
      txt.setAttribute('text-anchor', 'middle');
      txt.setAttribute('class', 'treemap-text');
      txt.textContent = d.name;
      svg.appendChild(txt);

      const sz = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      sz.setAttribute('x', d.x + d.w / 2);
      sz.setAttribute('y', d.y + d.h / 2 + 12);
      sz.setAttribute('text-anchor', 'middle');
      sz.setAttribute('class', 'treemap-size');
      sz.textContent = d.size_fmt;
      svg.appendChild(sz);
    }}
  }});

  el.appendChild(svg);
}}

// ── File table ────────────────────────────
function fileTable(data) {{
  const tbody = document.querySelector('#file-table tbody');
  const maxSize = data[0]?.size || 1;
  data.forEach(f => {{
    const tr = document.createElement('tr');
    const pct = ((f.size / maxSize) * 100).toFixed(0);
    tr.innerHTML = `
      <td style="color:var(--text);max-width:300px;overflow:hidden;text-overflow:ellipsis">${{f.path}}</td>
      <td style="color:var(--muted)">${{f.section}}</td>
      <td><span class="ext-badge" style="background:${{extColor(f.ext)}};color:var(--bg)">${{f.ext}}</span></td>
      <td style="text-align:right">${{f.size_fmt}}</td>
      <td style="width:120px"><div class="size-bar" style="width:${{pct}}%"></div></td>
    `;
    tbody.appendChild(tr);
  }});
}}

// ── Render all ────────────────────────────
treemap('treemap', treemapData, totalSize);

hbar('section-bars', sections, 'name', 'size', 'size_fmt',
     (d) => COLORS[sections.indexOf(d) % COLORS.length], 15);

hbar('ext-bars', extensions, 'ext', 'size', 'size_fmt',
     (d) => extColor(d.ext), 12);

// Count charts need formatted count
const extWithCount = extensions.map(d => ({{...d, count_fmt: d.count + ' files'}}));
hbar('ext-count-bars', extWithCount, 'ext', 'count', 'count_fmt',
     (d) => extColor(d.ext), 12);

const secWithCount = sections.map(d => ({{...d, files_fmt: d.files + ' files'}}));
hbar('section-count-bars', secWithCount, 'name', 'files', 'files_fmt',
     (d) => COLORS[sections.indexOf(d) % COLORS.length], 15);

fileTable(topFiles);
</script>
</body>
</html>"""

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html)
