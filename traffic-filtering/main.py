import base64
import json
import random
import pandas as pd

def sliding_window(data, window_size, step):
    for start_row in range(0, len(data) - window_size + 1, step):
        yield data[start_row:start_row + window_size]

def average_list(nested_list):
    total = 0
    count = 0
    for sublist in nested_list:
        total += sum(sublist)
        count += len(sublist)
    if count == 0:
        return 0  # 빈 리스트 처리
    return total / count

file_name = input("파일을 입력하시오 : ")

test = pd.read_csv(file_name, header=None)
test = test.transpose()

humid = []
pm10 = []
pm25 = []
temp = []

for i in range(len(test)):
    val = test.values[i][0]
    val = val.replace("'", "")
    val = val.replace("b", "", 1)
    json_val = json.loads(val)

    res_payload = json_val['Payload']
    dec_res = base64.b64decode(res_payload)
    dec_res = dec_res.decode("UTF-8")
    str_test = dec_res.replace("'", "\"")
    json_data = json.loads(str_test)

    humid.append(json_data['event']['readings'][0]['objectValue']['humidity'])
    pm10.append(json_data['event']['readings'][0]['objectValue']['pm10'])
    pm25.append(json_data['event']['readings'][0]['objectValue']['pm25'])
    temp.append(json_data['event']['readings'][0]['objectValue']['temperature'])

humid_series = pd.Series(humid)
pm10_series = pd.Series(pm10)
pm25_series = pd.Series(pm25)
temp_series = pd.Series(temp)

# EMA 계산
ema_humid = humid_series.ewm(span=5).mean()
ema_pm10 = pm10_series.ewm(span=5).mean()
ema_pm25 = pm25_series.ewm(span=5).mean()
ema_temp = temp_series.ewm(span=5).mean()

# EMA 기반 절대값 차분 계산
diff_humid = (humid_series - ema_humid).abs().tolist()
diff_pm10 = (pm10_series - ema_pm10).abs().tolist()
diff_pm25 = (pm25_series - ema_pm25).abs().tolist()
diff_temp = (temp_series - ema_temp).abs().tolist()

# 필터링 시작
window_size = 10
step = 10
weight = random.uniform(0.15, 0.2)

# 슬라이딩 윈도우 적용
humid_window = list(sliding_window(diff_humid, window_size, step))
pm10_window = list(sliding_window(diff_pm10, window_size, step))
pm25_window = list(sliding_window(diff_pm25, window_size, step))
temp_window = list(sliding_window(diff_temp, window_size, step))

# 기준값 설정
avdf_humid = average_list(humid_window)
avdf_pm10 = average_list(pm10_window)
avdf_pm25 = average_list(pm25_window)
avdf_temp = average_list(temp_window)

# 필터링
filtered_indices = []
for i in range(len(diff_humid)):
    if (diff_humid[i] < avdf_humid + weight and
            diff_pm10[i] < avdf_pm10 + weight and
            diff_pm25[i] < avdf_pm25 + weight and
            diff_temp[i] < avdf_temp + weight):
        filtered_indices.append(i)

# 조건 만족 시 결과 출력 후 종료
print("입력 트래픽 수 :", len(humid))
print("출력 트래픽 수 : ", len(humid) - len(filtered_indices))
print("감소율 : ", round((len(humid) - (len(humid) - len(filtered_indices))) / len(humid) * 100, 2), "%")