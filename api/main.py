import saferx
# import restapi

# get model run , input parameter, output paremeter

# run 0.0.0.0.8080:

import requests
import json
# base URL
BASE_URL = 'http://localhost:8000'

# 테스트할 파일 경로
location_file_path = '/mount/nas/disk02/Data/Health/Mental_Health/SAFER/20240514/snuh_all_20240514/snuh_location.csv'
sensor_file_path ='/mount/nas/disk02/Data/Health/Mental_Health/SAFER/20240812/snuh_20240806/snuh_sensing.csv'
trait_file_path ='/mount/nas/disk02/Data/Health/Mental_Health/SAFER/20240514/trait_state/SAFER_selected_trait.csv'
crf_file_path='/mount/nas/disk02/Data/Health/Mental_Health/SAFER/20240514/trait_state/SAFER_selected_state.csv'

# 테스트용 location_dict 정의
location_dict = {
    "(37.579239,126.998505)": "hallway",
    "(37.579326,126.998565)": "hallway",
    "(37.579308,126.998482)": "ward",
    "(37.579334,126.998444)": "ward",
    "(37.579339,126.998502)": "ward",
    "(37.579350,126.998456)": "ward",
    "(37.579388,126.998612)": "hallway",
    "(37.579361,126.998559)": "ward",
    "(37.579373,126.998512)": "ward",
    "(37.579377,126.998570)": "ward",
    "(37.579403,126.998535)": "ward",
    "(37.579474,126.998598)": "other",
    "(37.579320,126.998629)": "ward",
    "(37.579338,126.998611)": "ward",
    "(37.579348,126.998652)": "ward",
    "(37.579353,126.998622)": "ward",
    "(37.579375,126.998676)": "ward",
    "(37.579397,126.998682)": "ward",
    "(37.579471,126.998672)": "hallway",
    "(37.579545,126.998724)": "hallway",
    "(37.579501,126.998659)": "other",
    "(37.579514,126.998615)": "other",
    "(37.579551,126.998659)": "other",
    "(37.579580,126.998679)": "other",
    "(37.579277,126.998448)": "ward",
    "(37.579270,126.998489)": "ward",
    "(37.579247,126.998542)": "ward",
    "(37.579225,126.998565)": "ward",
    "(37.579264,126.998573)": "ward",
    "(37.579251,126.998622)": "ward",
    "(37.579294,126.998593)": "ward",
    "(37.579268,126.998632)": "ward",
    "(37.579428,126.998571)": "ward",
    "(37.579452,126.998534)": "ward",
    "(37.579534,126.998785)": "other"
}

########################################################################## m1  ##########################################################################
def call_api(url, method='POST', files=None, data=None, json_data=None):
    """API 호출 유틸리티 함수"""
    try:
        response = requests.request(method, url, files=files, data=data, json=json_data)
        response.raise_for_status()
        print(f"{url} 호출 성공:", response.json())
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f"{url} 호출 실패:", err)
        return None

# 1. /assign_location_labels 호출
location_files = {'location_file': open(location_file_path, 'rb')}
location_data = {'location_dict': json.dumps(location_dict)}
call_api(f'{BASE_URL}/m1_assign_location_labels', files=location_files, data=location_data)


# 2. /load_sensing_data 호출
sensor_files = {'sensor_file': open(sensor_file_path, 'rb')}
call_api(f'{BASE_URL}/m1_load_sensing_data', files=sensor_files)



# set_suicide_flag 데이터를 JSON 형식으로 변환
import pandas as pd

