
from tkinter import Image
import numpy as np
import tensorflow as tf
from PIL import Image


def predict_tumor(image_path):
    """Predict tumor status using the primary model."""
    try:
        image = Image.open(image_path).convert('RGB')
        image = image.resize((150, 150))
        image_array = np.array(image) / 255.0
        image_array = np.expand_dims(image_array, axis=0)

        prediction = modelpredict.predict(image_array)
        if prediction.shape[-1] == 2:
            class_index = np.argmax(prediction[0])
            confidence = prediction[0][class_index] * 100

            result = "Tumor Detected" if confidence >= 70 and class_index == 0 else "Normal"
            return result, confidence
        else:
            return "Error in prediction", 0.0
    except Exception as e:
        print(f"Prediction error: {e}")
        return "Error in prediction", 0.0
    




# Load your CNN models
modelpredict = tf.keras.models.load_model('E:\\FYP\\new_Project\\newmodel.h5')
print("Model Predict loaded successfully ")




# Load the model (make sure to provide the correct path)
brain_model = tf.keras.models.load_model("E:/FYP/new_Project/braintumor.h5")
print("Brain MRI Model loaded successfully.")

# Define class labels
brain_class_labels = ['Glioma', 'Meningioma', 'No Tumor', 'Pituitary']

def predict_brain_tumor(image_path):
    try:
        # Load and preprocess image
        image = Image.open(image_path).convert('RGB')  # Open the image
        image = image.resize((150, 150))  # Resize to match model input
        image_array = np.array(image) / 255.0  # Normalize image
        image_array = np.expand_dims(image_array, axis=0)  # Add batch dimension

        # Make prediction
        prediction = brain_model.predict(image_array)
        class_index = np.argmax(prediction[0])  # Get the class with highest probability
        confidence = prediction[0][class_index] * 100  # Get confidence percentage
        label = brain_class_labels[class_index]  # Get the class label

        return label, confidence

    except Exception as e:
        print(f"Prediction error: {e}")
        return "Error in prediction", 0.0

 

