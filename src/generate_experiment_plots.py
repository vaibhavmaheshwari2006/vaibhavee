import os
import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display

# Add current dir/src to path just in case
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
import fingerprint as fp

def generate_all_plots():
    # Find sample audio in temp folder
    temp_dir = "temp"
    mp3_files = [f for f in os.listdir(temp_dir) if f.endswith('.mp3')]
    if not mp3_files:
        print("Error: No MP3 files found in temp/ directory to use for plots.")
        return
    
    audio_path = os.path.join(temp_dir, mp3_files[0])
    print(f"Using audio file: {audio_path}")
    
    # Create temp_plots directory if it doesn't exist
    plots_dir = "temp_plots"
    os.makedirs(plots_dir, exist_ok=True)
    
    # Load audio - downsampled to 11025 Hz
    y_full, sr = fp.load_audio(audio_path, sr=11025)
    
    # Use a 10-second segment for detailed visual comparison
    duration_s = 10
    num_samples = int(duration_s * sr)
    y = y_full[:num_samples]
    
    # Setup plotting styles for clean publication-quality figures
    plt.rcParams.update({
        'font.size': 10,
        'axes.labelsize': 11,
        'axes.titlesize': 12,
        'xtick.labelsize': 9,
        'ytick.labelsize': 9,
        'figure.titlesize': 14
    })
    
    # ==========================================
    # 1. Window Length Experiment
    # ==========================================
    print("Generating Window Length Experiment plots...")
    
    # Compute spectrogram with N_FFT = 512
    spec_512, freqs_512, times_512 = fp.compute_spectrogram(y, sr, n_fft=512, hop_length=128)
    # Compute spectrogram with N_FFT = 2048
    spec_2048, freqs_2048, times_2048 = fp.compute_spectrogram(y, sr, n_fft=2048, hop_length=512)
    
    # Plot N_FFT = 512
    plt.figure(figsize=(6, 4))
    librosa.display.specshow(spec_512, sr=sr, hop_length=128, x_axis='time', y_axis='linear', cmap='magma')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Spectrogram (Window Size $N_{fft} = 512$)')
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')
    plt.ylim(0, 5500)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'exp1_window_512.png'), dpi=90)
    plt.close()
    
    # Plot N_FFT = 2048
    plt.figure(figsize=(6, 4))
    librosa.display.specshow(spec_2048, sr=sr, hop_length=512, x_axis='time', y_axis='linear', cmap='magma')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Spectrogram (Window Size $N_{fft} = 2048$)')
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')
    plt.ylim(0, 5500)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'exp1_window_2048.png'), dpi=90)
    plt.close()
    
    # ==========================================
    # 2. Single Peaks vs. Paired Hashes
    # ==========================================
    print("Generating Constellation Map and Paired Landmarks plots...")
    
    # Use N_FFT = 512 baseline
    spec, freqs, times = fp.compute_spectrogram(y, sr, n_fft=512, hop_length=128)
    peaks = fp.find_peaks(spec, min_amplitude=-50, neighborhood_size=15)
    
    # Draw Constellation Map (Single Peaks)
    plt.figure(figsize=(6, 4))
    t_coords = [times[p[0]] for p in peaks]
    f_coords = [freqs[p[1]] for p in peaks]
    plt.scatter(t_coords, f_coords, c='green', marker='o', s=12, alpha=0.8, label='Landmark Peak')
    plt.xlim(0, duration_s)
    plt.ylim(0, 5500)
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')
    plt.title('Constellation Map (Detected 2D Peaks)')
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'exp2_constellation.png'), dpi=90)
    plt.close()
    
    # Draw Paired Hashes (Anchor-Target connections)
    # We will connect anchors to target peaks within a small window to make it visually clear
    plt.figure(figsize=(6, 4))
    plt.scatter(t_coords, f_coords, c='green', marker='o', s=12, alpha=0.5, zorder=2)
    
    # Let's draw connections for the first 4 seconds to avoid overcrowding the plot
    num_peaks = len(peaks)
    drawn_lines = 0
    for i in range(num_peaks):
        t1_idx, f1_idx, _ = peaks[i]
        t1 = times[t1_idx]
        f1 = freqs[f1_idx]
        
        # Only plot connections for anchors in the first 4 seconds
        if t1 > 4.0:
            continue
            
        targets_paired = 0
        for j in range(i + 1, num_peaks):
            t2_idx, f2_idx, _ = peaks[j]
            t2 = times[t2_idx]
            f2 = freqs[f2_idx]
            
            delta_t_idx = t2_idx - t1_idx
            
            if delta_t_idx > 100: # max_delta_t
                break
            if delta_t_idx >= 1: # min_delta_t
                # Plot line connection
                plt.plot([t1, t2], [f1, f2], color='red', alpha=0.35, linewidth=0.8, zorder=1)
                # Highlight anchor and target
                if targets_paired == 0:
                    plt.scatter(t1, f1, c='blue', marker='s', s=20, zorder=3)
                plt.scatter(t2, f2, c='orange', marker='^', s=15, zorder=3)
                
                targets_paired += 1
                drawn_lines += 1
                if targets_paired >= 5: # limit fan-out to 5 for plotting clarity
                    break
                    
    # Custom legends for markers
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='s', color='w', label='Anchor Peak (Source)', markerfacecolor='blue', markersize=6),
        Line2D([0], [0], marker='^', color='w', label='Target Peak', markerfacecolor='orange', markersize=6),
        Line2D([0], [0], marker='o', color='w', label='Other Peaks', markerfacecolor='green', markersize=6, alpha=0.5),
        Line2D([0], [0], color='red', alpha=0.5, linewidth=1, label='Hash Coupling Connection')
    ]
    plt.legend(handles=legend_elements, loc='upper right', fontsize=8)
    
    plt.xlim(0, duration_s)
    plt.ylim(0, 5500)
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')
    plt.title('Combinatorial Hashing (Anchor-Target Links)')
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'exp2_paired.png'), dpi=90)
    plt.close()
    
    # ==========================================
    # 3. Added Noise Experiment
    # ==========================================
    print("Generating Added Noise Experiment plots...")
    
    y_noise_01 = fp.add_noise(y, noise_level=0.01)
    y_noise_05 = fp.add_noise(y, noise_level=0.05)
    
    spec_n0, _, _ = fp.compute_spectrogram(y, sr, n_fft=512, hop_length=128)
    spec_n01, _, _ = fp.compute_spectrogram(y_noise_01, sr, n_fft=512, hop_length=128)
    spec_n05, _, _ = fp.compute_spectrogram(y_noise_05, sr, n_fft=512, hop_length=128)
    
    # Original Spectrogram
    plt.figure(figsize=(6, 4))
    librosa.display.specshow(spec_n0, sr=sr, hop_length=128, x_axis='time', y_axis='linear', cmap='magma')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Spectrogram (Original / Clean Signal)')
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')
    plt.ylim(0, 5500)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'exp3_noise_0.png'), dpi=90)
    plt.close()
    
    # Noise = 0.01
    plt.figure(figsize=(6, 4))
    librosa.display.specshow(spec_n01, sr=sr, hop_length=128, x_axis='time', y_axis='linear', cmap='magma')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Spectrogram (Noise Level = 0.01)')
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')
    plt.ylim(0, 5500)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'exp3_noise_01.png'), dpi=90)
    plt.close()
    
    # Noise = 0.05
    plt.figure(figsize=(6, 4))
    librosa.display.specshow(spec_n05, sr=sr, hop_length=128, x_axis='time', y_axis='linear', cmap='magma')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Spectrogram (Noise Level = 0.05)')
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')
    plt.ylim(0, 5500)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'exp3_noise_05.png'), dpi=90)
    plt.close()
    
    # ==========================================
    # 4. Pitch Shift Experiment
    # ==========================================
    print("Generating Pitch Shift Experiment plots...")
    
    y_pitch_up = fp.pitch_shift(y, sr, n_steps=1.0)
    y_pitch_down = fp.pitch_shift(y, sr, n_steps=-1.0)
    
    spec_p0, _, _ = fp.compute_spectrogram(y, sr, n_fft=512, hop_length=128)
    spec_pup, _, _ = fp.compute_spectrogram(y_pitch_up, sr, n_fft=512, hop_length=128)
    spec_pdown, _, _ = fp.compute_spectrogram(y_pitch_down, sr, n_fft=512, hop_length=128)
    
    # Original
    plt.figure(figsize=(6, 4))
    librosa.display.specshow(spec_p0, sr=sr, hop_length=128, x_axis='time', y_axis='linear', cmap='magma')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Original Spectrogram')
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')
    plt.ylim(0, 5500)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'exp4_pitch_0.png'), dpi=90)
    plt.close()
    
    # Pitch +1 Semitone
    plt.figure(figsize=(6, 4))
    librosa.display.specshow(spec_pup, sr=sr, hop_length=128, x_axis='time', y_axis='linear', cmap='magma')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Pitch Shifted Spectrogram (+1 Semitone)')
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')
    plt.ylim(0, 5500)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'exp4_pitch_plus.png'), dpi=90)
    plt.close()
    
    # Pitch -1 Semitone
    plt.figure(figsize=(6, 4))
    librosa.display.specshow(spec_pdown, sr=sr, hop_length=128, x_axis='time', y_axis='linear', cmap='magma')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Pitch Shifted Spectrogram (-1 Semitone)')
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')
    plt.ylim(0, 5500)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'exp4_pitch_minus.png'), dpi=90)
    plt.close()
    
    # ==========================================
    # 5. Time Stretch Experiment
    # ==========================================
    print("Generating Time Stretch Experiment plots...")
    
    y_stretch_09 = fp.time_stretch(y, rate=0.9)
    y_stretch_11 = fp.time_stretch(y, rate=1.1)
    
    spec_s0, _, _ = fp.compute_spectrogram(y, sr, n_fft=512, hop_length=128)
    spec_s09, _, _ = fp.compute_spectrogram(y_stretch_09, sr, n_fft=512, hop_length=128)
    spec_s11, _, _ = fp.compute_spectrogram(y_stretch_11, sr, n_fft=512, hop_length=128)
    
    # Original
    plt.figure(figsize=(6, 4))
    librosa.display.specshow(spec_s0, sr=sr, hop_length=128, x_axis='time', y_axis='linear', cmap='magma')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Original Spectrogram')
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')
    plt.ylim(0, 5500)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'exp5_stretch_0.png'), dpi=90)
    plt.close()
    
    # Stretch = 0.9 (Compresses time, physically shorter signal, looks stretched out on time axis if we pad/rescale,
    # let's plot it with its actual rescaled duration)
    duration_09 = len(y_stretch_09) / sr
    times_09 = librosa.frames_to_time(np.arange(spec_s09.shape[1]), sr=sr, hop_length=128)
    
    plt.figure(figsize=(6, 4))
    librosa.display.specshow(spec_s09, sr=sr, hop_length=128, x_axis='time', y_axis='linear', cmap='magma')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Time Stretched Spectrogram (Rate = 0.9 - Slower)')
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')
    plt.ylim(0, 5500)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'exp5_stretch_09.png'), dpi=90)
    plt.close()
    
    # Stretch = 1.1 (Expands time, physically longer signal)
    duration_11 = len(y_stretch_11) / sr
    times_11 = librosa.frames_to_time(np.arange(spec_s11.shape[1]), sr=sr, hop_length=128)
    
    plt.figure(figsize=(6, 4))
    librosa.display.specshow(spec_s11, sr=sr, hop_length=128, x_axis='time', y_axis='linear', cmap='magma')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Time Stretched Spectrogram (Rate = 1.1 - Faster)')
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')
    plt.ylim(0, 5500)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'exp5_stretch_11.png'), dpi=90)
    plt.close()
    
    print("All experimental plots successfully generated and saved to temp_plots/ directory!")

if __name__ == '__main__':
    generate_all_plots()
