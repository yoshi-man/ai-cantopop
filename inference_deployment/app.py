


import tensorflow as tf
from tensorflow.keras.layers.experimental import preprocessing
import numpy as np
import os


from flask import Flask
from flask import request, jsonify

from flask_cors import CORS, cross_origin



app = Flask(__name__)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

def read_data(path):
    text = open(path, 'rb').read().decode(encoding='utf-8')
    return text

# Get the set of characters within the text, which would eventaully be indexed
def get_vocab(text):
    vocab = sorted(set(text))
    return vocab


# Simple function that takes the list of chars and join them into 1 string
def text_from_ids(ids):
    return tf.strings.reduce_join(chars_from_ids(ids), axis=-1)



# In[28]:


# Initialize our data
text = read_data('./reduced_text.txt')
vocab = get_vocab(text)


# Converters between the "ids" and "characters", which tokenizes each character based on our vocab pool
# Invert just means it the function is to recover our original vocab character based on id
ids_from_chars = preprocessing.StringLookup(vocabulary=list(vocab))
chars_from_ids = preprocessing.StringLookup(vocabulary=ids_from_chars.get_vocabulary(), invert=True)

# Average characters per line is 6, usual patterns in chinese songs come in stanzas of 4 lines
# So we would use information rougly from the previous 3 lines to determine what to write
seq_length = 24

# The embedding dimension, this was up-ed as there are way more characters in the chinese language,
# each being much more information dense
embedding_dim = 1024

# Number of RNN units, here we'll use LSTM
rnn_units = 1024


# In[29]:


class LyricsGenerationModel(tf.keras.Model):
    def __init__(self, vocab_size, embedding_dim, rnn_units):
        super().__init__(self)
        self.embedding = tf.keras.layers.Embedding(vocab_size, embedding_dim)
        self.gru = tf.keras.layers.GRU(rnn_units,
                                    return_sequences=True,
                                    return_state=True)
        self.dense = tf.keras.layers.Dense(vocab_size)

    def call(self, inputs, states=None, return_state=False, training=False):
        x = inputs
        x = self.embedding(x, training=training)
        if states is None:
            states = self.gru.get_initial_state(x)
            
        x, states = self.gru(x, initial_state=states, training=training)
        x = self.dense(x, training=training)

        if return_state:
            return x, states
        else:
            return x
        
model = LyricsGenerationModel(
    # Be sure the vocabulary size matches the `StringLookup` layers.
    vocab_size=len(ids_from_chars.get_vocabulary()),
    embedding_dim=embedding_dim,
    rnn_units=rnn_units)

model.build(input_shape=(seq_length, len(ids_from_chars.get_vocabulary())))



# In[5]:


model.load_weights('./model_weights.h5')


# In[6]:


class OneStep(tf.keras.Model):
    def __init__(self, model, chars_from_ids, ids_from_chars, temperature=1.0):
        super().__init__()
        self.temperature = temperature
        self.model = model
        self.chars_from_ids = chars_from_ids
        self.ids_from_chars = ids_from_chars

        # Create a mask to prevent "[UNK]" from being generated.
        skip_ids = self.ids_from_chars(['[UNK]'])[:, None]
        sparse_mask = tf.SparseTensor(
            # Put a -inf at each bad index.
            values=[-float('inf')]*len(skip_ids),
            indices=skip_ids,
            # Match the shape to the vocabulary
            dense_shape=[len(ids_from_chars.get_vocabulary())])
        self.prediction_mask = tf.sparse.to_dense(sparse_mask)

    @tf.function
    def generate_one_step(self, inputs, states=None):
        # Convert strings to token IDs.
        input_chars = tf.strings.unicode_split(inputs, 'UTF-8')
        input_ids = self.ids_from_chars(input_chars).to_tensor()

        # Run the model.
        # predicted_logits.shape is [batch, char, next_char_logits]
        predicted_logits, states = self.model(inputs=input_ids, states=states,
                                              return_state=True)
        # Only use the last prediction.
        predicted_logits = predicted_logits[:, -1, :]
        predicted_logits = predicted_logits/self.temperature
        # Apply the prediction mask: prevent "[UNK]" from being generated.
        predicted_logits = predicted_logits + self.prediction_mask

        # Sample the output logits to generate token IDs.
        predicted_ids = tf.random.categorical(predicted_logits, num_samples=1)
        predicted_ids = tf.squeeze(predicted_ids, axis=-1)

        # Convert from token ids to characters
        predicted_chars = self.chars_from_ids(predicted_ids)

        # Return the characters and model state.
        return predicted_chars, states

# In[7]:


def generate_lyrics(seed_sentence, length):

    if len(seed_sentence) == 0:
        return 'No seed sentence provided'

    if len(seed_sentence) > 12:
        seed_sentence = seed_sentence[:12]

    if length < 12:
        length = 12

    if length > 720:
        length = 720


    one_step_model = OneStep(model, chars_from_ids, ids_from_chars)

    try:
        states = None
        next_char = tf.constant([seed_sentence])
        result = [next_char]

        for n in range(length):
            next_char, states = one_step_model.generate_one_step(next_char, states=states)
            result.append(next_char)

        result = tf.strings.join(result)

        return result[0].numpy().decode('utf-8')

    except Exception as err_message:
        return "Error generating lyrics: " + err_message


# In[25]:



# In[ ]:

@app.route("/")
@cross_origin()
def hello():

	results = {}

	results['STATUS'] = 200

	results['BODY'] = 'Why hello there'
	
	return jsonify(results)



@app.route("/seed=<sentence>&length=<length>", methods=['GET'])
@cross_origin()
def get_lyrics(sentence, length):

    try:
        results = {}
        results['STATUS'] = 200
        results['BODY'] = generate_lyrics(str(sentence), int(length))
        return jsonify(results)

    except Exception as error_message:
        results = {}
        results['STATUS'] = 400
        results['BODY'] = 'Error getting lyrics: ' + error_message
        return jsonify(results)


