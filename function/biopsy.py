from model_loader import stage_model
import numpy as np
from PIL import Image

def predict_biopsy(image_path):
    try:
        image = Image.open(image_path).convert('RGB')
        image = image.resize((150, 150))
        image_array = np.array(image) / 255.0
        image_array = np.expand_dims(image_array, axis=0)

        prediction = stage_model.predict(image_array)
        class_index = np.argmax(prediction[0])
        confidence = prediction[0][class_index] * 100

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