from __future__ import annotations

import json
from pathlib import Path
from typing import Any

def generate_storyboard_html(session_data: dict[str, Any]) -> str:
    """Generate a self-contained HTML storyboard for a session."""
    
    session_id = session_data["session_id"]
    title = session_data.get("title") or session_id
    outputs = session_data.get("outputs", [])
    prompts = session_data.get("prompts", [])
    costs = session_data.get("costs", {})
    created_at = session_data.get("created_at", "")
    
    # Calculate total duration
    total_duration = 0
    video_count = 0
    for out in outputs:
        if out.get("type") == "video" and out.get("status") != "aborted":
            total_duration += out.get("cost", {}).get("duration", 0)
            video_count += 1

    # Filter relevant outputs
    cards = []
    for out in outputs:
        if out.get("type") in ("video", "preflight"):
            cards.append(out)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Grok Video Storyboard</title>
    <style>
        :root {{
            --bg: #09090b;
            --panel: #121417;
            --text: #ededed;
            --text-muted: #9ca3af;
            --border: #2a2e35;
            --accent: #10b981;
        }}
        body {{
            background: var(--bg);
            color: var(--text);
            font-family: system-ui, -apple-system, sans-serif;
            margin: 0;
            padding: 40px;
            line-height: 1.5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        header {{
            border-bottom: 1px solid var(--border);
            padding-bottom: 24px;
            margin-bottom: 40px;
        }}
        h1 {{ margin: 0 0 8px 0; font-size: 2.5rem; }}
        .meta {{ color: var(--text-muted); font-family: monospace; }}
        
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 24px;
        }}
        
        .card {{
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 12px;
            overflow: hidden;
            padding: 16px;
        }}
        
        video {{
            width: 100%;
            border-radius: 8px;
            background: #000;
            margin-bottom: 12px;
        }}
        
        .badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 99px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            background: var(--border);
            color: var(--text-muted);
            margin-bottom: 8px;
        }}
        .badge.video {{ background: var(--text); color: var(--bg); }}
        .badge.preflight {{ background: #3b82f6; color: white; }}
        .badge.aborted {{ background: #ef4444; color: white; }}
        
        .prompt {{
            font-family: monospace;
            font-size: 0.85rem;
            color: var(--text-muted);
            white-space: pre-wrap;
            max-height: 150px;
            overflow-y: auto;
            background: rgba(0,0,0,0.3);
            padding: 8px;
            border-radius: 6px;
        }}
        
        .cost {{
            margin-top: 12px;
            font-size: 0.8rem;
            color: var(--text-muted);
            text-align: right;
        }}
        
        .summary-stats {{
            display: flex;
            gap: 24px;
            margin-top: 16px;
        }}
        .stat {{ display: flex; flex-direction: column; }}
        .stat span {{ font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; }}
        .stat strong {{ font-size: 1.25rem; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="meta">SESSION ID: {session_id}</div>
            <h1>{title}</h1>
            <div class="summary-stats">
                <div class="stat">
                    <span>Created</span>
                    <strong>{created_at[:10] if created_at else 'Unknown'}</strong>
                </div>
                <div class="stat">
                    <span>Total Cost</span>
                    <strong>${costs.get('total', 0):.2f}</strong>
                </div>
                <div class="stat">
                    <span>Clips</span>
                    <strong>{video_count}</strong>
                </div>
                <div class="stat">
                    <span>Duration</span>
                    <strong>{total_duration}s</strong>
                </div>
            </div>
        </header>
        
        <div class="grid">
"""
    
    for card in cards:
        video_src = card.get("path")
        prompt_text = card.get("prompt", "")
        kind = card.get("type", "video")
        status = card.get("status", "success")
        part = card.get("part")
        cost = card.get("cost", {}).get("total_cost", 0.0)
        
        badge_class = "aborted" if status == "aborted" else kind
        label = "REJECTED" if status == "aborted" else kind.upper()
        if part:
            label += f" • PART {part}"
            
        html += f"""
            <div class="card">
                <span class="badge {badge_class}">{label}</span>
                <video controls src="{video_src}" preload="metadata"></video>
                <div class="prompt">{prompt_text}</div>
                <div class="cost">${cost:.2f}</div>
            </div>
"""

    html += """
        </div>
    </div>
</body>
</html>
"""
    return html
