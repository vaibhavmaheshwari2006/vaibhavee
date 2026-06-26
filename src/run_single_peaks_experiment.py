import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict, Counter

# Ensure src is in import path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import fingerprint as fp

def run_experiment():
    plots_dir = "temp_plots"
    os.makedirs(plots_dir, exist_ok=True)
    
    # Load database song
    db_song_path = r"C:\Users\Asus\OneDrive\Desktop\Project Sound detection\songs\Back In The U.S.S.R..mp3"
    query_clip_path = r"temp\back-in-the-ussr_Tht6iWYj.mp3"
    
    if not os.path.exists(db_song_path):
        print(f"Error: Database song not found at {db_song_path}")
        return
    if not os.path.exists(query_clip_path):
        print(f"Error: Query clip not found at {query_clip_path}")
        return
        
    print("Loading audio files...")
    y_db, sr_db = fp.load_audio(db_song_path, sr=11025)
    y_query, sr_query = fp.load_audio(query_clip_path, sr=11025)
    
    print("Computing spectrograms...")
    spec_db, freqs_db, times_db = fp.compute_spectrogram(y_db, sr=11025)
    spec_query, freqs_query, times_query = fp.compute_spectrogram(y_query, sr=11025)
    
    print("Finding peaks...")
    peaks_db = fp.find_peaks(spec_db)
    peaks_query = fp.find_peaks(spec_query)
    
    # ---------------------------------------------
    # 1. Paired Hashes Matching
    # ---------------------------------------------
    print("Running Paired Hashes Matching...")
    fp_db = fp.generate_fingerprints(peaks_db)
    fp_query = fp.generate_fingerprints(peaks_query)
    
    db_by_hash = defaultdict(list)
    for hash_val, t_db in fp_db:
        db_by_hash[hash_val].append(t_db)
        
    paired_diffs = []
    for hash_val, t_query in fp_query:
        if hash_val in db_by_hash:
            for t_db in db_by_hash[hash_val]:
                paired_diffs.append(t_db - t_query)
                
    # Find best offset
    counts = Counter(paired_diffs)
    best_offset = counts.most_common(1)[0][0]
    
    print(f"Best offset for paired hashes: {best_offset}")
    
    # Plot Paired Hashes Histogram
    plt.figure(figsize=(6, 4))
    min_bin = best_offset - 100
    max_bin = best_offset + 100
    filtered_diffs = [d for d in paired_diffs if min_bin <= d <= max_bin]
    
    if filtered_diffs:
        plt.hist(filtered_diffs, bins=200, color='#1DB954', edgecolor='none', alpha=0.8)
        plt.axvline(best_offset, color='#ff4b4b', linestyle='--', linewidth=1.5, 
                    label=f"True Alignment Peak (Offset = {best_offset})")
        plt.legend()
    else:
        plt.hist(paired_diffs, bins=50, color='#1DB954', edgecolor='none', alpha=0.8)
        
    plt.xlabel("Time Offset Difference (frames)")
    plt.ylabel("Match Count")
    plt.title("Paired Hashes Offset Alignment Histogram")
    plt.grid(True, linestyle=':', alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'histogram.png'), dpi=100)
    plt.close()
    print("Paired hashes histogram saved.")
    
    # ---------------------------------------------
    # 2. Single Peaks Matching
    # ---------------------------------------------
    print("Running Single Peaks Matching...")
    db_by_freq = defaultdict(list)
    for t_db, f_db, _ in peaks_db:
        db_by_freq[f_db].append(t_db)
        
    single_diffs = []
    for t_query, f_query, _ in peaks_query:
        if f_query in db_by_freq:
            for t_db in db_by_freq[f_query]:
                # In actual single peak matching, since the start time offset is unknown,
                # any frequency match is a candidate match.
                single_diffs.append(t_db - t_query)
                
    # Plot Single Peaks Histogram
    plt.figure(figsize=(6, 4))
    # Filter to same range as paired histogram for direct comparison
    filtered_single = [d for d in single_diffs if min_bin <= d <= max_bin]
    
    if filtered_single:
        plt.hist(filtered_single, bins=200, color='#888888', edgecolor='none', alpha=0.8)
    else:
        plt.hist(single_diffs, bins=50, color='#888888', edgecolor='none', alpha=0.8)
        
    plt.xlabel("Time Offset Difference (frames)")
    plt.ylabel("Match Count")
    plt.title("Single Peaks Offset Alignment Histogram")
    plt.grid(True, linestyle=':', alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'histogram_single.png'), dpi=100)
    plt.close()
    print("Single peaks histogram saved.")

if __name__ == '__main__':
    run_experiment()
