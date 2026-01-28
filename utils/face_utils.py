import face_recognition
import numpy as np
import pickle
import os
import base64
import cv2
from datetime import datetime
import pandas as pd
from PIL import Image
import io

class FaceRecognitionSystem:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_user_ids = []
        self.encodings_file = 'models/face_encodings.pkl'
        self.attendance_file = 'data/attendance/attendance.csv'
        self.load_known_faces()
        
    def load_known_faces(self):
        """Load known face encodings from file"""
        if os.path.exists(self.encodings_file):
            with open(self.encodings_file, 'rb') as f:
                data = pickle.load(f)
                self.known_face_encodings = data['encodings']
                self.known_face_names = data['names']
                self.known_user_ids = data['user_ids']
            print(f"Loaded {len(self.known_face_names)} known faces")
        else:
            print("No existing face encodings found")
    
    def save_known_faces(self):
        """Save known face encodings to file"""
        data = {
            'encodings': self.known_face_encodings,
            'names': self.known_face_names,
            'user_ids': self.known_user_ids
        }
        with open(self.encodings_file, 'wb') as f:
            pickle.dump(data, f)
        print("Face encodings saved")
    
    def decode_image(self, image_data):
        """Decode base64 image to numpy array"""
        # Remove data URL prefix if present
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        # Decode base64
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB numpy array
        image_np = np.array(image)
        
        # Convert RGBA to RGB if necessary
        if image_np.shape[-1] == 4:
            image_np = cv2.cvtColor(image_np, cv2.COLOR_RGBA2RGB)
        
        return image_np
    
    def register_face(self, name, user_id, image):
        """Register a new face"""
        try:
            # Check if user already exists
            if user_id in self.known_user_ids:
                return False, "User ID already registered"
            
            # Find face locations and encodings
            face_locations = face_recognition.face_locations(image)
            
            if len(face_locations) == 0:
                return False, "No face detected in image"
            
            if len(face_locations) > 1:
                return False, "Multiple faces detected. Please ensure only one face is in the frame"
            
            # Get face encoding
            face_encodings = face_recognition.face_encodings(image, face_locations)
            face_encoding = face_encodings[0]
            
            # Add to known faces
            self.known_face_encodings.append(face_encoding)
            self.known_face_names.append(name)
            self.known_user_ids.append(user_id)
            
            # Save face image
            face_dir = f'data/faces/{user_id}'
            os.makedirs(face_dir, exist_ok=True)
            
            # Save original image
            cv2.imwrite(f'{face_dir}/face.jpg', cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
            
            # Save encodings
            self.save_known_faces()
            
            return True, f"Successfully registered {name} (ID: {user_id})"
            
        except Exception as e:
            return False, f"Error during registration: {str(e)}"
    
    def identify_face(self, image):
        """Identify a face in the image"""
        try:
            # Find face locations
            face_locations = face_recognition.face_locations(image)
            
            if len(face_locations) == 0:
                return "Unknown", "", 0.0
            
            # Get face encodings
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            if len(face_encodings) == 0:
                return "Unknown", "", 0.0
            
            face_encoding = face_encodings[0]
            
            # Compare with known faces
            if len(self.known_face_encodings) == 0:
                return "Unknown", "", 0.0
            
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            
            # Threshold for recognition (lower is better, 0.6 is standard)
            if face_distances[best_match_index] < 0.6:
                name = self.known_face_names[best_match_index]
                user_id = self.known_user_ids[best_match_index]
                confidence = round((1 - face_distances[best_match_index]) * 100, 2)
                return name, user_id, confidence
            else:
                return "Unknown", "", 0.0
                
        except Exception as e:
            print(f"Error in identify_face: {str(e)}")
            return "Unknown", "", 0.0
    
    def mark_attendance(self, user_id, name, action):
        """Mark attendance (punch-in or punch-out)"""
        try:
            timestamp = datetime.now()
            date = timestamp.strftime('%Y-%m-%d')
            time = timestamp.strftime('%H:%M:%S')
            
            # Create attendance record
            record = {
                'user_id': user_id,
                'name': name,
                'date': date,
                'time': time,
                'action': action,
                'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Load existing attendance or create new DataFrame
            if os.path.exists(self.attendance_file):
                df = pd.read_csv(self.attendance_file)
            else:
                df = pd.DataFrame(columns=['user_id', 'name', 'date', 'time', 'action', 'timestamp'])
            
            # Check for duplicate within last 5 minutes
            if len(df) > 0:
                recent = df[(df['user_id'] == user_id) & 
                           (df['action'] == action) & 
                           (df['date'] == date)]
                if len(recent) > 0:
                    last_time = pd.to_datetime(recent.iloc[-1]['timestamp'])
                    current_time = pd.to_datetime(timestamp)
                    time_diff = (current_time - last_time).total_seconds() / 60
                    
                    if time_diff < 5:
                        return False, f"Already marked {action} within last 5 minutes"
            
            # Add new record
            df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
            
            # Save attendance
            os.makedirs(os.path.dirname(self.attendance_file), exist_ok=True)
            df.to_csv(self.attendance_file, index=False)
            
            return True, f"Successfully marked {action} for {name} at {time}"
            
        except Exception as e:
            return False, f"Error marking attendance: {str(e)}"
    
    def get_attendance_records(self):
        """Get all attendance records"""
        try:
            if os.path.exists(self.attendance_file):
                df = pd.read_csv(self.attendance_file)
                return df.to_dict('records')
            return []
        except Exception as e:
            print(f"Error getting attendance records: {str(e)}")
            return []
    
    def get_attendance_report(self, start_date=None, end_date=None):
        """Get attendance report for date range"""
        try:
            if not os.path.exists(self.attendance_file):
                return []
            
            df = pd.read_csv(self.attendance_file)
            
            if start_date:
                df = df[df['date'] >= start_date]
            if end_date:
                df = df[df['date'] <= end_date]
            
            return df.to_dict('records')
        except Exception as e:
            print(f"Error getting attendance report: {str(e)}")
            return []
    
    def get_registered_users(self):
        """Get list of registered users"""
        users = []
        for i in range(len(self.known_face_names)):
            users.append({
                'name': self.known_face_names[i],
                'user_id': self.known_user_ids[i]
            })
        return users
