import tensorflow as tf
from tensorflow import keras
from keras import layers

# Load and prepare the MNIST dataset
print("Loading MNIST data...")
(train_images, train_labels), (test_images, test_labels) = keras.datasets.mnist.load_data()

# Normalize the pixel values
train_images = train_images.astype("float32") / 255.0
test_images = test_images.astype("float32") / 255.0

# Reshape to include channel dimension
train_images = train_images.reshape((-1, 28, 28, 1))
test_images = test_images.reshape((-1, 28, 28, 1))

print(f"Training data shape: {train_images.shape}")
print(f"Test data shape: {test_images.shape}")

# Build the LeNet like model using Keras
cnn_model = keras.Sequential([
    layers.Input(shape=(28, 28, 1)),
    layers.Conv2D(filters=6, kernel_size=(5, 5), padding='same', activation='relu'),
    layers.AveragePooling2D(pool_size=(2, 2)),

    layers.Conv2D(filters=16, kernel_size=(5, 5), padding='same', activation='relu'),
    layers.AveragePooling2D(pool_size=(2, 2)),

    layers.Flatten(),
    layers.Dense(120, activation='relu'),
    layers.Dense(84, activation='relu'),
    layers.Dense(10, activation='softmax')
])

# Compile the model
cnn_model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])

print("Starting training process...")
cnn_model.fit(train_images, train_labels, epochs=10, batch_size=128, validation_split=0.2)
print("Training completed.")

# Evaluate the model
print("Running evaluation on test set...")
loss, accuracy = cnn_model.evaluate(test_images, test_labels)
print(f"Test Accuracy: {accuracy:.4f}")
