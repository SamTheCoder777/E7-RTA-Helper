import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, MultiLabelBinarizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Embedding, Dense, Masking, Concatenate, Input, Lambda
import tensorflow as tf
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
from tensorflow.keras import activations, initializers, regularizers
from tensorflow.keras.layers import LSTM, Dropout
from tensorflow.keras import backend as K
from tensorflow.keras.regularizers import l2
from attention import Attention
import ast
import pickle
from tensorflow_model_optimization.python.core.keras.compat import keras

import os
os.environ['TF_XLA_FLAGS'] = '--tf_xla_cpu_global_jit'

tf.config.optimizer.set_jit(True)  # Enable XLA

# Load data
data = pd.read_csv('data/epic7_match_history.csv')
hero_details = pd.read_csv('data/hero_types.csv')

data = data.merge(hero_details, left_on='Hero', right_on='code', how='left')

# Add a 'First_Pick_Win' feature
data['First_Pick_Win'] = (data['First Pick'] == 1) & (data['Match Result'] == 'Win')
# Encode the 'First_Pick_Win' and 'First_Pick_Loss' as binary features
data['First_Pick_Win_encoded'] = data['First_Pick_Win'].astype(int)

# Encode heroes and teams as integers
hero_encoder = LabelEncoder()
hero_encoder.fit(list(data['Hero'].unique())+['unknown'])
data['Hero_encoded'] = hero_encoder.transform(data['Hero'])

team_encoder = LabelEncoder()
data['Team_encoded'] = team_encoder.fit_transform(data['Team'])

# Function to check for problematic entries
def ensure_list(x):
    if pd.isna(x):
        return False  # Mark as problematic
    return True

# Apply the function to identify rows with issues
data['is_valid'] = data['type'].apply(ensure_list)

# Identify the Match Numbers with any invalid rows
invalid_matches = data.loc[~data['is_valid'], 'Match Number'].unique()
print(f'Invalid Matches: {invalid_matches}')

# Identify the Match Numbers with any invalid rows
invalid_matches = data.loc[~data['is_valid'], 'Match Number'].unique()

# Drop all rows with those Match Numbers
data = data[~data['Match Number'].isin(invalid_matches)].drop(columns=['is_valid'])


def safe_literal_eval(val):
    try:
        return ast.literal_eval(val)
    except (ValueError, SyntaxError):
        print(f"Error with value: {val}")
        return val  # Return the original value if it fails

# Convert the 'type' column from string to list
data['type'] = data['type'].apply(safe_literal_eval)

# Encode types as multi-hot vectors
type_encoder = MultiLabelBinarizer()
unique_types = np.unique(data['type'])

type_encoder.fit(list(unique_types)+['Unknown'])
data['Type_encoded'] = list(type_encoder.transform(data['type']))

# Encode first pick
first_pick_encoder = LabelEncoder()
data['First_Pick_encoded'] = first_pick_encoder.fit_transform(data['First Pick'])

# Prepare sequences and labels
sequences = []
labels = []
pick_orders = []
team_sequences = []
type_sequences = []
first_pick_sequences = []
first_pick_win_sequences = []

for match_number in data['Match Number'].unique():
    match_df = data[data['Match Number'] == match_number]
    
    picks_sequence = match_df.sort_values(by='Pick Order')['Hero_encoded'].tolist()
    pick_order_sequence = match_df.sort_values(by='Pick Order')['Pick Order'].tolist()
    team_sequence = match_df.sort_values(by='Pick Order')['Team_encoded'].tolist()
    type_sequence = match_df.sort_values(by='Pick Order')['Type_encoded'].tolist()
    first_pick_sequence = match_df.sort_values(by='Pick Order')['First_Pick_encoded'].tolist()
    first_pick_win_sequence = match_df.sort_values(by='Pick Order')['First_Pick_Win_encoded'].tolist()

    for i in range(1, len(picks_sequence)):
        sequences.append(picks_sequence[:i])
        labels.append(picks_sequence[i])
        pick_orders.append(pick_order_sequence[:i])
        team_sequences.append(team_sequence[:i])
        type_sequences.append(type_sequence[:i])
        first_pick_sequences.append(first_pick_sequence[:i])
        first_pick_win_sequences.append(first_pick_win_sequence[:i])

