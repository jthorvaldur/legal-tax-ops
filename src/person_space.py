"""Person information space — semantic retrieval + 3D visualization.

Retrieves all semantically related data points for a person across all Qdrant
collections using vector similarity (not just text match). Generates an
interactive 3D PCA projection.

Usage:
    from src.person_space import build_person_space, generate_person_report

    space = build_person_space("Party A", mode="utility")
    generate_person_report(space, Path("reports/party_a_space.html"))

Modes:
    "full"    — everything above similarity threshold
    "utility" — filter out personal/casual content, keep business, technical,
                concepts, patents, proposals, structured docs
"""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path
from dataclasses import dataclass, field
from datetime import date
from collections import defaultdict

QDRANT_URL = "http://localhost:6333"

# Content classification keywords for utility filtering
PERSONAL_SIGNALS = [
    "fall asleep", "good morning", "good night", "miss you", "love you",
    "hahaha", "lol", "emoji", "birthday", "dinner", "lunch",
    "ear buds", "watching", "listening to",
]

UTILITY_SIGNALS = [
    "patent", "algorithm", "equation", "coherence", "field",
    "company", "LLC", "holdco", "opco", "IP", "licensing",
    "proposal", "research", "publication", "conference",
    "dimension", "frequency", "quantum", "compute",
    "strategy", "structure", "framework", "system",
    "investor", "revenue", "valuation", "term sheet",
    "waterloo", "WICI", "ICGAC", "zenodo", "preprint",
    "delta", "rootwell", "citizen gardens", "recover margins",
]


@dataclass
class PersonPoint:
    collection: str
    label: str
    text_preview: str
    similarity: float
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    category: str = ""  # utility, personal, technical, unknown
    vector: list = field(default_factory=list, repr=False)


@dataclass
class PersonSpace:
    name: str
    scan_date: str
    mode: str
    points: list[PersonPoint] = field(default_factory=list)
    total_raw: int = 0
    total_filtered: int = 0
    total_dimensions: int = 0
    variance_explained: list[float] = field(default_factory=list)
    collection_counts: dict[str, int] = field(default_factory=dict)


def _qdrant_post(path: str, body: dict) -> dict:
    req = urllib.request.Request(
        f"{QDRANT_URL}{path}",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
    )
    return json.loads(urllib.request.urlopen(req, timeout=30).read())


def _scroll_all(collection: str, filt: dict, with_vector: bool = False) -> list[dict]:
    """Paginate through all matching points."""
    all_points = []
    offset = None
    while True:
        body = {"limit": 100, "with_payload": True, "with_vector": with_vector, "filter": filt}
        if offset is not None:
            body["offset"] = offset
        resp = _qdrant_post(f"/collections/{collection}/points/scroll", body)
        result = resp.get("result", {})
        points = result.get("points", [])
        next_offset = result.get("next_page_offset")
        all_points.extend(points)
        if not next_offset or len(points) == 0:
            break
        offset = next_offset
    return all_points


def _semantic_search(collection: str, vector: list, limit: int = 500,
                     threshold: float = 0.45) -> list[dict]:
    """Vector similarity search with score threshold."""
    resp = _qdrant_post(f"/collections/{collection}/points/search", {
        "vector": vector,
        "limit": limit,
        "with_payload": True,
        "with_vector": True,
        "score_threshold": threshold,
    })
    return resp.get("result", [])


def _get_anchor_vectors(name: str) -> list[list[float]]:
    """Get anchor vectors for a person from contacts collection."""
    parts = name.strip().split()
    first = parts[0]
    last = parts[-1] if len(parts) > 1 else ""

    filt = {"must": [{"key": "first", "match": {"text": first}}]}
    if last:
        filt["must"].append({"key": "last", "match": {"text": last}})

    points = _scroll_all("contacts", filt, with_vector=True)
    vectors = [p["vector"] for p in points if p.get("vector")]
    return vectors


def _classify_content(text: str, collection: str, chat_name: str = "") -> str:
    """Classify a data point as utility or personal."""
    text_lower = text.lower()

    # Structured collections are always utility
    if collection in ("directives", "patents"):
        return "utility"

    # Concepts (screenshots) — check content
    if collection == "concepts":
        return "utility"

    # Claude chats — planning/work
    if collection == "claude_chats_ai":
        return "utility"

    # Group chats are typically utility/technical
    if collection == "whatsapp_chats":
        if any(g in chat_name for g in ["Coherence", "Field Group", "Signal", "General Chat",
                                         "University", "Connection"]):
            return "utility"

    # Check for personal signals
    personal_score = sum(1 for s in PERSONAL_SIGNALS if s in text_lower)
    utility_score = sum(1 for s in UTILITY_SIGNALS if s in text_lower)

    if utility_score > personal_score:
        return "utility"
    if personal_score > utility_score and personal_score >= 2:
        return "personal"

    # Default: if it's a direct chat with low utility signals, mark as personal
    if collection == "whatsapp_chats" and utility_score == 0:
        return "personal"

    return "utility"