suicide_flags = [
    {'name': '101-14KNJ', 'time': pd.to_datetime('2023-07-14 14:00:00')},
    {'name': '101-14KNJ', 'time': pd.to_datetime('2023-07-14 10:00:00')},
    {'name': '101-14KNJ', 'time': pd.to_datetime('2023-07-15 11:00:00')},
    {'name': '101-14KNJ', 'time': pd.to_datetime('2023-07-17 17:00:00')},
    
    {'name': '101-23PDM', 'time': pd.to_datetime('2023-09-17 12:00:00')},
    {'name': '101-3JYS', 'time': pd.to_datetime('2023-06-04 22:00:00')},
    
    {'name': '101-37SJM', 'time': pd.to_datetime('2023-12-29 21:00:00')},
    {'name': '101-37SJM', 'time': pd.to_datetime('2023-12-30 16:00:00')},
    {'name': '101-40OJE', 'time': pd.to_datetime('2023-12-28 19:00:00')},
    
    {'name': '101-46KSE', 'time': pd.to_datetime('2023-02-03 21:00:00')},
    {'name': '101-46KSE', 'time': pd.to_datetime('2023-02-04 15:00:00')},
    
    {'name': '101-49SJM', 'time': pd.to_datetime('2023-03-13 00:00:00')},
    {'name': '101-49SJM', 'time': pd.to_datetime('2023-03-13 23:00:00')},
    {'name': '101-49SJM', 'time': pd.to_datetime('2023-03-29 14:00:00')},
    
    {'name': '101-54LYR', 'time': pd.to_datetime('2024-02-28 18:00:00')},
    {'name': '101-54LYR', 'time': pd.to_datetime('2024-02-28 22:00:00')},
    {'name': '101-54LYR', 'time': pd.to_datetime('2024-03-11 18:00:00')},
    
    {'name': '101-59KSJ', 'time': pd.to_datetime('2024-04-02 10:00:00')},
    {'name': '101-59KSJ', 'time': pd.to_datetime('2024-04-02 11:00:00')},
    
    {'name': '101-61LSK', 'time': pd.to_datetime('2024-04-05 21:00:00')},
    {'name': '101-61LSK', 'time': pd.to_datetime('2024-04-06 19:00:00')},
    {'name': '101-61LSK', 'time': pd.to_datetime('2024-04-07 18:00:00')},
    {'name': '101-61LSK', 'time': pd.to_datetime('2024-04-08 18:00:00')},
    {'name': '101-61LSK', 'time': pd.to_datetime('2024-04-09 06:00:00')},
    {'name': '101-61LSK', 'time': pd.to_datetime('2024-04-10 06:00:00')},
    {'name': '101-61LSK', 'time': pd.to_datetime('2024-04-11 06:00:00')},
    
    {'name': '101-63KYS', 'time': pd.to_datetime('2024-04-08 13:00:00')},
    {'name': '101-63KYS', 'time': pd.to_datetime('2024-04-21 01:00:00')}
]

# JSON 형식으로 변환할 준비
json_suicide_flags = [{'name': entry['name'], 'time': entry['time'].isoformat()} for entry in suicide_flags]


# 3. /load_data 호출
files = {
    'crf_file': open(crf_file_path, 'rb'),
    'trait_file': open(trait_file_path, 'rb')
}
load_data_response = call_api(f'{BASE_URL}/m1_load_data', files=files, json_data={'suicide_flags': json_suicide_flags})
if load_data_response:
    print("All data loaded successfully.")
else:
    print("Failed to load data. Stopping further execution.")
    exit(1)

# 4. /predict 호출
predict_response = call_api(f'{BASE_URL}/m1_predict')
if predict_response:
    print("Prediction Completed:", predict_response['predictions'])
else:
    print("Prediction failed. Please check the logs for details.")


########################################################################## m2  ##########################################################################

# def call_api(url, method='POST', files=None, data=None, json_data=None):
#     """API 호출 유틸리티 함수"""
#     try:
#         response = requests.request(method, url, files=files, data=data, json=json_data)
#         response.raise_for_status()
#         print(f"{url} 호출 성공:", response.json())
#         return response.json()
#     except requests.exceptions.HTTPError as err:
#         print(f"{url} 호출 실패:", err)
#         return None

# # 1. /assign_location_labels 호출
# location_files = {'location_file': open(location_file_path, 'rb')}
# location_data = {'location_dict': json.dumps(location_dict)}
# call_api(f'{BASE_URL}/assign_location_labels', files=location_files, data=location_data)

# # 2. /load_sensing_data 호출
# sensor_files = {'sensor_file': open(sensor_file_path, 'rb')}
# call_api(f'{BASE_URL}/load_sensing_data', files=sensor_files)

# # 3. /load_data 호출
# files = {
#     'crf_file': open(crf_file_path, 'rb'),
#     'trait_file': open(trait_file_path, 'rb')
# }
# load_data_response = call_api(f'{BASE_URL}/load_data', files=files)

# if load_data_response:
#     print("All data loaded successfully.")
# else:
#     print("Failed to load data. Stopping further execution.")
#     exit(1)


# # 4. /predict 호출
# predict_response = call_api(f'{BASE_URL}/predict')

# if predict_response:
#     print("Prediction Completed:", predict_response['predictions'])
# else:
#     print("Prediction failed. Please check the logs for details.")







