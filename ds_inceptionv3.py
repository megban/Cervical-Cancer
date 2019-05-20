# -*- coding: utf-8 -*-
"""DS_INCEPTIONV3.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/16M-ZkB3fRoytMGZpE5XJ1l_Bb6lJTDjD
"""

from google.colab import drive
drive.mount('/content/gdrive')
#4/TwFbyEdEj30EgQsCQNwt9kaRBvJuXHvNcVxozNnxZWS8qOFORLhOoIY

!pip install Pillow==4.0.0
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
# import matplotlib.pyplot as plt
# import matplotlib.image as mpimg
# from tensorflow.keras import layers
# from tensorflow.keras import Model
# import os, tensorflow as tf
# import pprint
# from tensorflow.keras.preprocessing.image import ImageDataGenerator
# from tensorflow.keras.optimizers import RMSprop
# import keras
# import numpy as np
# from keras.applications import vgg16, inception_v3, resnet50, mobilenet
# !pip install h5py pyyaml
# !pip install tf_nightly

from tensorflow.keras.preprocessing.image import ImageDataGenerator

train_datagen = ImageDataGenerator(
    rescale = 1./255,
    rotation_range = 40,
    width_shift_range = 0.2,
    height_shift_range = 0.2,
    shear_range = 0.2,
    zoom_range = 0.2,
    horizontal_flip = True)

# Note that the validation data should not be augmented!
test_datagen = ImageDataGenerator(rescale = 1./255)

# Flow training images in batches of 32 using train_datagen generator
train_generator = train_datagen.flow_from_directory(
        "/content/gdrive/My Drive/cervical_cancer_data/train",  # This is the source directory for training images
        target_size = (150, 150),  # All images will be resized to 150x150
        batch_size = 64,
        # Since we use binary_crossentropy loss, we need binary labels
        class_mode = 'categorical')

# Flow validation images in batches of 32 using test_datagen generator
validation_generator = test_datagen.flow_from_directory(
        "/content/gdrive/My Drive/cervical_cancer_data/val",
        target_size = (150, 150),
        batch_size = 64,
        class_mode = 'categorical')

from tensorflow.keras import layers
from tensorflow.keras import Model, Input
import tensorflow as tf
# img_input = layers.Input(shape=(150,150,3))
# #print(shape=(150,150,3))
# x = tf.keras.layers.Conv2D(4, 3, activation='relu')(img_input)
# x = tf.keras.layers.MaxPooling2D(2)(x)
# x = tf.keras.layers.Conv2D(5, 3, activation='relu')(x)
# x = tf.keras.layers.MaxPooling2D(2)(x)
# x = tf.keras.layers.Conv2D(10, 3, activation='relu')(x)
# x = tf.keras.layers.MaxPooling2D(2)(x)
# x = tf.keras.layers.Flatten()(x)
# x = tf.keras.layers.Dense(20, activation='relu')(x)
# output = tf.keras.layers.Dense(3, activation='softmax')(x)
# simple_model = tf.keras.Model(img_input, output)
# # simple_model.compile(loss = 'categorical_crossentropy',
# #               optimizer = tf.train.RMSPropOptimizer(0.001),
# #               metrics = ['acc'])
# simple_model.summary

# # Our input feature map is 150x150x3: 150x150 for the image pixels, and 3 for
# # the three color channels: R, G, and B
# img_input = layers.Input(shape=(150, 150, 3))

# # First convolution extracts 4 filters that are 3x3
# # Convolution is followed by max-pooling layer with a 2x2 window
# x = layers.Conv2D(4, 3, activation='relu')(img_input)
# x = layers.MaxPooling2D(2)(x)

# # Second convolution extracts 5 filters that are 3x3
# # Convolution is followed by max-pooling layer with a 2x2 window
# x = layers.Conv2D(5, 3, activation='relu')(x)
# x = layers.MaxPooling2D(2)(x)

# # Third convolution extracts 10 filters that are 3x3
# # Convolution is followed by max-pooling layer with a 2x2 window
# x = layers.Conv2D(10, 3, activation='relu')(x)
# x = layers.MaxPooling2D(2)(x)

# # Flatten feature map to a 1-dim tensor so we can add fully connected layers
# x = layers.Flatten()(x)

# # Create a fully connected layer with ReLU activation and 20 hidden units
# x = layers.Dense(20, activation='relu')(x)

# # Create output layer with a single node and sigmoid activation
# output = layers.Dense(1, activation='sigmoid')(x)

# # Create model:
# # input = input feature map
# # output = input feature map + stacked convolution/maxpooling layers + fully 
# # connected layer + sigmoid output layer
# model = Model(img_input, output)
# model.summary()

from tensorflow.keras.applications import vgg16, inception_v3, resnet50, mobilenet
#input_tensor = Input(shape=(150, 150, 3))  # this assumes K.image_data_format() == 'channels_last'

#model = InceptionV3(input_tensor=input_tensor, weights='imagenet', include_top=True)
base_model = inception_v3.InceptionV3(include_top=True, weights=None, input_tensor=None, input_shape=(150,150,3), pooling=None, classes=3)
#model = Model(inputs=base_model.input, outputs=base_model.output)
x = base_model.output

model = Model(inputs = base_model.input, outputs = x)
model.summary()

import os
tpu_model = tf.contrib.tpu.keras_to_tpu_model(
    model,
    strategy=tf.contrib.tpu.TPUDistributionStrategy(
        tf.contrib.cluster_resolver.TPUClusterResolver(tpu='grpc://' + os.environ['COLAB_TPU_ADDR'])
    )
)
tpu_model.compile(
    optimizer=tf.train.AdamOptimizer(learning_rate=1e-3, ),
    loss=tf.keras.losses.categorical_crossentropy,
    metrics=['categorical_accuracy']
)

history = tpu_model.fit_generator(
      train_generator,
      steps_per_epoch = 100,  # 2000 images = batch_size * steps
      epochs = 15,
      validation_data = validation_generator,
      validation_steps = 50,  # 1000 images = batch_size * steps
      verbose = 2)

tpu_model.save('Inception.h5')

import matplotlib.pyplot as plt
print(history.history.keys())
acc = history.history['categorical_accuracy']
val_acc = history.history['val_categorical_accuracy']

# Retrieve a list of list results on training and test data
# sets for each training epoch
loss = history.history['loss']
val_loss = history.history['val_loss']

# Get number of epochs
epochs = range(len(acc))

# Plot training and validation accuracy per epoch
plt.plot(epochs, acc)
plt.plot(epochs, val_acc)
plt.title('Training and validation accuracy')

plt.figure()

# Plot training and validation loss per epoch
plt.plot(epochs, loss)
plt.plot(epochs, val_loss)
plt.title('Training and validation loss')