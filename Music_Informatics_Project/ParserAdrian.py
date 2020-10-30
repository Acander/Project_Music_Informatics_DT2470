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
    '\[M:3\/8\]\n',
    '\[M:9\/8\]\n'
]

valid_metrics_regex_for_bugs = [
    '\[M:8\/8\] ',
    '\[M:4\/4\] ',
    '\[M:2\/2\] ',
    '\[M:3\/4\] ',
    '\[M:2\/4\] ',
    '\[M:6\/8\] ',
    '\[M:8\/16\] ',
    '\[M:5\/4\] ',
    '\[M:3\/8\] ',
    '\[M:9\/8\] '
]

#  chromatic_scale_sharps = ['C', '^C', 'D', '^D', 'E', 'F', '^F', 'G', '^G', 'A', '^A', 'B']
chromatic_scale = [['C', '_D', 'D', '_E', 'E', 'F', '_G', 'G', '_A', 'A', '_B', 'B'],
                   ['c', '_d', 'd', '_e', 'e', 'f', '_g', 'g', '_a', 'a', '_b', 'b'],
                   ['c\'', '_d\'', 'd\'', '_e\'', 'e\'', 'f\'', '_G\'', 'G\'', '_A\'', 'A\'', '_B\'', 'B\'']]

sharp_to_flat = [[['^C', '^D', '^F', '^G', '^A'],
                  ['_D', '_E', '_G', '_A', '_B']],
                 [['^c', '^d', '^f', '^g', '^a'],
                  ['_d', '_e', '_g', '_a', '_b']],
                 [['^c\'', '^d\'', '^f\'', '^g\'', '^a\''],
                  ['_d\'', '_e\'', '_g\'', '_a\'', '_b\'']]]

key_types = [['Maj', 'Dor', 'Phr', 'Lyd', 'Mix', 'Min', 'Loc'],
             [0, 2, 3, 5, 7, 9, 11]
             ]


def import_music_samples():
    filename = "training_data_from_folkRNN.txt"
    with open(filename, 'r') as file:
        raw_text = file.read()

    return raw_text


def remove_meters(music):
    for i, metric_reg in enumerate(valid_metrics_regex):
        music, _ = re.subn(metric_reg, '', music)
        music, _ = re.subn(valid_metrics_regex_for_bugs[i], '', music)

    #  print(music)
    return music


def transpose(music):
    music_pieces = split_into_pieces(music)
    music_pieces, keys = get_keys(music_pieces)
    music_pieces = shift_notes(music_pieces, keys)


def split_into_pieces(music):
    music_pieces = music.split("\n\n")
    return remove_noisy_data(music_pieces)


def remove_noisy_data(music_pieces):
    for music_piece in music_pieces:
        if len(music_piece.split("\n")) > 3:
            music_pieces.remove(music_piece)
    return music_pieces


def get_keys(music_pieces):
    keys = []
    for music_piece in music_pieces:
        key = get_key(music_piece)
        keys.append(key)

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
    return kt[len(kt) - 4:len(kt) - 1]


def is_flat(letter_after_tonic):
    return letter_after_tonic == "b"


def key_token(music_piece):
    return music_piece.split("\n")[1]


def shift_notes(music_pieces, keys):
    for i, music_piece in enumerate(music_pieces):
        shift_value = chromatic_scale.index(keys[i])
        shift_value += shift_to_major(keys[i])
        if shift_value > len(chromatic_scale):
            shift_value -= len(chromatic_scale)


def shift_to_major(key):
    scale_types = key_types[0]
    #  print(key)

    return scale_types.index(key[1])


def shift(music_tokens, shift_value):
    if shift_value == 0:
        return music_tokens
    music_tokens


def convert_all_sharps_to_flats(music):
    music_pieces = music.split("\n\n")
    #  print(music_pieces)
    for j, piece in enumerate(music_pieces):
        music_tokens = piece.split("\n")[2].split(" ")
        for i, token in enumerate(music_tokens):
            music_tokens[i] = convert_sharp_to_flat(token)
        music_tokens = concatenate_string_array(music_tokens)
        music_pieces[j] = piece.split("\n")[0] + "\n" + piece.split("\n")[1] + "\n" + music_tokens
    music = " "
    for piece in music_pieces:
        music += piece + "\n\n"

    return music


def concatenate_string_array(string_array):
    final_string = ""
    for string in string_array:
        final_string += string + " "
    return final_string


def convert_sharp_to_flat(token):
    if token[0] == '^':
        for octave in sharp_to_flat:
            if token in octave[0]:
                note = octave[0].index(token)
                return octave[1][note]
    return token


if __name__ == '__main__':
    music = import_music_samples()
    music_without_metrics = remove_meters(music)
    music_without_metrics_and_with_flats = convert_all_sharps_to_flats(music_without_metrics)
    #  print(music_without_metrics_and_with_flats)
    transpose(music_without_metrics)
