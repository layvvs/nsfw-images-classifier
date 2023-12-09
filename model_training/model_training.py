import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import keras
from keras import layers


inputs = keras.Input(shape=(256, 256, 3), name="img")
x = layers.Conv2D(256, 3, activation="relu")(inputs)
x = layers.Conv2D(512, 3, activation="relu")(x)
block_1_output = layers.MaxPooling2D(3)(x)

x = layers.Conv2D(256, 3, activation="relu", padding="same")(block_1_output)
x = layers.Conv2D(256, 3, activation="relu", padding="same")(x)
block_2_output = layers.add([x, block_1_output])

x = layers.Conv2D(256, 3, activation="relu", padding="same")(block_2_output)
x = layers.Conv2D(256, 3, activation="relu", padding="same")(x)
block_3_output = layers.add([x, block_2_output])

x = layers.Conv2D(256, 3, activation="relu")(block_3_output)
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dense(512, activation="relu")(x)
x = layers.Dropout(0.5)(x)
outputs = layers.Dense(10, activation='softmax')(x)

model = keras.Model(inputs, outputs, name="nsfw-classifier")

model.compile(optimizer='adam',
             loss='categorical_crossentropy',
             metrics=['accuracy'])

