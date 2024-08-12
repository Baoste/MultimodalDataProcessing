import librosa
import numpy as np
import soundfile as sf
import os

wav_files = []
input_folder_path = './input/Game/2024-08-04'
for root, dirs, files in os.walk(input_folder_path):
        for file in files:
            if file.endswith('output.wav'):
                wav_files.append(os.path.join(root, file))

for file_path in wav_files:
    file_name = file_path.split('\\')[-1]
    name_without_end = file_name.split('.')[0]
    y, sr = librosa.load(file_path, sr=None)
    audio_array = np.zeros(int(sr/2))
    audio_array = np.append(audio_array, values=y[:-int(sr/2)])
    out_path = os.path.join(os.path.dirname(file_path), '{0}_output.wav'.format(name_without_end))
    print(out_path)
    sf.write(out_path, audio_array, sr)