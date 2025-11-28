#!/usr/bin/env python3
"""
Auto Recording and PESQ Testing 
Voice-triggered recording for 15 seconds, then performs offset correction and PESQ testing
"""

import sounddevice as sd
import soundfile as sf
import numpy as np
from scipy.signal import correlate
from scipy.io import wavfile
from pesq import pesq
import argparse
import os
import glob


def get_next_number():
    """Get next available file number"""
    files = glob.glob("Degraded_*.wav")
    if not files:
        return 1
    numbers = []
    for f in files:
        # Extract number from filename like "Degraded_1.wav" or "Degraded_1_PESQ_4.210.wav"
        try:
            num_str = f.replace("Degraded_", "").split("_")[0].split(".")[0]
            numbers.append(int(num_str))
        except:
            continue
    return max(numbers) + 1 if numbers else 1


def record_with_voice_trigger(duration=15, threshold=0.03, sample_rate=8000):
    """
    Start recording when voice is detected
    
    Args:
        duration: Recording duration in seconds
        threshold: Voice detection threshold
        sample_rate: Sample rate
    
    Returns:
        audio: Recorded audio data
    """
    print("Waiting for voice trigger...")
    
    # Listen until voice is detected
    while True:
        chunk = sd.rec(int(0.1 * sample_rate), samplerate=sample_rate, channels=1)
        sd.wait()
        if np.abs(chunk).max() > threshold:
            break
    
    print(f"✓ Voice detected, recording for {duration} seconds...")
    
    # Record
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
    sd.wait()
    
    return audio.flatten()


def align_audio(ref_file, rec_audio, rec_sr):
    """Align audio and return offset"""
    ref, sr_ref = sf.read(ref_file)
    
    if ref.ndim > 1:
        ref = ref.mean(axis=1)
    
    if sr_ref != rec_sr:
        raise ValueError(f"Sample rate mismatch: reference={sr_ref}Hz, recorded={rec_sr}Hz")
    
    print("Calculating audio offset...")
    corr = correlate(rec_audio, ref, mode='full')
    lag = np.argmax(corr) - (len(ref) - 1)
    offset_sec = lag / sr_ref
    
    print(f"✓ Detected offset: {offset_sec*1000:.2f} ms")
    
    # Align
    if lag > 0:
        aligned = rec_audio[lag:]
    else:
        aligned = np.pad(rec_audio, (abs(lag), 0), mode='constant')
    
    min_len = min(len(aligned), len(ref))
    return aligned[:min_len], offset_sec


def calculate_pesq(ref_path, deg_audio, sample_rate):
    """Calculate PESQ score"""
    fs_ref, ref = wavfile.read(ref_path)
    
    if fs_ref != sample_rate:
        raise ValueError(f"Sample rate mismatch: {fs_ref} vs {sample_rate}")
    
    mode = 'nb' if sample_rate == 8000 else 'wb'
    mode_name = "narrowband" if mode == 'nb' else "wideband"
    
    print(f"Calculating PESQ score ({mode_name})...")
    
    # Convert to int16
    deg_int16 = (deg_audio * 32767).astype(np.int16)
    score = pesq(sample_rate, ref, deg_int16, mode)
    
    return score, mode_name


def main():
    parser = argparse.ArgumentParser(description='Auto recording, alignment and PESQ testing')
    parser.add_argument('reference', help='Reference audio file')
    parser.add_argument('-d', '--duration', type=int, default=25, help='Recording duration in seconds (default: 25)')
    parser.add_argument('-t', '--threshold', type=float, default=0.03, help='Voice detection threshold (default: 0.03)')
    parser.add_argument('-s', '--sample-rate', type=int, default=8000, 
                       choices=[8000, 16000], help='Sample rate (default: 8000)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.reference):
        print(f"Error: Reference file not found: {args.reference}")
        return
    
    number = get_next_number()
    filename = f"Degraded_{number}.wav"
    
    print("=" * 70)
    print("Auto Recording and PESQ Testing")
    print("=" * 70)
    print(f"Reference file: {args.reference}")
    print(f"Recording file: {filename}")
    print(f"Sample rate:    {args.sample_rate} Hz")
    print("=" * 70)
    print()
    
    try:
        # Record
        audio = record_with_voice_trigger(args.duration, args.threshold, args.sample_rate)
        
        # Save original recording
        sf.write(filename, audio, args.sample_rate)
        print(f"✓ Recording saved: {filename}")
        print()
        
        # Align audio
        print("[Step 1/2] Audio Alignment")
        print("-" * 70)
        aligned, offset = align_audio(args.reference, audio, args.sample_rate)
        
        # Save aligned audio
        aligned_filename = filename.replace('.wav', '_aligned.wav')
        sf.write(aligned_filename, aligned, args.sample_rate)
        print(f"✓ Aligned audio saved: {aligned_filename}")
        
        # Calculate PESQ
        print()
        print("[Step 2/2] PESQ Quality Assessment")
        print("-" * 70)
        score, mode = calculate_pesq(args.reference, aligned, args.sample_rate)
        
        # Rename files with PESQ score
        new_filename = f"Degraded_{number}_PESQ_{score:.3f}.wav"
        new_aligned_filename = f"Degraded_{number}_PESQ_{score:.3f}_aligned.wav"
        os.rename(filename, new_filename)
        os.rename(aligned_filename, new_aligned_filename)
        print(f"✓ Files renamed with PESQ score")
        
        # Display results
        print()
        print("=" * 70)
        print("RESULTS")
        print("=" * 70)
        print(f"Original file:      {new_filename}")
        print(f"Aligned file:       {new_aligned_filename}")
        print(f"Time Offset:        {offset*1000:+.2f} ms")
        print(f"PESQ Score ({mode}): {score:.3f}")
        print("=" * 70)
        
        # Rating
        if score >= 4.0:
            quality = "Excellent"
        elif score >= 3.5:
            quality = "Good"
        elif score >= 3.0:
            quality = "Fair"
        elif score >= 2.5:
            quality = "Poor"
        else:
            quality = "Bad"
        
        print(f"\nQuality Rating: {quality}")
        print("(PESQ scale: 1.0 = Bad, 4.5 = Excellent)")
        print("\n✓ Processing completed!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")


if __name__ == "__main__":
    main()
