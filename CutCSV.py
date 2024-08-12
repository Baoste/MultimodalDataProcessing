import pandas as pd

def time_to_milliseconds(time_str):
    # 解析时间字符串
    hours, minutes, seconds, milliseconds = map(int, time_str.split(':'))
    # 计算总毫秒数
    total_milliseconds = ((hours * 3600 + minutes * 60 + seconds) * 1000 + milliseconds)
    
    return total_milliseconds

file_name = r"D:\IF Files\Kwai\2024-07-29\Scene_1_01_0005_Subscenes\15_22_42_BP_TakeRecordingExporter_ks-iPhone.csv"
df = pd.read_csv(file_name)
df['time'] = df['Timecode'].apply(time_to_milliseconds)
df['time'] = df['time'] - df['time'].iloc[0]
start_time = 5000
end_time = 10000
df = df[~df['time'].between(start_time, end_time)]

df.iloc[:,:-1].to_csv('result.csv', index=False)