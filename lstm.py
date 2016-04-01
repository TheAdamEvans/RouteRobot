import numpy as np
import pandas as pd
from keras.models import Sequential
from keras.layers import LSTM, Dense, Activation
from keras.optimizers import Adagrad

# params
hidden1_size = 128
seq_len = 25
nb_epoch = 50

# get just the route names -- will need to clean this data further
# to remove space characters
df = pd.read_csv('route_name.txt', header=None).loc[:, 1]
df = df.dropna()
# vocabulary
text = ''.join(list(df.values))
chars = set(text)
print 'vocab:', chars
char_to_idx = dict((c, i) for i, c in enumerate(chars))
idx_to_char = dict((i, c) for i, c in enumerate(chars))

# vectorize data by chunking into overlapping sequences of equal length
# there is a way to use variable-length seqs with rnns, so we could use the individual names
maxlen = 20
step = 3
seqs = []
next_chars = []
for i in range(0, len(text) - maxlen, step):
    seqs.append(text[i: i + maxlen])
    next_chars.append(text[i + maxlen])
X = np.zeros((len(seqs), seq_len, len(chars)), dtype=np.bool)
y = np.zeros((len(seqs), len(chars)), dtype=np.bool)
for i, sentence in enumerate(seqs):
    for t, char in enumerate(sentence):
        X[i, t, char_to_idx[char]] = 1
    y[i, char_to_idx[next_chars[i]]] = 1

# model def -- single hidden layer for now
model = Sequential()
model.add(LSTM(hidden1_size, return_sequences=False,  input_shape=(seq_len, len(chars))))
model.add(Dense(len(chars)))
model.add(Activation('softmax'))
opt = Adagrad()
model.compile(loss='categorical_crossentropy', optimizer=opt)

# can sample from model in this loop
p = 0
for epoch in range(nb_epoch):
    print
    print '-' * 50
    print 'Epoch ' + str(epoch)
    model_hist = model.fit(X, y, nb_epoch=1)

