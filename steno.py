import wave
import numpy as np
import os
import struct
import tempfile

uploads_dir = tempfile.gettempdir()
uploads_dir = os.path.join(uploads_dir, "steno")

def encode(audio, filename, message):
    """LSB encoding for audio files"""
    frames = audio.getframes(-1)
    sound_info = list(struct.unpack("<" + str(len(frames)) + "B", frames))
    
    # Convert message to binary
    message += "####"  # Delimiter
    binary_message = ''.join(format(ord(char), '08b') for char in message)
    
    # Check if audio file is large enough
    if len(binary_message) > len(sound_info):
        raise ValueError("Audio file too small for message")
    
    # Encode message into LSBs
    for i in range(len(binary_message)):
        if binary_message[i] == '0':
            sound_info[i] = sound_info[i] & 0xFE
        else:
            sound_info[i] = sound_info[i] | 0x01
    
    # Write encoded audio
    output_path = os.path.join(uploads_dir, filename + "encoded")
    with wave.open(output_path, 'wb') as output_audio:
        output_audio.setparams(audio.getparams())
        output_audio.writeframes(struct.pack("<" + str(len(sound_info)) + "B", *sound_info))
    
    audio.close()

def decode(audio, filename):
    """LSB decoding for audio files"""
    frames = audio.getframes(-1)
    sound_info = list(struct.unpack("<" + str(len(frames)) + "B", frames))
    
    # Extract LSBs
    binary_message = ""
    for byte in sound_info:
        binary_message += str(byte & 1)
    
    # Convert binary to text
    message = ""
    for i in range(0, len(binary_message), 8):
        byte = binary_message[i:i+8]
        if len(byte) == 8:
            char = chr(int(byte, 2))
            message += char
            if message.endswith("####"):
                return message[:-4]
    
    audio.close()
    return "No hidden message found"

def phase_encode(audio, path, filename, message):
    """Phase encoding for audio files"""
    frames = audio.readframes(-1)
    audio_data = np.frombuffer(frames, dtype=np.int16)
    
    message += "####"
    binary_message = ''.join(format(ord(char), '08b') for char in message)
    
    segment_length = len(audio_data) // len(binary_message)
    
    for i, bit in enumerate(binary_message):
        start_idx = i * segment_length
        end_idx = min((i + 1) * segment_length, len(audio_data))
        
        if bit == '1':
            audio_data[start_idx:end_idx] = -audio_data[start_idx:end_idx]
    
    output_path = os.path.join(uploads_dir, filename + "encoded")
    with wave.open(output_path, 'wb') as output_audio:
        output_audio.setparams(audio.getparams())
        output_audio.writeframes(audio_data.tobytes())
    
    audio.close()

def phase_decode(audio, filename, path):
    """Phase decoding for audio files"""
    frames = audio.readframes(-1)
    audio_data = np.frombuffer(frames, dtype=np.int16)
    
    message = "Phase decoding not fully implemented"
    
    audio.close()
    return message