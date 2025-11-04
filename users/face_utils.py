import face_recognition
import numpy as np
from typing import Optional, Tuple
import base64
import re
import io
from PIL import Image
import pickle

def process_base64_image(base64_string):
    """Convert base64 image data to numpy array."""
    try:
        # Remove data URL prefix if present
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        # Decode base64 to bytes
        image_bytes = base64.b64decode(base64_string)
        
        # Convert to PIL Image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to numpy array
        return np.array(image)
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return None

def get_face_encoding(image_array):
    """Get face encoding from image array."""
    try:
        if image_array is None:
            return None
            
        # Get face locations
        face_locations = face_recognition.face_locations(image_array)
        if not face_locations:
            print("No face detected in the image")
            return None
            
        # Get face encodings
        face_encodings = face_recognition.face_encodings(image_array, face_locations)
        if not face_encodings:
            print("Could not encode face")
            return None
            
        return face_encodings[0]  # Return the first face encoding
    except Exception as e:
        print(f"Error getting face encoding: {str(e)}")
        return None

def verify_face(stored_encoding, image_array):
    """Verify if the face matches the stored encoding."""
    try:
        if image_array is None or stored_encoding is None:
            return False
            
        # Load stored encoding if it's serialized
        if isinstance(stored_encoding, (str, bytes)):
            stored_encoding = pickle.loads(stored_encoding)
            
        # Get face encoding from current image
        face_locations = face_recognition.face_locations(image_array)
        if not face_locations:
            print("No face detected in verification image")
            return False
            
        face_encodings = face_recognition.face_encodings(image_array, face_locations)
        if not face_encodings:
            print("Could not encode face in verification image")
            return False
            
        # Compare faces
        matches = face_recognition.compare_faces([stored_encoding], face_encodings[0], tolerance=0.6)
        return matches[0]
    except Exception as e:
        print(f"Error verifying face: {str(e)}")
        return False

def encode_face_data(face_encoding):
    """Serialize face encoding for storage."""
    try:
        return pickle.dumps(face_encoding)
    except Exception as e:
        print(f"Error encoding face data: {str(e)}")
        return None

def decode_face_data(face_data: bytes) -> np.ndarray:
    """Convert stored face data bytes back to numpy array."""
    return np.frombuffer(face_data, dtype=np.float64) 