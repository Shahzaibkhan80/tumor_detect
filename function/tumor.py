from model_loader import modelpredict, stage_model, brain_model, brain_class_labels
import numpy as np
import tensorflow as tf
from PIL import Image

def predict_tumor(image_path):
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

def predict_brain_tumor(image_path):
    try:
        image = Image.open(image_path).convert('RGB')
        image = image.resize((150, 150))
        image_array = np.array(image) / 255.0
        image_array = np.expand_dims(image_array, axis=0)

        prediction = brain_model.predict(image_array)
        class_index = np.argmax(prediction[0])
        confidence = prediction[0][class_index] * 100
        label = brain_class_labels[class_index]

        return label, confidence
    except Exception as e:
        print(f"Prediction error: {e}")
        return "Error in prediction", 0.0