from pathlib import Path
import json
from api.session import SessionState

# Mock data based on the user's provided file content
data = {
  "session_id": "e656fe",
  "mode": "multi",
  "status": "running",
  "current_part": 1,
  "total_parts": 1,
  "pending_action": None,
  "allowed_actions": [],
  "logs": [],
  "outputs": [],
  "prompts": ["test"],
  "refined_prompts": [],
  "accepted_prompts": ["test"],
  "created_at": "2026-02-06T07:58:43.405777Z",
  "updated_at": "2026-02-06T07:59:07.285785Z",
  "last_error": None,
  "playlists": {},
  "settings": {
    "duration": 2,
    "resolution": "720p",
    "preflight": True,
    "api_host": "api.x.ai",
    "refine_prompts": True,
    "refine_auto_accept": False
  },
  "costs": {
    "currency": "USD",
    "total": 0.15,
    "items": [],
    "violation_fee": 0.05
  }
}

try:
    session = SessionState.from_dict(data, Path("/tmp"), Path("/tmp/e656fe"))
    print("Successfully loaded session")
    print(f"Parent Session ID: {session.parent_session_id}")
    print(f"Budget Cap: {session.budget_cap}")
except Exception as e:
    print(f"Failed to load session: {e}")