unique_type_values = np.unique(np.concatenate(type_sequences))
print("Unique values in type_sequences before padding:", unique_type_values)

# Pad sequences
max_sequence_length = max(len(seq) for seq in sequences)
print(f"Max sequence length: {max_sequence_length}")
X_heroes = pad_sequences(sequences, maxlen=max_sequence_length, padding='pre')
X_pick_orders = pad_sequences(pick_orders, maxlen=max_sequence_length, padding='pre')
X_teams = pad_sequences(team_sequences, maxlen=max_sequence_length, padding='pre')
X_first_picks = pad_sequences(first_pick_sequences, maxlen=max_sequence_length, padding='pre')
# Convert lists to numpy arrays and pad sequences
X_first_pick_wins = pad_sequences(first_pick_win_sequences, maxlen=max_sequence_length, padding='pre')

# Pad type sequences differently because each entry is a list of multi-hot vectors
#X_types = pad_sequences(type_sequences, maxlen=max_sequence_length, padding='pre', dtype=object, value=[0]*len(type_encoder.classes_))
# Convert lists of multi-hot vectors to numpy array
#X_types = np.array([np.stack(x) for x in X_types], dtype=np.float32)

# Convert lists of multi-hot vectors to numpy array
X_types = pad_sequences([np.array(x) for x in type_sequences], maxlen=max_sequence_length, padding='pre', dtype='float32')

y = to_categorical(labels, num_classes=len(hero_encoder.classes_))
y_win = np.array([sequence[0] for sequence in first_pick_win_sequences])

# Parameters
num_heroes = len(hero_encoder.classes_)
num_types = len(type_encoder.classes_)
embedding_dim = 512  # Experiment with 128, 256, 512
lstm_units = 256  # Reduced to match the subsequent attention mechanism

# Preprocessing Step: Clip values to ensure indices are within bounds
X_heroes = np.clip(X_heroes, 0, num_heroes - 1)
X_pick_orders = np.clip(X_pick_orders, 0, max_sequence_length - 1)
X_teams = np.clip(X_teams, 0, len(team_encoder.classes_) - 1)
X_first_picks = np.clip(X_first_picks, 0, len(first_pick_encoder.classes_) - 1)
X_first_pick_wins = np.clip(X_first_pick_wins, 0, max_sequence_length - 1)

# Build the model
input_heroes = Input(shape=(max_sequence_length,))
input_pick_orders = Input(shape=(max_sequence_length,))
input_teams = Input(shape=(max_sequence_length,))
input_types = Input(shape=(max_sequence_length, num_types))
input_first_picks = Input(shape=(max_sequence_length,))
# Define input layers
input_first_pick_wins = Input(shape=(max_sequence_length,))

hero_embedding = Embedding(input_dim=num_heroes, output_dim=embedding_dim, input_length=max_sequence_length)(input_heroes)
masking_heroes = Masking(mask_value=0.0)(hero_embedding)

pick_order_embedding = Embedding(input_dim=max_sequence_length, output_dim=embedding_dim, input_length=max_sequence_length)(input_pick_orders)
masking_orders = Masking(mask_value=0.0)(pick_order_embedding)

team_embedding = Embedding(input_dim=len(team_encoder.classes_), output_dim=embedding_dim, input_length=max_sequence_length)(input_teams)
masking_teams = Masking(mask_value=0.0)(team_embedding)

first_pick_embedding = Embedding(input_dim=len(first_pick_encoder.classes_), output_dim=embedding_dim, input_length=max_sequence_length)(input_first_picks)
masking_first_picks = Masking(mask_value=0.0)(first_pick_embedding)

