import numpy as np
import librosa
import scipy.ndimage as ndimage

def load_audio(filepath, sr=11025):
    """
    Load an audio file, downsample it, and convert to mono.
    """
    y, loaded_sr = librosa.load(filepath, sr=sr, mono=True)
    return y, loaded_sr

def compute_spectrogram(y, sr=11025, n_fft=512, hop_length=128):
    """
    Compute the Short-Time Fourier Transform (STFT) and convert to dB scale.
    Returns:
        spectrogram_db: 2D array of decibel magnitudes
        frequencies: array of frequency bin values (Hz)
        times: array of time values (seconds)
    """
    # Compute STFT
    S = librosa.stft(y, n_fft=n_fft, hop_length=hop_length, win_length=n_fft, window='hamming')
    S_abs = np.abs(S)
    
    # Convert to dB scale (avoid log of zero)
    spectrogram_db = librosa.amplitude_to_db(S_abs, ref=np.max)
    
    # Frequency and time grids
    frequencies = librosa.fft_frequencies(sr=sr, n_fft=n_fft)
    times = librosa.frames_to_time(np.arange(S_abs.shape[1]), sr=sr, hop_length=hop_length)
    
    return spectrogram_db, frequencies, times

def find_peaks(spectrogram_db, min_amplitude=-50, neighborhood_size=15):
    """
    Find local peaks in the 2D spectrogram using a maximum filter.
    Returns a list of tuples: (time_index, freq_index, amplitude)
    """
    # 2D maximum filter
    data_max = ndimage.maximum_filter(spectrogram_db, size=neighborhood_size, mode='constant', cval=-np.inf)
    
    # Locate peaks: where the original is the local maximum and above amplitude threshold
    peaks_mask = (spectrogram_db == data_max) & (spectrogram_db > min_amplitude)
    
    # Extract coordinates
    freq_indices, time_indices = np.where(peaks_mask)
    
    peaks = []
    for t_idx, f_idx in zip(time_indices, freq_indices):
        amp = spectrogram_db[f_idx, t_idx]
        peaks.append((t_idx, f_idx, amp))
        
    # Sort peaks by time index primarily, and then amplitude
    peaks.sort(key=lambda x: (x[0], -x[2]))
    return peaks

def generate_fingerprints(peaks, fan_value=15, min_delta_t=1, max_delta_t=100):
    """
    Generate hashes by pairing nearby peaks.
    For each anchor peak (t1, f1), search forward in time for up to 'fan_value' target peaks
    within the time interval [t1 + min_delta_t, t1 + max_delta_t].
    
    Returns:
        A list of tuples: (hash_str, offset_t1)
        where hash_str = "f1:f2:delta_t"
        and offset_t1 is the index t1 (absolute time offset from the start)
    """
    fingerprints = []
    num_peaks = len(peaks)
    
    for i in range(num_peaks):
        t1, f1, _ = peaks[i]
        
        # Look for target peaks forward in time
        targets_paired = 0
        for j in range(i + 1, num_peaks):
            t2, f2, _ = peaks[j]
            
            delta_t = t2 - t1
            
            # Since peaks are sorted by time, if delta_t exceeds max_delta_t, we can stop searching for this anchor
            if delta_t > max_delta_t:
                break
                
            if delta_t >= min_delta_t:
                # Create a deterministic string hash
                hash_str = f"{f1}:{f2}:{delta_t}"
                fingerprints.append((hash_str, t1))
                targets_paired += 1
                
                # Limit the fan-out
                if targets_paired >= fan_value:
                    break
                    
    return fingerprints

# Audio degradation / robustness functions

def add_noise(y, noise_level=0.005):
    """
    Add white Gaussian noise to the signal.
    """
    if noise_level <= 0:
        return y
    noise = np.random.normal(0, noise_level, len(y))
    return y + noise

def pitch_shift(y, sr=11025, n_steps=0.5):
    """
    Shift pitch by n_steps semitones.
    """
    if n_steps == 0:
        return y
    return librosa.effects.pitch_shift(y, sr=sr, n_steps=n_steps)

def time_stretch(y, rate=1.05):
    """
    Stretch or compress time by rate.
    """
    if rate == 1.0 or rate == 0:
        return y
    return librosa.effects.time_stretch(y, rate=rate)
