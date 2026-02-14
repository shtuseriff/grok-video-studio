from pathlib import Path

def fix_playlists():
    output_dir = Path("sessions")
    if not output_dir.exists():
        return

    # Iterate over all session directories
    for session_dir in output_dir.iterdir():
        if not session_dir.is_dir():
            continue
            
        session_id = session_dir.name
        
        # Find all m3u8 files in this session directory
        playlists = list(session_dir.glob("*.m3u8"))
        
        for playlist_path in playlists:
            print(f"Checking playlist: {playlist_path}")
            original_content = playlist_path.read_text()
            lines = original_content.splitlines()
            new_lines = []
            modified = False
            
            for line in lines:
                if line.strip() and not line.startswith("#"):
                    # This is a file entry
                    # Check if it starts with "session_id/"
                    prefix = f"{session_id}/"
                    if line.startswith(prefix):
                        new_line = line[len(prefix):]
                        new_lines.append(new_line)
                        modified = True
                        print(f"  Fixed entry: {line} -> {new_line}")
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)
            
            if modified:
                print(f"  Saving changes to {playlist_path.name}")
                playlist_path.write_text("\n".join(new_lines) + "\n")
            else:
                print("  No changes needed.")

if __name__ == "__main__":
    fix_playlists()
