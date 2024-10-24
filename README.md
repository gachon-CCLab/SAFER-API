
## 소개

위치와 센서 데이터를 활용한 데이터 전처리, 병합, 그리고 예측을 수행합니다. 이 API 서버는 두 가지 모델(m1과 m2)을 통해 각각의 목적에 맞는 데이터 처리와 예측을 제공합니다.

## 기능

- 위치 레이블 할당
- 센서 데이터 로드 및 전처리
- 데이터 병합 및 처리
- 예측 수행

## API 엔드포인트

아래는 제공되는 API 엔드포인트와 요청/응답 형식에 대한 상세 정보입니다.

| **Endpoint**                  | **Model name** | **Method** | **Description**                                           | **Request Parameters**                                                                                                                                                 | **Response**                                                                                             | **Status Codes**                           |
|-------------------------------|----------------|------------|-----------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------|--------------------------------------------|
| `/assign_location_labels`     | m2             | POST       | 위치 레이블을 CSV 파일과 좌표 딕셔너리를 통해 할당         | **Form Data**:<br>`location_file`: 위치 CSV 파일<br>`location_dict`: JSON 문자열의 좌표-레이블 딕셔너리 (병동 내 위치정보)                                             | `{'message': 'Location labels assigned successfully'}`                                                 | 200: 성공<br>400: 유효하지 않은 요청<br>500: 서버 오류 |
| `/load_sensing_data`          | m2             | POST       | 센서 데이터를 CSV 파일로 로드 및 전처리                    | **Form Data**:<br>`sensor_file`: 센서 CSV 파일                                                                                                                         | `{'message': 'Sensor data loaded successfully', 'sensor_data': {...}}`                                  | 200: 성공<br>400: 파일 누락<br>500: 서버 오류 |
| `/load_data`                  | m2             | POST       | 저장된 location, sensor 데이터와 CRF, Trait 파일을 병합 및 처리 | **Form Data**:<br>`crf_file`: CRF CSV 파일<br>`trait_file`: Trait CSV 파일                                                                                             | `{'message': 'All data loaded and processed successfully'}`                                            | 200: 성공<br>400: 데이터 누락<br>500: 서버 오류 |
| `/predict`                    | m2             | POST       | 저장된 데이터로 예측 수행                                   | N/A                                                                                                                                                                    | `{'message': 'Prediction completed successfully', 'predictions': [...]}`                                | 200: 성공<br>400: 데이터 오류<br>500: 서버 오류 |
| `/m1_assign_location_labels`  | m1             | POST       | 모델 1의 위치 레이블을 CSV 파일과 좌표 딕셔너리로 할당       | **Form Data**:<br>`location_file`: 위치 CSV 파일<br>`location_dict`: JSON 문자열의 좌표-레이블 딕셔너리                                                               | `{'message': 'Location labels assigned successfully'}`                                                 | 200: 성공<br>400: 유효하지 않은 요청<br>500: 서버 오류 |
| `/m1_load_sensing_data`       | m1             | POST       | 모델 1의 센서 데이터를 로드 및 전처리                       | **Form Data**:<br>`sensor_file`: 센서 CSV 파일                                                                                                                          | `{'message': 'Sensor data loaded successfully'}`                                                        | 200: 성공<br>400: 파일 누락<br>500: 서버 오류 |
| `/m1_load_data`               | m1             | POST       | 모델 1의 location, sensor 데이터와 CRF, Trait 파일을 병합    | **Form Data**:<br>`crf_file`: CRF CSV 파일<br>`trait_file`: Trait CSV 파일<br>`json_data`: 자해 플래그 JSON 문자열                                                  | `{'message': 'All data loaded and processed successfully'}`                                            | 200: 성공<br>400: 데이터 오류<br>500: 서버 오류 |
| `/m1_predict`                 | 1m             | POST       | 모델 1의 병합된 데이터로 예측 수행                           | N/A                                                                                                                                                                    | `{'message': 'Prediction completed successfully', 'predictions': [...]}`                                | 200: 성공<br>400: 데이터 오류<br>500: 서버 오류 |

## 설치

프로젝트를 로컬 환경에 설치하려면 다음 명령어를 사용하세요:

```bash
# 저장소를 클론합니다.
git clone https://github.com/사용자명/저장소명.git

# 디렉토리로 이동합니다.
cd 저장소명

# 필요한 패키지를 설치합니다.
pip install -r requirements.txt
```

## 사용법

프로젝트 서버를 실행하려면 아래 명령어를 사용하세요:

```bash
python app.py
```
python main.py -> test_file
서버가 실행되면 제공된 API 엔드포인트에 접근하여 데이터를 처리할 수 있습니다.

