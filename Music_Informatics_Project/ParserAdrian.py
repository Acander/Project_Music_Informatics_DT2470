"""Musical notation parser that parses the folkRNN Parser dataset (https://github.com/ztime/polska) in the following ways:
    * Removes the meter tokens
    * Transposes all the notations to C-major (but to keep the original key token)
It is meant that this should improve performance of the folkRNN by reducing the size of the vocabulary
"""

import re
import numpy as np

# Valid metrics according to folkRNN parser
valid_metrics_regex = [
    '\[M:8\/8\]\n',
    '\[M:4\/4\]\n',
    '\[M:2\/2\]\n',
    '\[M:3\/4\]\n',
    '\[M:2\/4\]\n',
    '\[M:6\/8\]\n',
    '\[M:8\/16\]\n',
    '\[M:5\/4\]\n',
    '\[M:3\/8\]\n'
]

chromatic_scale_sharps = ['A', '^A', 'B', 'C', '^C', 'D', '^D', 'E', 'F', '^F', 'G', '^G']
chromatic_scale_flats = ['A', '_B', 'B', 'C', '_D', 'D', '_E', 'E', 'F', '_G', 'G', '_A']

key_types = [['Maj', 'Dor', 'Phr', 'Lyd', 'Mix', 'Min', 'Loc'],
             [0, 2, 3, 5, 7, 9, 11]
]

def import_music_samples():
    filename = "training_data_from_folkRNN.txt"
    with open(filename, 'r') as file:
        raw_text = file.read()

    return raw_text


def remove_meters(music):
    for metric_reg in valid_metrics_regex:
        music, n = re.subn(metric_reg, '', music)

    print(music)
    return music


def transpose(music):
    music_pieces = split_into_pieces(music)
    music_pieces, keys = get_keys(music_pieces)
    music_pieces = shift_notes(music_pieces, keys)

def split_into_pieces(music):
    return music.split("\n\n")

def get_keys(music_pieces):
    keys = []
    print(len(music_pieces))
    for music_piece in music_pieces:
        key = get_key(music_piece)
        if key[0] not in chromatic_scale_flats:
            music_pieces.remove(music_piece)
            continue
        keys.append(key)
    print(len(music_pieces))
    print(len(keys))

    return music_pieces, keys

def get_key(music_piece):
    return (get_tonic(music_piece), get_scale_type(music_piece))

def get_tonic(music_piece):
    kt = key_token(music_piece)
    if is_flat(kt[4]):
        return "_" + kt[3:4]
    return kt[3]

def get_scale_type(music_piece):
    kt = key_token(music_piece)
    return kt[len(kt)-4:len(kt)-1]

def is_flat(letter_after_tonic):
    return letter_after_tonic == "b"

def key_token(music_piece):
    return music_piece.split("\n")[1]

def shift_notes(music_pieces, keys):
    for i, music_piece in enumerate(music_pieces):
        music_pieces[i] = shift_to_major(music_piece, keys[i])

def shift_to_major(music_piece, key):
    get_shift_value(key)

    music = music_piece.split("\n")[2]


def get_shift_value(key):
    scale_types = key_types[0]
    print(key)
    #print(scale_types.index(key[1]))

if __name__ == '__main__':
    music = import_music_samples()
    # print(music)
    music_without_metrics = remove_meters(music)
    transpose(music_without_metrics)