def _extract_label(payload: dict, collection: str) -> tuple[str, str]:
    """Extract a display label and text preview from a point's payload."""
    if collection == "contacts":
        label = f"{payload.get('first', '')} {payload.get('last', '')} ({payload.get('organization', '')})"
        preview = payload.get("note", "")
    elif collection == "whatsapp_chats":
        label = payload.get("chat_name", "")[:50]
        dr = payload.get("date_range", "")
        if dr:
            label += f" [{dr[:10]}]"
        preview = payload.get("text", "")[:200]
    elif collection == "directives":
        text = payload.get("text", "")
        label = text[:80]
        preview = text[:200]
    elif collection == "concepts":
        src = payload.get("source", "") if isinstance(payload.get("source"), str) else ""
        label = src[:50] if src else "concept"
        preview = payload.get("text", "")[:200]
    elif collection == "claude_chats_ai":
        label = f"Claude [{payload.get('date_range', '')}]"
        preview = payload.get("text", "")[:200]
    elif collection == "patents":
        label = "Patent"
        preview = payload.get("text", "")[:200]
    elif collection == "legal_docs":
        label = payload.get("subject", payload.get("file_path", ""))[:60]
        preview = payload.get("text", "")[:200]
    else:
        label = str(payload)[:60]
        preview = ""

    return label.replace('"', "'").replace("\n", " "), preview.replace('"', "'").replace("\n", " ")


def build_person_space(name: str, mode: str = "utility",
                       similarity_threshold: float = 0.45,
                       collections: list[str] | None = None) -> PersonSpace:
    """Build a complete information space for a person.

    Args:
        name: Person's name (matched against contacts)
        mode: "full" or "utility" (filters personal content)
        similarity_threshold: Minimum cosine similarity to include
        collections: Which collections to search (None = all)
    """
    space = PersonSpace(name=name, scan_date=date.today().isoformat(), mode=mode)

    # Get anchor vectors
    anchors = _get_anchor_vectors(name)
    if not anchors:
        raise ValueError(f"No contact found for '{name}' in Qdrant contacts collection")

    # Use first anchor (primary contact vector)
    anchor = anchors[0]

    # Discover available collections
    if collections is None:
        resp = json.loads(urllib.request.urlopen(f"{QDRANT_URL}/collections").read())
        collections = [c["name"] for c in resp["result"]["collections"]]

    # Semantic search across all collections
    seen_ids = set()
    raw_points = []

    for coll in collections:
        results = _semantic_search(coll, anchor, limit=500, threshold=similarity_threshold)
        for r in results:
            point_id = (coll, r["id"])
            if point_id in seen_ids:
                continue
            seen_ids.add(point_id)

            payload = r.get("payload", {})
            vector = r.get("vector", [])
            score = r["score"]
            label, preview = _extract_label(payload, coll)
            chat_name = payload.get("chat_name", "")
            text = payload.get("text", preview)

            category = _classify_content(text, coll, chat_name)

            raw_points.append(PersonPoint(
                collection=coll,
                label=label,
                text_preview=preview[:150],
                similarity=score,
                category=category,
                vector=vector,
            ))

    space.total_raw = len(raw_points)

    # Filter based on mode
    if mode == "utility":
        points = [p for p in raw_points if p.category == "utility"]
    else:
        points = raw_points

    space.total_filtered = len(points)
    space.total_dimensions = len(points) * 768

    # Count by collection
    for p in points:
        space.collection_counts[p.collection] = space.collection_counts.get(p.collection, 0) + 1

    # PCA to 3D
    if len(points) >= 3:
        import numpy as np
        vectors = np.array([p.vector for p in points])
        centered = vectors - vectors.mean(axis=0)
        U, S, Vt = np.linalg.svd(centered, full_matrices=False)
        coords = U[:, :3] * S[:3]
        total_var = (S ** 2).sum()
        space.variance_explained = [round(float(S[i] ** 2 / total_var * 100), 1) for i in range(min(3, len(S)))]

        for i, p in enumerate(points):
            p.x = float(coords[i, 0])
            p.y = float(coords[i, 1])
            p.z = float(coords[i, 2])
            p.vector = []  # free memory

    space.points = points
    return space


