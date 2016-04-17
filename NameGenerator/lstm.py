from __future__ import print_function

import re
import sys
import random
import numpy as np
import pandas as pd
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
from keras.optimizers import RMSprop

# starting params
hidden1_size = 32
seq_len = 5
nb_epoch = 25

# get just the route names
df = pd.read_csv('summary_data.csv')

# basic cleaning to validate this works. english + select chars only, lowercase, single space
names = df['name'][df['is_route']].dropna().values
names = [name for name in names if re.search('^[A-Za-z0-9 !@#$%^&*_-]*$', name)]
names = [name.lower() for name in names]
names = [' '.join(name.split()) for name in names]
names = list(set(names))
text = '\n'.join(names)

# vocabulary
chars = set(text)
print('vocab:', chars)
char_to_idx = dict((c, i) for i, c in enumerate(chars))
idx_to_char = dict((i, c) for i, c in enumerate(chars))

# vectorize data
step = 3
seqs = []
next_chars = []
for i in range(0, len(text) - seq_len, step):
    seqs.append(text[i: i + seq_len])
    next_chars.append(text[i + seq_len])
X = np.zeros((len(seqs), seq_len, len(chars)), dtype=np.bool)
y = np.zeros((len(seqs), len(chars)), dtype=np.bool)
for i, seq in enumerate(seqs):
    for t, char in enumerate(seq):
        X[i, t, char_to_idx[char]] = 1
    y[i, char_to_idx[next_chars[i]]] = 1


# model def -- single hidden layer with heavy regularization
model = Sequential()
model.add(LSTM(hidden1_size, input_shape=(seq_len, len(chars)), dropout_U=0.2, dropout_W=0.2))
model.add(Dropout(0.2))
model.add(Dense(len(chars), activation='softmax'))
opt = RMSprop()
model.compile(loss='categorical_crossentropy', optimizer=opt)


def sample(a, temperature=1.0):
    # helper function to sample an index from a probability array
    a = np.log(a) / temperature
    a = np.exp(a) / np.sum(np.exp(a))
    return np.argmax(np.random.multinomial(1, a, 1))


# can sample from model in this loop
for epoch in range(nb_epoch):
    print()
    print('-' * 50)
    print('Epoch ' + str(epoch))
    model_hist = model.fit(X, y, nb_epoch=1)

    start_index = random.randint(0, len(text) - seq_len - 1)

    for diversity in [0.2, 0.5, 1.0, 1.2]:
        print()
        print('----- diversity:', diversity)

        generated = ''
        sentence = text[start_index: start_index + seq_len]
        generated += sentence
        print('----- Generating with seed: "' + sentence + '"')
        sys.stdout.write(generated)

        for i in range(400):
            x = np.zeros((1, seq_len, len(chars)))
            for t, char in enumerate(sentence):
                x[0, t, char_to_idx[char]] = 1.

            preds = model.predict(x, verbose=0)[0]
            next_index = sample(preds, diversity)
            next_char = idx_to_char[next_index]

            generated += next_char
            sentence = sentence[1:] + next_char

            sys.stdout.write(next_char)
            sys.stdout.flush()
        print()

