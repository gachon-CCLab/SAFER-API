import saferx
# import restapi

# get model run , input parameter, output paremeter

# run 0.0.0.0.8080:

import requests

# base URL
BASE_URL = 'http://localhost:8000'

# 테스트할 파일 경로
location_file_path = '/mount/nas/disk02/Data/Health/Mental_Health/SAFER/20240514/snuh_all_20240514/snuh_location.csv'
sensor_file_path ='/mount/nas/disk02/Data/Health/Mental_Health/SAFER/20240812/snuh_20240806/snuh_sensing.csv'
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

##### 파일과 location_dict 전송 준비 #####

# location_data 준비
location_files = {'location_file': open(location_file_path, 'rb')}
location_data = {'location_dict': str(location_dict)}

# sensor_data 준비
sensor_files = {'sensor_file' : open(sensor_file_path,'rb')}

# crf_data 준비

#####  POST 요청 전송 ##### 

# 위치 데이터
response = requests.post(f'{BASE_URL}/assign_location_labels', files=location_files, data=location_data)

# 응답 확인
if response.status_code == 200:
    print("성공적으로 위치 데이터 라벨이 할당되었습니다.")
    print(response.json())
else:
    print(f"위치 데이터 오류 발생: {response.status_code}")
    print(response.json())

# 센서 데이터
response = requests.post(f'{BASE_URL}/load_sensing_data', files=sensor_files)
if response.status_code == 200 :
    print("성공적으로 센서 데이터 라벨이 할당되었습니다.")
    print(response.json())







# response = requests.post(f'{BASE_URL}/load_data', files=files)
# print(response.json())

# # 2. merge_location_and_sensor 엔드포인트 호출
# response = requests.post(f'{BASE_URL}/merge_location_and_sensor')
# print(response.json())

# # 3. process_crf_data 엔드포인트 호출
# response = requests.post(f'{BASE_URL}/process_crf_data')
# print(response.json())

# # 4. merge_trait_data 엔드포인트 호출
# response = requests.post(f'{BASE_URL}/merge_trait_data')
# print(response.json())

# # 5. predict 엔드포인트 호출
# files = {
#     'data_file': open('merged_data_m2_dong.csv', 'rb'),
# }
# response = requests.post(f'{BASE_URL}/predict', files=files)
# print(response.json())
