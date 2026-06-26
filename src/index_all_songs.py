import os
import sys

# Ensure src is in import path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import fingerprint as fp
import database as db

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, "fingerprints.db")
    songs_dir = r"C:\Users\Asus\OneDrive\Desktop\Project Sound detection\songs"
    
    print(f"Initializing database at: {db_path}")
    db.init_db(db_path)
    
    if not os.path.exists(songs_dir):
        print(f"Error: Songs directory not found at {songs_dir}")
        return
        
    mp3_files = [f for f in os.listdir(songs_dir) if f.endswith('.mp3')]
    print(f"Found {len(mp3_files)} MP3 files. Indexing...")
    
    for idx, filename in enumerate(mp3_files):
        file_path = os.path.join(songs_dir, filename)
        song_title = os.path.splitext(filename)[0]
        print(f"[{idx+1}/{len(mp3_files)}] Indexing: {song_title}")
        try:
            y, sr = fp.load_audio(file_path, sr=11025)
            spec, freqs, times = fp.compute_spectrogram(y, sr)
            peaks = fp.find_peaks(spec)
            fingerprints = fp.generate_fingerprints(peaks)
            db.store_song_fingerprints(db_path, song_title, fingerprints)
        except Exception as e:
            print(f"Error indexing {filename}: {e}")
            
    print("Indexing complete! fingerprints.db successfully created.")

if __name__ == '__main__':
    main()
