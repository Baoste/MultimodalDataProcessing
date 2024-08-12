import os, shutil, re

# 移动fbx
def move_fbx():
    input_folder_path = r'D:\ExportedAsset\Game'
    target_root = r'.\output\Game'
    for root, dirs, files in os.walk(input_folder_path):
            for file in files:
                if file.endswith('.FBX'):
                    target_path = target_root
                    file_path = os.path.join(root, file)
                    date_folder = file_path.split('\\')[3:-1]
                    for f in date_folder:
                        target_path = os.path.join(target_path, f) 
                    # print(target_path)
                    if not os.path.exists(target_path):
                        os.makedirs(os.path.abspath(target_path))
                    shutil.copy(file_path, target_path)


# 移动csv
def move_csv():
    input_folder_path = r'D:\IF Files\Kwai\new'
    target_root = r'.\output\Game'
    for root, dirs, files in os.walk(input_folder_path):
            for file in files:
                if file.endswith('.csv'):
                    target_path = target_root
                    file_path = os.path.join(root, file)
                    date_folder = file_path.split('\\')[4:-1]
                    for f in date_folder:
                        target_path = os.path.join(target_path, f) 
                    # print(target_path)
                    if not os.path.exists(target_path):
                        os.makedirs(os.path.abspath(target_path))
                    shutil.copy(file_path, target_path)

# 提取wav至一个文件夹
def export_wav():
    input_folder_path = r'D:\ExportedAsset\Game'
    target_root = r'.\output\Game'
    for root, dirs, files in os.walk(input_folder_path):
            for file in files:
                if file.endswith('.WAV'):
                    file_path = os.path.join(root, file)
                    date_folder = root.split('\\')[-4]
                    target_path = os.path.join(target_root, date_folder)
                    if not os.path.exists(target_path):
                        os.makedirs(os.path.abspath(target_path))
                    shutil.copy(file_path, target_path)
                    

# 移动wav
def move_wav():
    input_folder_path = r'D:\IF Files\code\Py\ReduceNoise\input\已降噪音频'
    target_root = r'.\output\Game'
    for root, dirs, files in os.walk(input_folder_path):
            for file in files:
                if file.endswith('output.wav'):
                    target_path = target_root
                    file_path = os.path.join(root, file)
                    target_path = os.path.join(target_path, file_path.split('\\')[-2])
                    target_path = os.path.join(target_path, 'save')
                    m = re.match(r'^(Audio)_(Scene_\d_\d+)_(.+)', file)
                    scene_folder = m.group(2) + '_Subscenes'
                    target_path = os.path.join(target_path, scene_folder)
                    if not os.path.exists(target_path):
                        continue
                    target_path = os.path.join(target_path, 'Audio')
                    if not os.path.exists(target_path):
                        os.makedirs(os.path.abspath(target_path))
                    # 文件已存在
                    if os.path.exists(os.path.join(target_path, file)):
                        continue
                    # print(target_path)
                    shutil.copy(file_path, target_path)

if __name__ == '__main__':
    move_wav()