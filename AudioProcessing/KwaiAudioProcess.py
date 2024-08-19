import noisereduce as nr
import librosa
import numpy as np
import soundfile as sf
import os
import math
from pydub import AudioSegment, effects  

import torch
from pathlib import Path
from pyannote.audio import Pipeline


# 归一化音频，初步降噪
def normalize_wav(file_path):
    audio_array, sr = librosa.load(file_path, sr=None)
    # # is_loud = librosa.effects.split(y, top_db=2)

    # # split_point = [0]
    # # for point in is_loud:
    # #     split_point.append(int(point[0] / sr * 1000))
    # #     split_point.append(int(point[1] / sr * 1000))

    # # rawsound = AudioSegment.from_file(file_path, "wav")
    # # split_point.append(len(rawsound))
    # # normalized_audio = effects.normalize(rawsound[split_point[0]:split_point[1]], headroom=2)
    # # audio_array = np.array(normalized_audio.get_array_of_samples(), dtype=np.float32) / (1 << (8 * normalized_audio.sample_width - 1))
    # # i = 1
    # # while i < len(split_point)-1:
    # #     normalized_audio = effects.normalize(rawsound[split_point[i]:split_point[i+1]], headroom=2)
    # #     tmp = np.array(normalized_audio.get_array_of_samples(), dtype=np.float32) / (1 << (8 * normalized_audio.sample_width - 1))
    # #     audio_array = np.append(audio_array, values=tmp)
    # #     i += 1

    # # 加载一个噪声样本
    # noise_sample, sr1 = librosa.load("./noiseSample.wav", sr=None)
    # # noise_sample = np.copy(audio_array)
    # # is_noise = librosa.effects.split(audio_array, top_db=35)
    # # for p in is_noise:
    # #     noise_sample[p[0]:p[1]] = 0
    # # sf.write('./output.wav', noise_sample, sr)
    # # 执行降噪，使用噪声样本
    # reduced_noise = nr.reduce_noise(y=audio_array, sr=sr, y_noise=noise_sample, stationary=True, prop_decrease=1)
    # return reduced_noise, sr
    return audio_array, sr


# 本地pipeline
def load_pipeline_from_pretrained(path_to_config: str | Path) -> Pipeline:
    path_to_config = Path(path_to_config)

    print(f"Loading pyannote pipeline from {path_to_config}...")
    # the paths in the config are relative to the current working directory
    # so we need to change the working directory to the model path
    # and then change it back

    cwd = Path.cwd().resolve()  # store current working directory

    # first .parent is the folder of the config, second .parent is the folder containing the 'models' folder
    cd_to = path_to_config.parent.parent.resolve()

    print(f"Changing working directory to {cd_to}")
    os.chdir(cd_to)

    pipeline = Pipeline.from_pretrained(path_to_config)

    print(f"Changing working directory back to {cwd}")
    os.chdir(cwd)

    return pipeline

def speaker_diarization(given_audio_file):
    speaker_info = []

    PATH_TO_CONFIG = "models/pyannote_diarization_config.yaml"
    pipeline = load_pipeline_from_pretrained(PATH_TO_CONFIG)
    if torch.cuda.is_available():
        pipeline.to(torch.device("cuda"))
    diarization = pipeline(given_audio_file, num_speakers=2)
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        print(f"start={turn.start}s stop={turn.end}s speaker_{speaker}")
        speaker_info.append({'start':turn.start, 'stop':turn.end, 'speaker':speaker})

    return speaker_info


