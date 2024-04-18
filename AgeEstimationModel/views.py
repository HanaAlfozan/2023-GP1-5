from django.http import JsonResponse
import numpy as np
from tensorflow.keras.models import load_model
from PIL import Image
import io
import base64
from django.views.decorators.csrf import csrf_protect
import json
import cv2

# OpenCV Cascade Classifier for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Define class labels
class_labels = ['0-3', '4+', '9+', '12+', '17+']

model = None

def load_custom_model():
    global model
    try:
        # Load the model only once when the server starts
        model = load_model('AgeEstimationModel/Models/Facial_Age_Group_Estimation_Model.h5')
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Error loading the model: {e}")

# Load the model when the server starts
load_custom_model()

def preprocess_image_non_224(image_array, target_size=(224, 224), crop_margin=0.4):
    # Convert to grayscale
    gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
    
    # Detect faces in the image
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) > 0:
        # Assuming only one face is detected, extract and crop the face
        x, y, w, h = faces[0]
        
        # Calculate the margins for cropping
        margin_x = int(w * crop_margin)
        margin_y = int(h * crop_margin)
        
        # Calculate the cropping boundaries
        crop_x1 = max(x - margin_x, 0)
        crop_y1 = max(y - margin_y, 0)
        crop_x2 = min(x + w + margin_x, image_array.shape[1])
        crop_y2 = min(y + h + margin_y, image_array.shape[0])
        
        # Crop the face with margins
        cropped_face = image_array[crop_y1:crop_y2, crop_x1:crop_x2]

        # Resize the cropped face to the target size
        resized_face = cv2.resize(cropped_face, target_size) / 255.0

        return np.expand_dims(resized_face, axis=0)
    else:
        return None

def preprocess_image(image_array, target_size=(224, 224)):
    # Resize image to target size
    image_array = cv2.resize(image_array, target_size)
    # Convert to RGB
    image_array = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
    # Convert to NumPy array
    img_array = np.expand_dims(image_array, axis=0)
    # Rescale pixel values to [0, 1]
    img_array = img_array.astype('float32') / 255.0
    return img_array

@csrf_protect
def process_image(request):
    if request.method == 'POST':
        try:
            # Get the image_data from the request body using json.loads
            data = json.loads(request.body)
            image_data = data.get('image_data')
            
            if image_data:
                # Convert the base64 image data to a NumPy array
                image_data = image_data.split(',')[1]
                image_data = io.BytesIO(base64.b64decode(image_data))
                image = Image.open(image_data)
                
                # Use OpenCV to detect faces in the image
                image_array = np.array(image)
                gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

                if len(faces) > 0:
                    # Assuming only one face is detected, crop and resize the image
                    x, y, w, h = faces[0]
                    face_image = image_array[y:y+h, x:x+w]

                    # Determine the size of the face image
                    if face_image.shape[0] == 224 and face_image.shape[1] == 224:
                        face_image_preprocessed = preprocess_image(face_image)
                    else:
                        face_image_preprocessed = preprocess_image_non_224(face_image)

                    # Check if the model is loaded successfully
                    if model is not None:
                        # Preprocess the image and make predictions using your VGG model
                        predictions = model.predict(face_image_preprocessed)
                        
                        # Assuming predictions is a numpy array
                        predicted_class_index = np.argmax(predictions)
                        predicted_class_label = class_labels[predicted_class_index]
                        
                        # Include the predicted class label in the response
                        response_data = {
                            'Estimated Age Group': predicted_class_label
                        }

                        return JsonResponse(response_data)
                    else:
                        return JsonResponse({'error': 'Model not loaded'})
                else: 
                    return JsonResponse({'error': 'No face detected'})
            else:
                return JsonResponse({'error': 'Invalid image_data'})
            
        except Exception as e:
            print(f"Error processing the image: {e}")
            return JsonResponse({'error': str(e)})

    return JsonResponse({'error': 'Invalid request method'})