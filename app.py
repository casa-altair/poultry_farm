import os
import numpy as np
import scipy
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout

IMAGE_WIDTH, IMAGE_HEIGHT = 150, 150
BATCH_SIZE = 32
EPOCHS = 10
NUM_CLASSES = 2  # Assuming 3 classes of diseases
BATCH_SIZE = 7

class_names = ['healthy', 'diseased']
# Define paths to your dataset
train_dir = 'train_dir'
validation_dir = 'validation_dir'
# test_image_path = '/Users/osm/Desktop/smart_poultry/unhealthy.jpg'
test_image_path = 'train_dir/healthy/image_1.jpg'


# Data preprocessing and augmentation
train_datagen = ImageDataGenerator(rescale=1./255, shear_range=0.2, zoom_range=0.2, horizontal_flip=True)
train_generator = train_datagen.flow_from_directory(train_dir, target_size=(IMAGE_WIDTH, IMAGE_HEIGHT), batch_size=BATCH_SIZE, class_mode='categorical')

validation_datagen = ImageDataGenerator(rescale=1./255)
validation_generator = validation_datagen.flow_from_directory(validation_dir, target_size=(IMAGE_WIDTH, IMAGE_HEIGHT), batch_size=BATCH_SIZE, class_mode='categorical')
print(validation_generator.samples)

# Build the CNN model
model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(IMAGE_WIDTH, IMAGE_HEIGHT, 3)),
    MaxPooling2D(2, 2),
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D(2, 2),
    Conv2D(128, (3, 3), activation='relu'),
    MaxPooling2D(2, 2),
    Conv2D(128, (3, 3), activation='relu'),
    MaxPooling2D(2, 2),
    Flatten(),
    Dropout(0.5),
    Dense(512, activation='relu'),
    Dense(NUM_CLASSES, activation='softmax')
])

# Compile the model
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Train the model
print("Number of training samples:", train_generator.samples)
print("Batch size:", BATCH_SIZE)
steps_per_epoch = train_generator.samples // BATCH_SIZE
print("Steps per epoch:", steps_per_epoch)

# If steps_per_epoch is zero, consider adjusting the batch size or checking your dataset
if steps_per_epoch == 0:
    print("WARNING: steps_per_epoch is zero. Please check your dataset or adjust the batch size.")
else:
    # Fit the model
    history = model.fit(train_generator, steps_per_epoch=steps_per_epoch, epochs=EPOCHS,
                        validation_data=validation_generator, validation_steps=validation_generator.samples // BATCH_SIZE)
# history = model.fit(train_generator, steps_per_epoch=train_generator.samples//BATCH_SIZE, epochs=EPOCHS, validation_data=validation_generator, validation_steps=validation_generator.samples//BATCH_SIZE)

# Save the trained model
model.save('chicken_disease_prediction_model.keras')

# Evaluate the model
loss, accuracy = model.evaluate(validation_generator, steps=validation_generator.samples//BATCH_SIZE)
print(f'Validation Accuracy: {accuracy * 100:.2f}%')

# Make predictions
# Assuming you have a single test image 'test_image.jpg'
test_image = tf.keras.preprocessing.image.load_img(test_image_path, target_size=(IMAGE_WIDTH, IMAGE_HEIGHT))
test_image = tf.keras.preprocessing.image.img_to_array(test_image)
test_image = np.expand_dims(test_image, axis=0)
test_image /= 255.0  # Normalize the image

predictions = model.predict(test_image)
predicted_class = np.argmax(predictions)
predicted_class_data = class_names[predicted_class]
print(f'Predicted class: {predicted_class_data}')
