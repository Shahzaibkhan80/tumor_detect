import numpy as np
import tensorflow as tf
from PIL import Image

# Load the model once globally
stage_model = tf.keras.models.load_model('E:\\FYP\\new_Project\\modelsarcoma.h5')
print("Stage Model loaded successfully")

def predict_biopsy(image_path):
    """
    Predict tumor status (Benign/Malignant) using the biopsy model.
    
    Args:
        image_path (str): Path to the biopsy image.

    Returns:
        str: Prediction result ("Malignant", "Benign", or error message)
    """
    try:
        # Load and preprocess image
        image = Image.open(image_path).convert('RGB')
        image = image.resize((150, 150))  # Ensure size matches model input
        image_array = np.array(image) / 255.0  # Normalize
        image_array = np.expand_dims(image_array, axis=0)  # Add batch dimension

        # Predict
        prediction = stage_model.predict(image_array)
        class_index = np.argmax(prediction[0])
        confidence = prediction[0][class_index] * 100

        # Assuming binary classification (Benign vs Malignant)
        if prediction.shape[-1] == 2:
            if class_index == 1 and confidence >= 70:
                return "Malignant"
            else:
                return "Benign"
        else:
            return "Error: Unexpected output shape from model"

    except Exception as e:
        print(f"Error during biopsy prediction: {e}")
        return "Error in biopsy prediction"
