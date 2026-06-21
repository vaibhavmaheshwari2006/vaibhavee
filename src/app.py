import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd
from collections import Counter
import textwrap

# Import core modules
import fingerprint as fp
import database as db

# Page configurations
st.set_page_config(
    page_title="Audio Song Recognition",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configure Matplotlib Styles for Dark Mode integration
def configure_matplotlib_theme():
    plt.rcParams.update({
        'figure.facecolor': '#121212',
        'axes.facecolor': '#1e1e1e',
        'text.color': '#ffffff',
        'axes.labelcolor': '#aaaaaa',
        'xtick.color': '#888888',
        'ytick.color': '#888888',
        'grid.color': '#333333',
        'grid.alpha': 0.3,
        'axes.edgecolor': '#333333',
        'font.family': 'sans-serif',
    })
configure_matplotlib_theme()

# Custom Styling (CSS)
st.html("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&display=swap');

    /* Global Font Override */
    .stApp, [data-testid="stSidebar"], .stMarkdown, button, input, select, textarea {
        font-family: 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    }

    /* Base App Dark Theme */
    .stApp {
        background: radial-gradient(circle at 50% 50%, #181818 0%, #0c0c0c 100%) !important;
        color: #ffffff !important;
    }

    /* Sidebar Dark Theme */
    section[data-testid="stSidebar"] {
        background-color: #050505 !important;
        border-right: 1px solid rgba(29, 185, 84, 0.1) !important;
    }

    /* Sidebar Title and Text */
    section[data-testid="stSidebar"] h1 {
        color: #ffffff !important;
        font-family: 'Outfit', sans-serif !important;
    }

    /* Custom Text Header Gradients */
    .main-title {
        background: linear-gradient(135deg, #ffffff 30%, #1DB954 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3rem;
        font-family: 'Outfit', sans-serif;
        letter-spacing: -0.5px;
        margin-bottom: 5px;
    }
    .sidebar-title {
        background: linear-gradient(135deg, #1DB954 0%, #00bcd4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 1.8rem;
        font-family: 'Outfit', sans-serif;
        letter-spacing: -0.5px;
        margin-bottom: 10px;
    }

    /* Success Card Banner styling */
    .success-card {
        background: linear-gradient(135deg, rgba(29, 185, 84, 0.15) 0%, rgba(10, 35, 18, 0.5) 100%);
        border: 1px solid rgba(29, 185, 84, 0.3);
        border-radius: 20px;
        padding: 30px;
        margin: 25px 0;
        box-shadow: 0 10px 40px 0 rgba(0, 0, 0, 0.5), 0 0 30px 0 rgba(29, 185, 84, 0.1) inset;
        backdrop-filter: blur(16px);
        position: relative;
        overflow: hidden;
    }
    .success-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.05), transparent);
        transform: translateX(-100%);
        animation: shimmer 3s infinite;
    }
    @keyframes shimmer {
        100% { transform: translateX(100%); }
    }
    .success-title {
        font-size: 1rem;
        color: #1ed760;
        text-transform: uppercase;
        font-weight: 800;
        letter-spacing: 2px;
    }
    .success-song {
        font-size: 3rem;
        font-weight: 800;
        color: #ffffff;
        margin: 15px 0;
        text-shadow: 0 0 20px rgba(29, 185, 84, 0.4);
        letter-spacing: -0.5px;
    }

    /* Buttons Styling */
    div.stButton > button {
        background: linear-gradient(135deg, #1DB954 0%, #179443 100%) !important;
        color: white !important;
        border: none !important;
        padding: 10px 24px !important;
        border-radius: 30px !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        box-shadow: 0 4px 15px rgba(29, 185, 84, 0.2) !important;
        width: 100%;
        text-shadow: none !important;
    }
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(29, 185, 84, 0.4) !important;
        background: linear-gradient(135deg, #1ed760 0%, #1db954 100%) !important;
        color: white !important;
    }
    div.stButton > button:active {
        transform: translateY(1px) !important;
    }

    /* Custom Table Styling */
    table {
        width: 100% !important;
        border-collapse: collapse !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        background-color: rgba(255, 255, 255, 0.02) !important;
        margin-top: 15px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    th {
        background-color: rgba(29, 185, 84, 0.08) !important;
        color: #1DB954 !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        padding: 14px 16px !important;
        border-bottom: 2px solid rgba(29, 185, 84, 0.2) !important;
        font-size: 0.85rem !important;
    }
    td {
        padding: 12px 16px !important;
        color: #e0e0e0 !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.04) !important;
        font-size: 0.95rem !important;
    }
    tr:hover {
        background-color: rgba(255, 255, 255, 0.03) !important;
    }

    /* Landing Page Layout styles */
    .landing-container {
        padding: 20px 0;
    }
    .landing-header {
        background: linear-gradient(135deg, rgba(29, 185, 84, 0.15) 0%, rgba(0, 188, 212, 0.05) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 40px;
        text-align: center;
        margin-bottom: 35px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        backdrop-filter: blur(10px);
    }
    .steps-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 20px;
        margin-bottom: 30px;
    }
    .step-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.01) 100%);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 25px;
        text-align: center;
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
    }
    .step-card:hover {
        transform: translateY(-5px);
        border-color: rgba(29, 185, 84, 0.3);
        background: linear-gradient(135deg, rgba(29, 185, 84, 0.06) 0%, rgba(255, 255, 255, 0.01) 100%);
        box-shadow: 0 12px 30px rgba(29, 185, 84, 0.05);
    }
    .step-icon {
        font-size: 2.5rem;
        margin-bottom: 15px;
    }
    .step-title {
        font-weight: 700;
        font-size: 1.2rem;
        color: #ffffff;
        margin-bottom: 10px;
    }
    .step-desc {
        font-size: 0.9rem;
        color: #aaaaaa;
        line-height: 1.45;
    }
</style>
""")

# Helper function to generate pairing coordinates for plots
def generate_pair_coordinates(peaks, fan_value=15, min_delta_t=1, max_delta_t=100):
    pairs = []
    num_peaks = len(peaks)
    for i in range(num_peaks):
        t1, f1, _ = peaks[i]
        targets_paired = 0
        for j in range(i + 1, num_peaks):
            t2, f2, _ = peaks[j]
            delta_t = t2 - t1
            if delta_t > max_delta_t:
                break
            if delta_t >= min_delta_t:
                pairs.append(((t1, f1), (t2, f2)))
                targets_paired += 1
                if targets_paired >= fan_value:
                    break
    return pairs

# DB Path and Default folder
DB_PATH = "fingerprints.db"
DEFAULT_DATA_DIR = r"C:\Users\Asus\OneDrive\Desktop\Project Sound detection\songs"

# Init DB on load
db.init_db(DB_PATH)

# Sidebar - Database Control
st.sidebar.html('<div class="sidebar-title">Database Control</div>')
st.sidebar.write("Configure and index your reference song catalog.")

# Directory Input
DATA_DIR = st.sidebar.text_input("📁 Audio Database Directory", value=DEFAULT_DATA_DIR)

# Action: Index files (Input button)
if st.sidebar.button("📂 Scan & Index Audio Folder"):
    if not os.path.exists(DATA_DIR) or len([f for f in os.listdir(DATA_DIR) if f.endswith('.mp3')]) == 0:
        st.sidebar.error(f"Please place `.mp3` files in the `{DATA_DIR}` directory.")
    else:
        mp3_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.mp3')]
        progress_bar = st.sidebar.progress(0)
        status_text = st.sidebar.empty()
        
        indexed_count = 0
        for i, file_name in enumerate(mp3_files):
            status_text.text(f"Indexing {file_name}...")
            file_path = os.path.join(DATA_DIR, file_name)
            
            try:
                y, sr = fp.load_audio(file_path)
                spec, freqs, times = fp.compute_spectrogram(y, sr)
                peaks = fp.find_peaks(spec)
                fingerprints = fp.generate_fingerprints(peaks)
                
                # Use clean file base name as song title
                song_title = os.path.splitext(file_name)[0]
                db.store_song_fingerprints(DB_PATH, song_title, fingerprints)
                indexed_count += 1
            except Exception as e:
                st.sidebar.error(f"Error indexing {file_name}: {e}")
            
            progress_bar.progress((i + 1) / len(mp3_files))
            
        status_text.text(f"Done! Indexed {indexed_count} songs.")
        st.balloons()

# Main Layout Header
st.html('<div class="main-title">🎵 Audio Recognition System</div>')

# Select mode
mode = st.radio("Select Application Mode", ["Single-Clip Mode", "Batch Mode"], horizontal=True)

if mode == "Single-Clip Mode":
    st.write("Upload a query audio clip, optionally apply deformations to test robust matching, and view full pipeline visualizations.")
    
    # Grid: Uploader on left, configs on right
    col_upload, col_config = st.columns([2, 1])
    
    with col_upload:
        uploaded_file = st.file_uploader("Upload Query Audio File (.wav or .mp3)", type=["wav", "mp3", "m4a"])
        
    with col_config:
        with st.expander("⚙️ Pipeline & Audio Degradation Settings"):
            st.markdown("##### STFT Parameters")
            n_fft = st.selectbox("Window Size (N_FFT)", [256, 512, 1024, 2048], index=1)
            hop_length = st.number_input("Hop Length", value=128, min_value=32, max_value=512, step=32)
            
            st.markdown("##### Peak Detection & Fingerprinting")
            neighborhood_size = st.slider("Neighborhood Size (2D Max Filter)", 5, 30, 15)
            min_amplitude = st.slider("Min Peak Amplitude (dB)", -80, -20, -50)
            fan_value = st.slider("Fingerprint Fan-Out Limit", 5, 25, 15)
            
            st.markdown("##### Robustness Testing (Deformations)")
            noise_level = st.slider("White Noise Level", 0.0, 0.05, 0.0, step=0.005, format="%.3f")
            pitch_shift = st.slider("Pitch Shift (Semitones)", -2.0, 2.0, 0.0, step=0.25)
            time_stretch = st.slider("Time Stretch Rate", 0.8, 1.2, 1.0, step=0.05)

    if uploaded_file is not None:
        # Save file temporarily to disk to load via librosa
        temp_dir = "temp"
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, uploaded_file.name)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        st.audio(temp_path, format="audio/mp3")
        
        # Identify Song Button (Output button)
        if st.button("🔍 Identify Song"):
            with st.spinner("Processing audio & matching against database..."):
                # Load Audio
                y, sr = fp.load_audio(temp_path)
                
                # Apply Audio Degradations
                if noise_level > 0.0:
                    y = fp.add_noise(y, noise_level)
                if pitch_shift != 0.0:
                    y = fp.pitch_shift(y, sr, pitch_shift)
                if time_stretch != 1.0:
                    y = fp.time_stretch(y, time_stretch)
                
                # Compute Spectrogram
                spec, freqs, times = fp.compute_spectrogram(y, sr, n_fft=n_fft, hop_length=hop_length)
                
                # Find Peaks
                peaks = fp.find_peaks(spec, min_amplitude=min_amplitude, neighborhood_size=neighborhood_size)
                
                # Generate Fingerprints
                fingerprints = fp.generate_fingerprints(peaks, fan_value=fan_value)
                
                # Match
                matches, song_names = db.match_fingerprints(DB_PATH, fingerprints)
                scores = db.score_matches(matches)
                
            # clean up temp file
            try:
                os.remove(temp_path)
            except:
                pass
                
            if not scores:
                st.html("""
                <div class="success-card" style="border-color: #ff9800; background: linear-gradient(135deg, rgba(255, 152, 0, 0.2) 0%, rgba(255, 152, 0, 0.05) 100%);">
                    <div class="success-title" style="color: #ff9800;">No Matches Found</div>
                    <div class="success-song" style="font-size: 1.8rem;">Could not identify song</div>
                    <p style="color: #aaaaaa; margin-top: 10px;">Ensure the database is indexed with songs.</p>
                </div>
                """)
            else:
                best_song_id, peak_score, total_matches, best_offset = scores[0]
                best_song_title = song_names.get(best_song_id, f"Unknown Song (ID: {best_song_id})")
                
                # Check confidence threshold
                if peak_score < 20:
                    st.html(f"""
                    <div class="success-card" style="border-color: #ff9800; background: linear-gradient(135deg, rgba(255, 152, 0, 0.2) 0%, rgba(255, 152, 0, 0.05) 100%);">
                        <div class="success-title" style="color: #ff9800;">Song Not in Dataset</div>
                        <div class="success-song" style="font-size: 2.2rem;">Confidence too low</div>
                        <p style="color: #aaaaaa; margin-top: 10px;">The closest candidate was <b>{best_song_title}</b> with a score of <b>{peak_score}</b> (threshold: 20). This indicates the query track is likely not in the database.</p>
                    </div>
                    """)
                else:
                    # Show a beautiful recognition card
                    st.html(f"""
                    <div class="success-card">
                        <div class="success-title">Recognized Song</div>
                        <div class="success-song">{best_song_title}</div>
                        <div style="display: flex; justify-content: center; gap: 30px; margin-top: 15px;">
                            <div>
                                <div style="font-size: 0.8rem; color: #888888; text-transform: uppercase;">Confidence Score (Peak Height)</div>
                                <div style="font-size: 1.5rem; font-weight: bold; color: #1DB954;">{peak_score}</div>
                            </div>
                            <div>
                                <div style="font-size: 0.8rem; color: #888888; text-transform: uppercase;">Total Matches</div>
                                <div style="font-size: 1.5rem; font-weight: bold; color: #ffffff;">{total_matches}</div>
                            </div>
                            <div>
                                <div style="font-size: 0.8rem; color: #888888; text-transform: uppercase;">Optimal Offset Difference</div>
                                <div style="font-size: 1.5rem; font-weight: bold; color: #00bcd4;">{best_offset} frames</div>
                            </div>
                        </div>
                    </div>
                    """)
                
                # Render Visualization Tabs
                tab_visuals, tab_leaderboard = st.tabs([
                    "📊 Intermediate Step Visualizations",
                    "🏆 Match Candidates Leaderboard"
                ])
                
                with tab_visuals:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("1. Spectrogram (STFT)")
                        fig_spec, ax_spec = plt.subplots(figsize=(6, 4))
                        img = ax_spec.imshow(spec, origin='lower', aspect='auto', 
                                              extent=[times[0], times[-1], freqs[0], freqs[-1]],
                                              cmap='magma')
                        cbar = fig_spec.colorbar(img, ax=ax_spec)
                        cbar.set_label("Magnitude (dB)", color="#aaaaaa")
                        cbar.ax.yaxis.set_tick_params(color='#888888', labelcolor='#888888')
                        ax_spec.set_xlabel("Time (s)")
                        ax_spec.set_ylabel("Frequency (Hz)")
                        st.pyplot(fig_spec)
                        st.caption("A spectrogram visualizes sound frequency (y-axis) over time (x-axis), with brightness representing loudness (dB).")
                        
                    with col2:
                        st.subheader("2. Constellation Map (Sparse Peaks)")
                        fig_peaks, ax_peaks = plt.subplots(figsize=(6, 4))
                        
                        if peaks:
                            t_coords = [times[p[0]] for p in peaks]
                            f_coords = [freqs[p[1]] for p in peaks]
                            ax_peaks.scatter(t_coords, f_coords, c='#1DB954', marker='o', s=15, alpha=0.8)
                            
                        ax_peaks.set_xlim(times[0], times[-1])
                        ax_peaks.set_ylim(freqs[0], freqs[-1])
                        ax_peaks.set_xlabel("Time (s)")
                        ax_peaks.set_ylabel("Frequency (Hz)")
                        ax_peaks.grid(True, linestyle='--', alpha=0.3)
                        st.pyplot(fig_peaks)
                        st.caption(f"Detected {len(peaks)} local maximum peaks. This 'constellation map' forms a robust, noise-tolerant summary of the song's audio content.")
                    
                    # Row 2: Offset Histogram
                    st.subheader("3. Offset Alignment Histogram")
                    st.write(f"Showing the distribution of time offset differences ($\\Delta \\tau = t_{{db}} - t_{{query}}$) for **{best_song_title}**.")
                    
                    diffs = matches[best_song_id]
                    fig_hist, ax_hist = plt.subplots(figsize=(10, 4))
                    
                    # Select range around the best offset to make the peak visually striking
                    min_bin = best_offset - 100
                    max_bin = best_offset + 100
                    filtered_diffs = [d for d in diffs if min_bin <= d <= max_bin]
                    
                    if filtered_diffs:
                        ax_hist.hist(filtered_diffs, bins=200, color='#1DB954', edgecolor='none', alpha=0.8)
                        ax_hist.axvline(best_offset, color='#ff4b4b', linestyle='--', linewidth=1.5, 
                                        label=f"True Alignment Peak (Offset = {best_offset})")
                        ax_hist.legend(facecolor='#1e1e1e', edgecolor='#333333')
                    else:
                        ax_hist.hist(diffs, bins=50, color='#1DB954', edgecolor='none', alpha=0.8)
                        
                    ax_hist.set_xlabel("Time Offset Difference (frames)")
                    ax_hist.set_ylabel("Match Count")
                    ax_hist.set_title(f"Offset Alignment Histogram for '{best_song_title}'")
                    ax_hist.grid(True, linestyle=':', alpha=0.3)
                    st.pyplot(fig_hist)
                    st.caption("A sharp, prominent peak indicates that many hashes from the query matched the song at the exact same relative time difference, proving a genuine match. Random matches create a low, flat background noise.")
                    
                with tab_leaderboard:
                    st.subheader("Leaderboard - Match Candidates")
                    leaderboard_data = []
                    for song_id, peak_sc, total_m, offset in scores:
                        leaderboard_data.append({
                            "Song Title": song_names.get(song_id, f"Unknown Song (ID: {song_id})"),
                            "Peak Alignment Score": peak_sc,
                            "Total Matching Hashes": total_m,
                            "Time Offset (frames)": offset
                        })
                    st.table(pd.DataFrame(leaderboard_data))
    else:
        # Home screen instructions
        st.html("""
        <div class="landing-container">
            <div class="landing-header">
                <h2 style="margin: 0; font-weight: 800; font-size: 2.2rem; color: #ffffff;">🎵 Audio Recognition Dashboard</h2>
                <p style="margin: 5px 0 0 0; color: #aaaaaa; font-size: 1.1rem;">Landmark-based Audio Fingerprinting & Song Recognition</p>
            </div>
            
            <div class="steps-grid">
                <div class="step-card">
                    <div class="step-icon">📁</div>
                    <div class="step-title">1. Audio Database</div>
                    <div class="step-desc">Configure the directory of MP3 audio tracks on the sidebar and scan/index to build the database hashes.</div>
                </div>
                <div class="step-card">
                    <div class="step-icon">📤</div>
                    <div class="step-title">2. Upload Query</div>
                    <div class="step-desc">Upload a short, noisy, or modified audio snippet (wav/mp3/m4a) that you want to recognize.</div>
                </div>
                <div class="step-card">
                    <div class="step-icon">🔍</div>
                    <div class="step-title">3. Identify Song</div>
                    <div class="step-desc">Click the 'Identify Song' button to match the query against the database in real-time.</div>
                </div>
            </div>
        </div>
        """)

else:
    st.write("Upload a folder/set of query audio files to predict all tracks in batch mode and export a `results.csv` file.")
    
    uploaded_files = st.file_uploader("Upload Query Audio Files", type=["wav", "mp3", "m4a"], accept_multiple_files=True)
    
    if uploaded_files:
        st.write(f"Loaded **{len(uploaded_files)}** files. Click 'Identify Batch' to execute the batch recognition.")
        
        # Identify Batch Button
        if st.button("🚀 Identify Batch"):
            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Temporary directory to process audio
            temp_dir = "temp_batch"
            os.makedirs(temp_dir, exist_ok=True)
            
            for idx, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"Processing ({idx+1}/{len(uploaded_files)}): {uploaded_file.name}...")
                
                # Write to temp path
                temp_path = os.path.join(temp_dir, uploaded_file.name)
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                try:
                    # Run identification steps with default stable parameters
                    y, sr = fp.load_audio(temp_path)
                    spec, freqs, times = fp.compute_spectrogram(y, sr)
                    peaks = fp.find_peaks(spec)
                    fingerprints = fp.generate_fingerprints(peaks)
                    
                    matches, song_names = db.match_fingerprints(DB_PATH, fingerprints)
                    scores = db.score_matches(matches)
                    
                    if not scores:
                        prediction = ""
                    else:
                        best_song_id, peak_score, _, _ = scores[0]
                        if peak_score < 20:
                            prediction = ""  # Song not in dataset
                        else:
                            prediction = song_names.get(best_song_id, "")
                        
                except Exception as e:
                    prediction = f"Error: {str(e)}"
                
                # Clean up temp file
                try:
                    os.remove(temp_path)
                except:
                    pass
                
                results.append({
                    "filename": uploaded_file.name,
                    "prediction": prediction
                })
                
                progress_bar.progress((idx + 1) / len(uploaded_files))
                
            status_text.text("Batch identification complete!")
            st.balloons()
            
            # Clean up temp batch directory
            try:
                os.rmdir(temp_dir)
            except:
                pass
                
            # Create DataFrame
            df = pd.DataFrame(results)
            
            # Save physically to disk
            df.to_csv("results.csv", index=False)
            
            # Show Table
            st.subheader("Batch Recognition Results")
            st.table(df)
            st.success("Successfully generated results.csv in the application directory!")
            
            # Download CSV
            csv_data = df.to_csv(index=False)
            st.download_button(
                label="📥 Download results.csv",
                data=csv_data,
                file_name="results.csv",
                mime="text/csv"
            )
