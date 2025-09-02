import cv2
import numpy as np
import os
import tempfile

uploads_dir = tempfile.gettempdir()
uploads_dir = os.path.join(uploads_dir, "steno")

def text_to_binary(text):
    """Convert text to binary representation"""
    return ''.join(format(ord(char), '08b') for char in text)

def binary_to_text(binary):
    """Convert binary representation to text"""
    text = ""
    for i in range(0, len(binary), 8):
        byte = binary[i:i+8]
        if len(byte) == 8:
            text += chr(int(byte, 2))
    return text

def encode_video(video_path, message, output_path=None):
    """Encode a message into a video using LSB steganography"""
    message += "####END####"
    binary_message = text_to_binary(message)
    
    cap = cv2.VideoCapture(video_path)
    
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    total_pixels = width * height * total_frames * 3
    if len(binary_message) > total_pixels:
        raise ValueError("Video too small for the message")
    
    if not output_path:
        filename = os.path.basename(video_path)
        name, ext = os.path.splitext(filename)
        output_path = os.path.join(uploads_dir, f"{name}_encoded{ext}")
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    message_index = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        if message_index < len(binary_message):
            frame = encode_frame(frame, binary_message, message_index)
            message_index = min(message_index + (width * height * 3), len(binary_message))
        
        out.write(frame)
    
    cap.release()
    out.release()
    
    return output_path

def encode_frame(frame, binary_message, start_index):
    """Encode part of the message into a single frame"""
    height, width, channels = frame.shape
    frame_flat = frame.flatten()
    
    for i in range(len(frame_flat)):
        if start_index + i < len(binary_message):
            bit = int(binary_message[start_index + i])
            frame_flat[i] = (frame_flat[i] & 0xFE) | bit
        else:
            break
    
    return frame_flat.reshape((height, width, channels))

def decode_video(video_path):
    """Decode a message from a video using LSB steganography"""
    cap = cv2.VideoCapture(video_path)
    
    binary_message = ""
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_flat = frame.flatten()
        for pixel in frame_flat:
            binary_message += str(pixel & 1)
        
        if len(binary_message) >= 88:
            try:
                current_text = binary_to_text(binary_message)
                if "####END####" in current_text:
                    cap.release()
                    return current_text.split("####END####")[0]
            except:
                continue
    
    cap.release()
    
    try:
        decoded = binary_to_text(binary_message)
        if "####END####" in decoded:
            return decoded.split("####END####")[0]
        else:
            return "No hidden message found"
    except:
        return "No hidden message found"
            