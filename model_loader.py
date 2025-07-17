# model_loader.py
import os
import tensorflow as tf

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# Load models using safe relative paths
try:
    stage_model = tf.keras.models.load_model(os.path.join(BASE_DIR, 'models', 'modelsarcoma.h5'))
    print("Stage Model loaded successfully")
except Exception as e:
    print("Stage Model loading failed:", e)

try:
    modelpredict = tf.keras.models.load_model(os.path.join(BASE_DIR, 'models', 'newmodel.h5'))
    print("Predict Model loaded successfully")
except Exception as e:
    print("Predict Model loading failed:", e)

try:
    brain_model = tf.keras.models.load_model(os.path.join(BASE_DIR, 'models', 'braintumor.h5'))
    print("Brain MRI Model loaded successfully")
except Exception as e:
    print("Brain MRI Model loading failed:", e)

# Labels
brain_class_labels = ['Glioma', 'Meningioma', 'No Tumor', 'Pituitary']
