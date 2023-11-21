from django.http import JsonResponse
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.vgg16 import preprocess_input
from PIL import Image
import io
import base64
from django.views.decorators.csrf import csrf_protect
import json
import cv2
import matplotlib.pyplot as plt
import tensorflow as tf

# OpenCV Cascade Classifier for face and eye detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

# Define class labels
class_labels = ['0-3', '12+', '17+', '4+', '9+']

model = None

def load_custom_model():
    global model
    try:
        # Load the VGG model only once when the server starts
        # Check TensorFlow version

        model = load_model('AgeEstimationModel/Models/AgeEstimation_Model_Best.h5')
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Error loading the model: {e}")


# Load the model when the server starts
load_custom_model()

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
                image = np.array(image)
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

                if len(faces) > 0:
                    # Assuming only one face is detected, crop and resize the image
                    x, y, w, h = faces[0]
                    face_image = image[y:y+h, x:x+w]
                    face_image = cv2.resize(face_image, (224, 224))
                    face_image = preprocess_input(face_image)

                    # Check if the model is loaded successfully
                    if model is not None:
                        # Preprocess the image and make predictions using your VGG model
                        predictions = model.predict(np.expand_dims(face_image, axis=0))
                        
                        # Assuming predictions is a numpy array
                        predicted_class_index = np.argmax(predictions)
                        predicted_class_label = class_labels[predicted_class_index]
                        
                        '''
                        # Display the processed image using matplotlib
                        plt.imshow(cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB))
                        plt.axis('off')
                        plt.show()
                        '''
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
