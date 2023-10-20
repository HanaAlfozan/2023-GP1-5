from django.http import JsonResponse
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.vgg16 import preprocess_input
from PIL import Image
import io
import base64
from django.views.decorators.csrf import csrf_protect
import json

# Define class labels
class_labels = ['0-3', '12+', '17+', '4+', '9+']
# ['Toddler', 'Kid', 'Adult']

model = None

def load_custom_model():
    global model
    try:
        # Load the VGG model only once when the server starts
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
                image = image.resize((224, 224))
                image = np.array(image)
                image = preprocess_input(image)

                # Check if the model is loaded successfully
                if model is not None:
                    # Preprocess the image and make predictions using your VGG model
                    predictions = model.predict(np.expand_dims(image, axis=0))
                    
                    # Assuming predictions is a numpy array
                    predicted_class_index = np.argmax(predictions)
                    predicted_class_label = class_labels[predicted_class_index]
                    
                    # Include the predicted class label in the response
                    result = {'Estimated Age Group is: ': predicted_class_label}
                    return JsonResponse(result)
                else:
                    return JsonResponse({'error': 'Model not loaded'})

            else:
                return JsonResponse({'error': 'Invalid image_data'})
            
        except Exception as e:
            print(f"Error processing the image: {e}")
            return JsonResponse({'error': str(e)})

    return JsonResponse({'error': 'Invalid request method'})
