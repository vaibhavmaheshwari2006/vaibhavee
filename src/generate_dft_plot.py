import os
import numpy as np
import matplotlib.pyplot as plt
import sys

# Ensure project root is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src import fingerprint as fp

def generate_entire_song_dft():
    temp_dir = "temp"
    plots_dir = "temp_plots"
    os.makedirs(plots_dir, exist_ok=True)
    
    mp3_files = [f for f in os.listdir(temp_dir) if f.endswith('.mp3')]
    if not mp3_files:
        print("Error: No MP3 files found in temp/ directory.")
        return
        
    audio_path = os.path.join(temp_dir, mp3_files[0])
    print(f"Loading full audio file for DFT: {audio_path}")
    
    # Load audio (downsampled to 11025 Hz as configured in system)
    sr = 11025
    y, sr = fp.load_audio(audio_path, sr=sr)
    
    print("Computing FFT of the entire song...")
    # Compute FFT
    fft_vals = np.fft.fft(y)
    n = len(y)
    
    # Compute corresponding frequency values in Hz
    freqs = np.fft.fftfreq(n, d=1/sr)
    
    # Get magnitude
    magnitude = np.abs(fft_vals)
    
    # Only keep positive frequencies
    positive_mask = freqs >= 0
    freqs = freqs[positive_mask]
    magnitude = magnitude[positive_mask]
    
    # Normalize magnitude for visual clarity if needed
    # Convert to dB relative to max magnitude to keep it consistent with other plots
    max_val = np.max(magnitude)
    if max_val > 0:
        magnitude_db = 20 * np.log10(magnitude / max_val)
    else:
        magnitude_db = magnitude
        
    print("Plotting DFT Magnitude spectrum...")
    plt.figure(figsize=(8, 4.5))
    plt.plot(freqs, magnitude_db, color='purple', alpha=0.85, linewidth=0.7)
    plt.grid(True, linestyle='--', alpha=0.3)
    
    plt.title("Discrete Fourier Transform (DFT) Magnitude of Entire Song")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude (dB, relative to max)")
    plt.xlim(0, sr/2) # Limit to Nyquist frequency
    plt.ylim(-100, 5) # Show down to -100 dB
    
    plt.tight_layout()
    plot_output_path = os.path.join(plots_dir, 'dft_entire_song.png')
    plt.savefig(plot_output_path, dpi=120)
    plt.close()
    
    print(f"Entire song DFT plot saved to: {plot_output_path}")

if __name__ == '__main__':
    generate_entire_song_dft()
