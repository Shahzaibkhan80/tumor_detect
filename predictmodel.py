import os
import numpy as np
import tensorflow as tf
from PIL import Image

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load models safely using relative paths
stage_model_path = os.path.join(BASE_DIR, 'models', 'modelsarcoma.h5')
modelpredict_path = os.path.join(BASE_DIR, 'models', 'newmodel.h5')
brain_model_path = os.path.join(BASE_DIR, 'models', 'braintumor.h5')

stage_model = tf.keras.models.load_model(stage_model_path)
print("Stage Model loaded successfully")

modelpredict = tf.keras.models.load_model(modelpredict_path)
print("Predict Model loaded successfully")

brain_model = tf.keras.models.load_model(brain_model_path)
print("Brain MRI Model loaded successfully.")
