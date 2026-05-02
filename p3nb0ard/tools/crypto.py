import base64
import urllib.parse


def decode_string(encoded_str: str) -> str:
    """
    Attempts to decode a string from various formats (Base64, Hex, URL encoding).
    Input must be the encoded string.
    """
    results = []
    
    # Try Base64
    try:
        # Pad string if needed
        padded = encoded_str + '=' * (-len(encoded_str) % 4)
        decoded = base64.b64decode(padded).decode('utf-8')
        results.append(f"Base64 Decode: {decoded}")
    except:
        pass
        
    # Try Hex
    try:
        decoded = bytes.fromhex(encoded_str).decode('utf-8')
        results.append(f"Hex Decode: {decoded}")
    except:
        pass
        
    # Try URL
    try:
        decoded = urllib.parse.unquote(encoded_str)
        if decoded != encoded_str:
            results.append(f"URL Decode: {decoded}")
    except:
        pass
        
    if not results:
        return "Could not decode string using known methods (Base64, Hex, URL)."
        
    return "\n".join(results)
