import shutil
from pathlib import Path

def migrate_sessions():
    output_dir = Path("sessions")
    if not output_dir.exists():
        print("No sessions directory found.")
        return

    # 1. Identify all session IDs from *_session.json files in the root.
    session_files = list(output_dir.glob("*_session.json"))
    sessions = {}
    
    for session_file in session_files:
        # Extract session_id (e.g. "10aea3" from "10aea3_session.json")
        session_id = session_file.stem.split("_session")[0]
        sessions[session_id] = session_file

    print(f"Found {len(sessions)} sessions to migrate.")

    for session_id, session_file in sessions.items():
        # Create dedicated directory
        session_dir = output_dir / session_id
        if not session_dir.exists():
            print(f"Creating directory for {session_id}...")
            session_dir.mkdir()
        else:
            print(f"Directory {session_id} already exists.")

        # 2. Find all files related to this session in the root directory.
        #    This includes:
        #    - {session_id}_session.json
        #    - {session_id}_input.*
        #    - {session_id}_*.mp4
        #    - {session_id}_*.png
        #    - {session_id}.m3u8 (if any, though usually generated later)
        #    - {session_id}_preflight.m3u8
        
        # We can glob for anything starting with session_id
        related_files = list(output_dir.glob(f"{session_id}*"))
        
        for file_path in related_files:
            # Skip if it's a directory (like the session dir we just created)
            if file_path.is_dir():
                continue
                
            # Move file into the session directory
            target_path = session_dir / file_path.name
            if not target_path.exists():
                print(f"  Moving {file_path.name} -> {session_id}/")
                shutil.move(str(file_path), str(target_path))
            else:
                print(f"  Skipping {file_path.name}, already exists in target.")
                # Optionally delete the source if it's a duplicate? 
                # Better safe than sorry: leave it or delete if identical.
                # For this migration, let's just leave duplicates in root to be manually cleaned or assume safety if successful.
                # Actually, to "clean up", we should probably remove the root one if the move failed due to existence.
                # But let's stick to simple move. 
                pass

    print("Migration complete.")

if __name__ == "__main__":
    migrate_sessions()
