from helper import snow_encode, snow_decode, subs_encode, subs_decode, zw_encode, zw_decode

def txt_encode(cover_text, secret_message, method="snow", binary=False):
    """Encode a secret message into text using various steganography methods"""
    
    if method == "snow":
        encoded_message = snow_encode(secret_message, binary=binary)
        lines = cover_text.split('\n')
        result_lines = []
        
        chars_per_line = len(encoded_message) // max(1, len(lines))
        remaining_chars = len(encoded_message) % len(lines)
        
        start_idx = 0
        for i, line in enumerate(lines):
            chars_to_add = chars_per_line + (1 if i < remaining_chars else 0)
            end_idx = start_idx + chars_to_add
            
            if start_idx < len(encoded_message):
                line_encoding = encoded_message[start_idx:end_idx]
                result_lines.append(line + line_encoding)
            else:
                result_lines.append(line)
            
            start_idx = end_idx
        
        return '\n'.join(result_lines)
    
    elif method == "lookalike":
        return subs_encode(cover_text, secret_message, binary=binary)
    
    elif method == "zw":
        encoded_message = zw_encode(secret_message, binary=binary)
        result = ""
        message_idx = 0
        
        for char in cover_text:
            result += char
            if message_idx < len(encoded_message):
                result += encoded_message[message_idx]
                message_idx += 1
        
        while message_idx < len(encoded_message):
            result += encoded_message[message_idx]
            message_idx += 1
        
        return result
    
    else:
        raise ValueError(f"Unknown encoding method: {method}")

def txt_decode(encoded_text, method="snow", binary=False):
    """Decode a secret message from text using various steganography methods"""
    
    if method == "snow":
        lines = encoded_text.split('\n')
        extracted_chars = ""
        
        for line in lines:
            stripped_line = line.rstrip(' \t')
            trailing = line[len(stripped_line):]
            extracted_chars += trailing
        
        try:
            return snow_decode(extracted_chars, binary=binary)
        except:
            return "No hidden message found"
    
    elif method == "lookalike":
        try:
            return subs_decode(encoded_text, binary=binary)
        except:
            return "No hidden message found"
    
    elif method == "zw":
        zw_chars = "\u200C\u200D\u200E\u200F"
        extracted_chars = ""
        
        for char in encoded_text:
            if char in zw_chars:
                extracted_chars += char
        
        try:
            return zw_decode(extracted_chars, binary=binary)
        except:
            return "No hidden message found"
    
    else:
        raise ValueError(f"Unknown decoding method: {method}")