def generate_person_report(space: PersonSpace, output: Path):
    """Generate interactive 3D HTML report for a person's information space."""

    COLLECTION_COLORS = {
        "contacts": "#7aa2f7",
        "whatsapp_chats": "#9ece6a",
        "directives": "#e0af68",
        "concepts": "#bb9af7",
        "claude_chats_ai": "#f7768e",
        "patents": "#73daca",
        "legal_docs": "#ff9e64",
    }
    COLLECTION_LABELS = {
        "contacts": "Contacts",
        "whatsapp_chats": "WhatsApp / Signal",
        "directives": "Directives",
        "concepts": "Concepts",
        "claude_chats_ai": "Claude Chats",
        "patents": "Patents",
        "legal_docs": "Legal Docs / Email",
    }

    # Build JSON data for the plot
    plot_points = []
    for p in space.points:
        plot_points.append({
            "x": p.x, "y": p.y, "z": p.z,
            "collection": p.collection,
            "label": p.label[:80],
            "preview": p.text_preview[:120],
            "similarity": round(p.similarity, 3),
            "category": p.category,
        })

    # Centroids
    centroids = defaultdict(lambda: {"x": 0, "y": 0, "z": 0, "n": 0})
    for p in plot_points:
        c = centroids[p["collection"]]
        c["x"] += p["x"]; c["y"] += p["y"]; c["z"] += p["z"]; c["n"] += 1
    centroid_list = [
        {"collection": k, "x": v["x"]/v["n"], "y": v["y"]/v["n"], "z": v["z"]/v["n"], "count": v["n"]}
        for k, v in centroids.items()
    ]

    data_json = json.dumps({
        "points": plot_points,
        "centroids": centroid_list,
    })

    var_str = " + ".join(f"PC{i+1}={v}%" for i, v in enumerate(space.variance_explained))
    total_var = sum(space.variance_explained)

    # Collection legend entries
    legend_items = ""
    for coll, count in sorted(space.collection_counts.items(), key=lambda x: x[1], reverse=True):
        color = COLLECTION_COLORS.get(coll, "#888")
        label = COLLECTION_LABELS.get(coll, coll)
        legend_items += f'<div class="legend-item" data-coll="{coll}"><div class="legend-dot" style="background:{color}"></div>{label} ({count})</div>\n'

    colors_json = json.dumps({k: v for k, v in COLLECTION_COLORS.items()})
    labels_json = json.dumps({k: v for k, v in COLLECTION_LABELS.items()})

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{space.name} — Information Space ({space.mode})</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<style>
:root {{
  --bg: #07070f; --surface: rgba(255,255,255,0.035); --border: rgba(255,255,255,0.07);
  --text: #e8e8f4; --muted: rgba(232,232,244,0.45); --dim: rgba(232,232,244,0.25);
  --accent: #7aa2f7; --mono: 'SF Mono','Fira Code',Consolas,monospace;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:var(--bg); color:var(--text); font-family:-apple-system,sans-serif; overflow:hidden; }}
#canvas {{ width:100vw; height:100vh; display:block; cursor:grab; }}
#canvas:active {{ cursor:grabbing; }}
.overlay {{ position:fixed; top:0; left:0; padding:1.5rem; pointer-events:none; z-index:10; }}
h1 {{ font-size:1.3rem; font-weight:600; margin-bottom:0.3rem; }}
.sub {{ font-size:0.8rem; color:var(--muted); margin-bottom:0.8rem; }}
.stats {{ font-family:var(--mono); font-size:0.7rem; color:var(--dim); line-height:1.6; }}
.stats span {{ color:var(--accent); }}
.mode-badge {{ display:inline-block; padding:2px 8px; border-radius:4px; font-size:0.65rem;
  font-weight:600; text-transform:uppercase; letter-spacing:0.06em; margin-left:8px; }}
.mode-utility {{ background:#9ece6a; color:#07070f; }}
.mode-full {{ background:#e0af68; color:#07070f; }}
.legend {{ position:fixed; top:1.5rem; right:1.5rem; background:var(--surface);
  border:1px solid var(--border); border-radius:10px; padding:1rem 1.2rem; z-index:10; }}
.legend h3 {{ font-size:0.7rem; color:var(--muted); text-transform:uppercase;
  letter-spacing:0.08em; margin-bottom:0.5rem; }}
.legend-item {{ display:flex; align-items:center; gap:8px; font-size:0.75rem;
  margin-bottom:0.3rem; cursor:pointer; transition:opacity 0.2s; }}
.legend-item:hover {{ opacity:0.7; }}
.legend-dot {{ width:10px; height:10px; border-radius:50%; }}
.tooltip {{ position:fixed; background:rgba(15,23,42,0.95); border:1px solid var(--border);
  border-radius:8px; padding:0.6rem 0.8rem; font-size:0.75rem; pointer-events:none;
  z-index:100; display:none; max-width:400px; backdrop-filter:blur(8px); }}
.tooltip .tt-coll {{ font-size:0.6rem; text-transform:uppercase; letter-spacing:0.06em; }}
.tooltip .tt-label {{ margin-top:2px; font-family:var(--mono); font-size:0.7rem; line-height:1.4; }}
.tooltip .tt-sim {{ font-size:0.6rem; color:var(--dim); margin-top:4px; }}
.controls {{ position:fixed; bottom:1.5rem; left:50%; transform:translateX(-50%);
  background:var(--surface); border:1px solid var(--border); border-radius:10px;
  padding:0.6rem 1.2rem; font-size:0.7rem; color:var(--muted); z-index:10; }}
</style>
</head>
<body>
<canvas id="canvas"></canvas>
<div class="overlay">
  <h1>{space.name} <span class="mode-badge mode-{space.mode}">{space.mode}</span></h1>
  <div class="sub">{space.total_filtered} data points across {len(space.collection_counts)} collections
    ({space.total_raw} raw, {space.total_raw - space.total_filtered} filtered)</div>
  <div class="stats">
    Continuous dimensions: <span>{space.total_dimensions:,}</span><br>
    {var_str} = <span>{total_var:.1f}%</span> captured<br>
    Similarity threshold: <span>0.45</span>
  </div>
</div>
<div class="legend"><h3>Collections</h3>
{legend_items}
</div>
<div class="tooltip" id="tooltip">
  <div class="tt-coll"></div>
  <div class="tt-label"></div>
  <div class="tt-sim"></div>
</div>
<div class="controls">Drag to rotate &middot; Scroll to zoom &middot; Hover for detail &middot; Click legend to toggle</div>
<script>
const DATA = {data_json};
const COLORS = {colors_json};
const LABELS = {labels_json};

function hexToInt(h) {{ return parseInt(h.replace('#',''), 16); }}

const canvas = document.getElementById('canvas');
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(55, innerWidth/innerHeight, 0.01, 100);
camera.position.set(0.8, 0.6, 0.8);
const renderer = new THREE.WebGLRenderer({{ canvas, antialias:true }});
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setClearColor(0x07070f);

scene.add(new THREE.AmbientLight(0xffffff, 0.4));
const dl = new THREE.DirectionalLight(0xffffff, 0.6);
dl.position.set(1,2,1); scene.add(dl);

const grid = new THREE.GridHelper(2, 20, 0x1a1a2e, 0x1a1a2e);
grid.position.y = -0.8; scene.add(grid);

// Axes
[[[-1,0,0],[1,0,0],0xf7768e],[[0,-1,0],[0,1,0],0x9ece6a],[[0,0,-1],[0,0,1],0x7aa2f7]]
.forEach(([f,t,c]) => {{
  const g = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(...f), new THREE.Vector3(...t)]);
  scene.add(new THREE.Line(g, new THREE.LineBasicMaterial({{color:c, opacity:0.25, transparent:true}})));
}});

const S = 1.8; // scale for spread
const meshes = [];
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

DATA.points.forEach((p, i) => {{
  const r = 0.008 + p.similarity * 0.008; // size by similarity
  const geo = new THREE.SphereGeometry(r, 10, 10);
  const color = hexToInt(COLORS[p.collection] || '#888888');
  const mat = new THREE.MeshPhongMaterial({{
    color, emissive: color, emissiveIntensity: 0.3,
    transparent: true, opacity: 0.82,
  }});
  const mesh = new THREE.Mesh(geo, mat);
  mesh.position.set(p.x*S, p.y*S, p.z*S);
  mesh.userData = {{ i, ...p }};
  scene.add(mesh); meshes.push(mesh);
}});

// Nearest-neighbor lines within collection
const groups = {{}};
DATA.points.forEach((p,i) => {{ (groups[p.collection] = groups[p.collection]||[]).push(i); }});
Object.entries(groups).forEach(([coll, ids]) => {{
  if (ids.length < 2) return;
  const color = hexToInt(COLORS[coll] || '#888');
  const pos = [];
  ids.forEach(i => {{
    const pi = DATA.points[i]; let md = Infinity, ni = -1;
    ids.forEach(j => {{ if(i===j) return;
      const pj = DATA.points[j];
      const d = (pi.x-pj.x)**2+(pi.y-pj.y)**2+(pi.z-pj.z)**2;
      if(d<md) {{ md=d; ni=j; }}
    }});
    if(ni>=0) {{
      const pn = DATA.points[ni];
      pos.push(pi.x*S,pi.y*S,pi.z*S, pn.x*S,pn.y*S,pn.z*S);
    }}
  }});
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  scene.add(new THREE.LineSegments(g, new THREE.LineBasicMaterial({{color, opacity:0.1, transparent:true}})));
}});

// Centroids
DATA.centroids.forEach(c => {{
  const color = hexToInt(COLORS[c.collection]||'#888');
  const mesh = new THREE.Mesh(
    new THREE.SphereGeometry(0.03, 16, 16),
    new THREE.MeshPhongMaterial({{color, emissive:color, emissiveIntensity:0.4, transparent:true, opacity:0.3, wireframe:true}})
  );
  mesh.position.set(c.x*S, c.y*S, c.z*S);
  scene.add(mesh);
}});

// Legend toggle
const visible = new Set(Object.keys(COLORS));
document.querySelectorAll('.legend-item').forEach(el => {{
  el.addEventListener('click', () => {{
    const c = el.dataset.coll;
    if(visible.has(c)) {{ visible.delete(c); el.style.opacity='0.3'; }}
    else {{ visible.add(c); el.style.opacity='1'; }}
    meshes.forEach(m => {{ m.visible = visible.has(m.userData.collection); }});
  }});
}});

// Orbit
let drag=false, px=0, py=0, theta=Math.PI/4, phi=Math.PI/4, radius=1.3;
function updateCam() {{
  camera.position.set(radius*Math.sin(phi)*Math.cos(theta), radius*Math.cos(phi), radius*Math.sin(phi)*Math.sin(theta));
  camera.lookAt(0,0,0);
}}
canvas.addEventListener('mousedown', e => {{ drag=true; px=e.clientX; py=e.clientY; }});
canvas.addEventListener('mouseup', () => {{ drag=false; }});
canvas.addEventListener('mousemove', e => {{
  mouse.x = (e.clientX/innerWidth)*2-1;
  mouse.y = -(e.clientY/innerHeight)*2+1;
  if(drag) {{
    theta -= (e.clientX-px)*0.005;
    phi = Math.max(0.1, Math.min(Math.PI-0.1, phi-(e.clientY-py)*0.005));
    px=e.clientX; py=e.clientY; updateCam();
  }}
  raycaster.setFromCamera(mouse, camera);
  const hits = raycaster.intersectObjects(meshes);
  const tt = document.getElementById('tooltip');
  if(hits.length) {{
    const d = hits[0].object.userData;
    const color = COLORS[d.collection]||'#888';
    tt.querySelector('.tt-coll').textContent = LABELS[d.collection]||d.collection;
    tt.querySelector('.tt-coll').style.color = color;
    tt.querySelector('.tt-label').textContent = d.label;
    tt.querySelector('.tt-sim').textContent = 'similarity: '+d.similarity + (d.preview ? ' — '+d.preview.slice(0,80)+'...' : '');
    tt.style.display='block';
    tt.style.left=(e.clientX+15)+'px'; tt.style.top=(e.clientY-10)+'px';
  }} else {{ tt.style.display='none'; }}
}});
canvas.addEventListener('wheel', e => {{
  radius = Math.max(0.3, Math.min(4, radius+e.deltaY*0.001));
  updateCam(); e.preventDefault();
}}, {{passive:false}});
window.addEventListener('resize', () => {{
  camera.aspect=innerWidth/innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
}});

let autoR = true;
canvas.addEventListener('mousedown', () => {{ autoR=false; }});
function animate() {{
  requestAnimationFrame(animate);
  if(autoR) {{ theta+=0.002; updateCam(); }}
  const t = Date.now()*0.001;
  meshes.forEach((m,i) => {{ m.material.emissiveIntensity = 0.2+0.12*Math.sin(t+i*0.2); }});
  renderer.render(scene, camera);
}}
updateCam(); animate();
</script>
</body>
</html>"""

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html)