# 对音频进行切分
def get_speech_np(y, file_path, sr):
    is_speech= []
    another_is_speech = []
    speaker_info = speaker_diarization(file_path)
    # 查找声音最大的speaker
    speaker_volumes = {}
    for split in speaker_info:
        try:
            vmax = np.max(y[int(split['start']*sr):int(split['stop']*sr)])
            speaker_volumes[split['speaker']] = max(speaker_volumes.get(split['speaker'], vmax), vmax)
        except ValueError as e:
            break
    tag = max(speaker_volumes, key=lambda k: speaker_volumes[k])
    for split in speaker_info:
        if split['speaker'] == tag:
            is_speech.append([int(split['start']*sr), int(split['stop']*sr)])
        else:
            another_is_speech.append([int(split['start']*sr), int(split['stop']*sr)])
    return is_speech, another_is_speech


# 合并两个区间
def interval_merging(list1, list2):
    intervals = [x for x in list1] + [x for x in list2]
    intervals.sort(key=lambda x: x[0])
    merged = []
    for interval in intervals:
        # 如果列表为空或不重合，直接添加
        if not merged or merged[-1][1] < interval[0]:
            merged.append(interval)
        else:
            # 否则进行合并
            merged[-1][1] = max(merged[-1][1], interval[1])
    return merged

# 将其他段静音
def mute_audio(reduced_noise, sr, is_speech, is_speech_extra):
    split_point = [0]
    for point in interval_merging(is_speech, is_speech_extra):
        split_point.append(point[0])
        split_point.append(point[1])
    split_point.append(len(reduced_noise))
    i = 0
    while i < len(split_point):
        # 设置淡入和淡出的时长
        duration = split_point[i+1] - split_point[i]
        if duration > sr * 0.2:
            fade_in_duration = int(min(duration/5, sr/2))
            fade_out_duration = int(min(duration/5, sr/2))
            fade_in = np.linspace(0, 1, fade_in_duration)
            fade_out = np.linspace(1, 0, fade_out_duration)
            reduced_noise[split_point[i]:split_point[i]+fade_out_duration] *= fade_out
            reduced_noise[split_point[i+1]-fade_in_duration:split_point[i+1]] *= fade_in
            reduced_noise[split_point[i]+fade_out_duration:split_point[i+1]-fade_in_duration] *= 0
        i += 2

    return reduced_noise


def kwai_reduce_noise(input_folder_path, output_folder_path):
    wav_files = {}
    for root, dirs, files in os.walk(input_folder_path):
        for file in files:
            if file.endswith('.WAV') or file.endswith('.wav'):
                id = os.path.splitext(file)[0].split('_')[3]
                wav_files[id] = wav_files.get(id, []) + [os.path.join(root, file)]
    for file_id in wav_files:
        files_path = [wav_files[file_id][0], wav_files[file_id][1]]
        files_name = [x.split('\\')[-1] for x in files_path]
        # 无后缀
        names_without_end = [x.split('.')[0] for x in files_name]
        print("处理文件：{0}".format(files_name[0]))
        y0, sr = normalize_wav(files_path[0])
        is_speech_0, another_is_speech_0 = get_speech_np(y0, files_path[0], sr)
        print("处理文件：{0}".format(files_name[1]))
        y1, sr = normalize_wav(files_path[1])
        is_speech_1, another_is_speech_1 = get_speech_np(y1, files_path[1], sr)
        reduced_noise_0 = mute_audio(y0, sr, is_speech_0, another_is_speech_1)
        reduced_noise_1 = mute_audio(y1, sr, is_speech_1, another_is_speech_0)
        # 保存降噪后的音频
        #out_path = os.path.join(output_folder_path, '{0}_output.wav'.format(name_without_end))
        out_path_0 = os.path.join(os.path.dirname(files_path[0]), '{0}_output.wav'.format(names_without_end[0]))
        out_path_1 = os.path.join(os.path.dirname(files_path[1]), '{0}_output.wav'.format(names_without_end[1]))
        sf.write(out_path_0, reduced_noise_0, sr)
        sf.write(out_path_1, reduced_noise_1, sr)


def main():
    input_folder_path = './input'
    output_folder_path = './output'
    kwai_reduce_noise(input_folder_path, output_folder_path)


if __name__ == "__main__":
    main()