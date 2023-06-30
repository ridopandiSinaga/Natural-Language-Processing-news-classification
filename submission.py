# -*- coding: utf-8 -*-
"""submission.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1mz8UGi6F1cCsyqoz2LAPfl_q-cPfr2Td

---
---





# Membuat Model NLP dengan TensorFlow

---

---

# Data Diri

Nama: Ridopandi Sinaga

E-mail: ridosinaga037@gmail.com

---
"""

!wget --no-check-certificate \
  https://storage.googleapis.com/dataset-uploader/bbc/bbc-text.csv \
  -O /tmp/bbc-text.csv

import pandas as pd
df = pd.read_csv('/tmp/bbc-text.csv')
df.info()
df

# Label Data Distribution/Proportion Graph
import seaborn as sns
import matplotlib.pyplot as plt

count = df['category'].value_counts()
sns.catplot(x='category', kind='count', data=df)
plt.title('Label Data Distribution')
plt.xlabel('category')
plt.ylabel('Count')
plt.show()

# Change the label into individual categories
# One hot encoding
category_ = pd.get_dummies(df['category'])
df_new   = pd.concat([df, category_], axis=1)
df_new   = df_new.drop(['category'], axis=1)
df_new

# Lower case, and delete whitespace
import string
df_new['text'] = df_new['text'].str.lower().str.strip()

# Delete punctuation (tanda baca)
def removePunctuation(text):
    for punct in string.punctuation:
        text = text.replace(punct, ' ')
    return text

df_new['text'] = df_new['text'].apply(removePunctuation)

# Delete stopwords
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords

stop = stopwords.words('english')

df_new['text'] = df_new['text'].apply(lambda x: ' '.join([
    word for word in x.split() if word not in (stop)
]))

# Seperate text and label values respectively in dataframe into numpy data type
tweet = df_new['text'].values
label = df_new[['business', 'entertainment', 'politics', 'sport', 'tech']].values

# Train and test data split
from sklearn.model_selection import train_test_split

descTrain, descTest, labelTrain, labelTest = train_test_split(tweet, label, test_size=0.2, random_state=1)

print(f'Train : {descTrain.shape} {labelTrain.shape}')
print(f'Test  : {descTest.shape} {labelTest.shape}')

# Tokenizer sequence and padding
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

tokenizer = Tokenizer(num_words=5000, oov_token='x')
tokenizer.fit_on_texts(descTrain)
tokenizer.fit_on_texts(descTest)

sequenceTrain = tokenizer.texts_to_sequences(descTrain)
sequenceTest  = tokenizer.texts_to_sequences(descTest)

paddedTrain = pad_sequences(sequenceTrain, maxlen=100)
paddedTest  = pad_sequences(sequenceTest,  maxlen=100)

len(tokenizer.word_index)

# Model architecture
import tensorflow as tf

model = tf.keras.Sequential([
    tf.keras.layers.Embedding(input_dim=5000, output_dim=16, input_length=100),
    tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(128, return_sequences=True)),
    tf.keras.layers.GlobalMaxPool1D(),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.Dropout(0.25),
    tf.keras.layers.Dense(5, activation='softmax')
])

model.compile(
    optimizer = 'adam',
    loss      = 'categorical_crossentropy',
    metrics   = ['accuracy']
)

model.summary()

#Callback
class stopCallback(tf.keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs={}):
        if (logs.get('accuracy') > 0.9 and logs.get('val_accuracy') > 0.9):
            print('\naccuracy and val_accuracy reach > 90%')
            self.model.stop_training = True

stopTraining = stopCallback()

reduceLROP   = tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.1, patience=2)

#train model
epoch = 30

history = model.fit(
    paddedTrain,
    labelTrain,
    batch_size      = 128,
    epochs          = epoch,
    steps_per_epoch = 10,
    validation_data = (paddedTest, labelTest),
    verbose         = 2,
    callbacks       = [reduceLROP]
)

accuracy     = history.history['accuracy']
val_accuracy = history.history['val_accuracy']

loss         = history.history['loss']
val_loss     = history.history['val_loss']

epoch_range  = range(epoch)

plt.figure(figsize = (12, 4))
plt.subplot(1, 2, 1)
plt.plot(epoch_range, accuracy,     label='Training Accuracy')
plt.plot(epoch_range, val_accuracy, label='Validation Accuracy')
plt.title('Training and Validation Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend(loc='lower right')

plt.subplot(1, 2, 2)
plt.plot(epoch_range, loss,     label='Training Loss')
plt.plot(epoch_range, val_loss, label='Validation Loss')
plt.title('Training and Validation Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend(loc='upper right')

plt.show()

loss, accuracy = model.evaluate(paddedTest, labelTest)
print('Accuracy:', accuracy)