# Define embeddings for the new inputs
first_pick_win_embedding = Embedding(input_dim=2, output_dim=embedding_dim, input_length=max_sequence_length)(input_first_pick_wins)
# Apply masking
masking_first_pick_wins = Masking(mask_value=0.0)(first_pick_win_embedding)

# Apply Masking before Dense layer for types
masking_types = Masking(mask_value=0.0)(input_types)
type_embedding = Dense(embedding_dim, activation='relu')(masking_types)
#masking_types = Masking(mask_value=0.0)(type_embedding)

# Concatenate all inputs
concatenated = Concatenate()([masking_heroes, masking_orders, masking_teams, masking_first_picks, type_embedding, masking_first_pick_wins])
concatenated_win = Concatenate()([masking_heroes, masking_orders, masking_teams, masking_first_picks, type_embedding])
def check_indices(data, max_index):
    if np.any(data >= max_index):
        print(f"Error: Found indices out of range in data. Max index allowed: {max_index - 1}")
        return False
    return True

# Check indices for each input array
if not check_indices(X_heroes, num_heroes):
    print("Invalid indices in X_heroes")
if not check_indices(X_pick_orders, max_sequence_length):
    print("Invalid indices in X_pick_orders")
if not check_indices(X_teams, len(team_encoder.classes_)):
    print("Invalid indices in X_teams")
if not check_indices(X_first_picks, len(first_pick_encoder.classes_)):
    print("Invalid indices in X_first_picks")
if not check_indices(X_types, num_types):
    print("Invalid indices in X_types")


lstm_out1 = LSTM(512, return_sequences=True)(concatenated)
attention = Attention(name='attention_weight')(lstm_out1)
output = Dense(num_heroes, activation='softmax')(attention)

lstm_out2 = LSTM(128, return_sequences=True)(concatenated_win)
attention_win = Attention(name='attention_win_weight')(lstm_out2)
win_hidden = Dense(64, activation='relu', kernel_regularizer=l2(0.01))(attention_win)
win_hidden = Dropout(0.5)(win_hidden)
win_output = Dense(1, activation='sigmoid', name='win_output')(win_hidden)

model = Model([input_heroes, input_pick_orders, input_teams, input_first_picks, input_types, input_first_pick_wins], [output, win_output])

optimizer = tf.keras.optimizers.legacy.Adam(learning_rate=0.0001)
    
model.compile(loss={'dense_1': 'categorical_crossentropy', 'win_output': 'binary_crossentropy'},
               optimizer=optimizer, 
              metrics={'dense_1':['accuracy',
                       tf.keras.metrics.TopKCategoricalAccuracy(k=3, name='top_3_accuracy'),
                       tf.keras.metrics.TopKCategoricalAccuracy(k=5, name='top_5_accuracy'),
                       tf.keras.metrics.TopKCategoricalAccuracy(k=10, name='top_10_accuracy')],
                       'win_output':['accuracy']})
    
# Callbacks
checkpoint_filepath = 'data/rec_model.h5'
model_checkpoint_callback = ModelCheckpoint(filepath=checkpoint_filepath, save_best_only=True, monitor='val_loss', mode='min')
early_stopping = EarlyStopping(monitor='val_loss', patience=0)
#learning_rate_scheduler = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=3, min_lr=0.00001)
# Save encoders
with open('data/rec_variables.pkl', 'wb') as f:
    pickle.dump([type_encoder, hero_encoder, max_sequence_length], f)

# Train the model
batch_size = 64
epochs = 500
history = model.fit([X_heroes, X_pick_orders, X_teams, X_first_picks, X_types, X_first_pick_wins], 
                    {'dense_1': y, 'win_output': y_win}, batch_size=batch_size, epochs=epochs, 
                    validation_split=0.2, 
                    callbacks=[model_checkpoint_callback, early_stopping])

# Save model without optimizer
model = tf.keras.models.load_model('data/rec_model.h5', custom_objects={'Attention': Attention})
keras.models.save_model(model, "data/rec_model.h5", include_optimizer=False)

