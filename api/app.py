from flask import Flask, request, jsonify
import saferx
import pandas as pd
import torch
import numpy as np
import os
import tempfile
from flask import jsonify
import json




app = Flask(__name__)
# 전역 변수 선언
stored_location_data = None
stored_sensor_data = None
stored_merged_data = None

stored_location_data_m1 = None
stored_sensor_data_m1 = None
stored_merged_data_m1 = None


m2_location_processor = saferx.M2LocationProcessor()
m2_sensor_data_processor = saferx.M2SensorDataProcessor()
m2_data_processor = saferx.M2DataProcessor()

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
m2_predictor = saferx.Predictor(device)




def save_to_temp_file(dataframe):
    """DataFrame을 임시 파일로 저장하고 경로 반환."""
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    dataframe.to_csv(tmp_file.name, index=False)
    print(f"Data saved to temporary file: {tmp_file.name}")
    return tmp_file.name



########################################################################## m2_data ##########################################################################
##################################### ###################################### ##################################### ######################################
##################################### ###################################### ##################################### ######################################
##################################### ###################################### ##################################### ######################################

########################################################################## m2_location ##########################################################################
@app.route('/assign_location_labels', methods=['POST'])
def assign_location_labels():
    global stored_location_data 
    try:
        # 요청에서 파일 및 location_dict 추출
        location_file = request.files.get('location_file')
        location_dict_raw = request.form.get('location_dict')

        # 파일과 location_dict 유효성 검사
        if not location_file or not location_dict_raw:
            raise ValueError("location_file과 location_dict가 필요합니다.")

        # JSON 문자열로 전송된 location_dict 파싱
        location_dict = {
            tuple(map(float, k.strip('()').split(','))): v
            for k, v in eval(location_dict_raw).items()
        }

        # CSV 파일 로드
        processed_data = m2_location_processor.load_data_from_csv(location_file)
        if processed_data is None or processed_data.empty:
            raise ValueError("CSV 파일을 로드하는 중 오류가 발생했습니다.")

        print("CSV 데이터 로드 완료:", processed_data.head())

        # 위치 라벨 할당
        assigned_data = m2_location_processor.assign_location_labels(processed_data, location_dict)
        if assigned_data is None or assigned_data.empty:
            raise ValueError("위치 레이블 할당에 실패했습니다.")

        print("위치 레이블 할당 완료:", assigned_data.head())

        

        # 메모리에 저장
        stored_location_data = assigned_data

        # JSON 응답 반환
        return jsonify({
            'message': 'Location labels assigned successfully'
        }), 200

    except ValueError as e:
        print(f"ValueError: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f"Exception: {e}")
        return jsonify({'error': str(e)}), 500

##########################################################################  m2_sensor ########################################################################## 
##################################### ###################################### ##################################### ######################################
##################################### ###################################### ##################################### ######################################
##################################### ###################################### ##################################### ######################################
@app.route('/load_sensing_data', methods=['POST'])
def load_sensing_data():
    global stored_sensor_data
    try:
        sensor_file = request.files.get('sensor_file')
        if not sensor_file:
            return jsonify({'error': 'No sensor file provided'}), 400

        sensor_data = m2_sensor_data_processor.load_sensing_data(sensor_file)
        sensor_data = m2_sensor_data_processor.process_sensing_data(sensor_data)
        sensor_data = m2_sensor_data_processor.aggregate_sensing_data(sensor_data)
        sensor_data = m2_sensor_data_processor.reorganize_column_names(sensor_data)

        # 메모리에 저장
        stored_sensor_data = sensor_data
        return jsonify({'message': 'Sensor data loaded successfully', 'sensor_data': sensor_data.to_dict()}), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


##########################################################################  m2_data ########################################################################## 
@app.route('/load_data', methods=['POST'])
def load_data():
    global stored_location_data, stored_sensor_data,stored_merged_data

    try:
        # 저장된 location 및 sensor 데이터 사용 확인
        if stored_location_data is None or stored_sensor_data is None:
            raise ValueError("저장된 location 또는 sensor 데이터가 없습니다.")

        # 요청에서 추가 파일(CRF, trait) 추출
        crf_file = request.files.get('crf_file')
        trait_file = request.files.get('trait_file')

        # 추가 데이터 로드
        crf_data = pd.read_csv(crf_file) if crf_file else None
        trait_data = pd.read_csv(trait_file) if trait_file else None

        if trait_data is None or crf_data is None:
            raise ValueError("CRF 또는 Trait 파일이 누락되었습니다.")

        print("CRF 및 Trait 데이터 로드 완료")
        print("Trait Data Head:\n", trait_data.head())

        # 데이터 로드 및 병합 수행
        m2_data_processor.load_data(
            stored_location_data, stored_sensor_data, crf_data, trait_data
        )

        print("Location과 Sensor 데이터 병합 중...")
        m2_data_processor.merge_location_and_sensor()
        print("Location과 Sensor 데이터 병합 완료")

        print("CRF 데이터 처리 중...")
        m2_data_processor.process_crf_data()
        print("CRF 데이터 처리 완료")

        print("Trait 데이터 병합 중...")
        merged_data = m2_data_processor.merge_trait_data()
        print("Trait 데이터 병합 완료:\n", merged_data.head())

        stored_merged_data = merged_data
        return jsonify({'message': 'All data loaded and processed successfully'}), 200

    except ValueError as ve:
        print(f"ValueError: {ve}")
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        print(f"Exception: {e}")
        return jsonify({'error': str(e)}), 500


##########################################################################  m2_model ########################################################################### 

##################################### ###################################### ##################################### ######################################
##################################### ###################################### ##################################### ######################################
##################################### ###################################### ##################################### ######################################


@app.route('/predict', methods=['POST'])
def predict():
    global stored_merged_data  # 전역 변수 사용

    try:
        # 병합된 데이터 유효성 확인
        if stored_merged_data is None:
            raise ValueError("병합된 데이터가 없습니다. 데이터를 먼저 로드하세요.")
        if stored_merged_data.empty:
            raise ValueError("병합된 데이터가 비어 있습니다.")

        print("Predicting with the following data:\n", stored_merged_data.head())

        # DataFrame을 임시 파일로 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_file:
            temp_file_path = tmp_file.name
            stored_merged_data.to_csv(temp_file_path, index=False)
            print(f"Data saved to temporary file: {temp_file_path}")

        # 데이터 전처리 수행 및 예외 처리
        try:
            data_loader = m2_predictor.preprocess_data(temp_file_path)

        except KeyError as e:
            missing_column = str(e).strip("[]'")
            print(f"Preprocessing error: {e} - 누락된 컬럼: {missing_column}")

            # 누락된 컬럼을 0으로 채워 추가
            stored_merged_data[missing_column] = 0

            # 다시 임시 파일로 저장 후 전처리 재시도
            with open(temp_file_path, 'w') as f:
                stored_merged_data.to_csv(f, index=False)
            data_loader = m2_predictor.preprocess_data(temp_file_path)

        except Exception as e:
            print(f"Preprocessing error: {e}")
            raise ValueError(f"데이터 전처리 중 오류 발생: {e}")

        # 예측 수행
        try:
            predictions = m2_predictor.predict(data_loader)
        except Exception as e:
            print(f"Prediction error: {e}")
            raise ValueError(f"예측 중 오류 발생: {e}")

        print("예측 완료:", predictions)

        # 임시 파일 삭제
        os.remove(temp_file_path)

        # 예측 결과 반환
        return jsonify({
            'message': 'Prediction completed successfully',
            'predictions': predictions.tolist()
        }), 200

    except ValueError as ve:
        print(f"ValueError: {ve}")
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        print(f"Exception: {e}")
        return jsonify({'error': str(e)}), 500




########################################################################## m1_data ##########################################################################
##################################### ###################################### ##################################### ######################################
##################################### ###################################### ##################################### ######################################
##################################### ###################################### ##################################### ######################################


m1_location_processor = saferx.M1LocationProcessor()
m1_sensor_data_processor = saferx.M1SensorDataProcessor()
m1_data_processor = saferx.M1DataProcessor()


########################################################################## m1_location ##########################################################################
##################################### ###################################### ##################################### ######################################
##################################### ###################################### ##################################### ######################################
##################################### ###################################### ##################################### ######################################

@app.route('/m1_assign_location_labels', methods=['POST'])
def m1_assign_location_labels():
    global stored_location_data_m1
    try:
        # 요청에서 파일 및 location_dict 추출
        location_file = request.files.get('location_file')
        location_dict_raw = request.form.get('location_dict')

        # 파일과 location_dict 유효성 검사
        if not location_file or not location_dict_raw:
            raise ValueError("location_file과 location_dict가 필요합니다.")

        # JSON 문자열로 전송된 location_dict 파싱
        location_dict = {
            tuple(map(float, k.strip('()').split(','))): v
            for k, v in eval(location_dict_raw).items()
        }

        # CSV 파일 로드
        processed_data = m1_location_processor.load_data_from_csv(location_file)
        if processed_data is None or processed_data.empty:
            raise ValueError("CSV 파일을 로드하는 중 오류가 발생했습니다.")

        print("CSV 데이터 로드 완료:", processed_data.head())

        # 위치 라벨 할당
        assigned_data = m1_location_processor.assign_location_labels(processed_data, location_dict)
        if assigned_data is None or assigned_data.empty:
            raise ValueError("위치 레이블 할당에 실패했습니다.")

        print("위치 레이블 할당 완료:", assigned_data.head())

        # 메모리에 저장
        stored_location_data_m1 = assigned_data

        # JSON 응답 반환
        return jsonify({
            'message': 'Location labels assigned successfully'
        }), 200

    except ValueError as e:
        print(f"ValueError: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f"Exception: {e}")
        return jsonify({'error': str(e)}), 500

# ########################################################################## m1_sensor ##########################################################################
@app.route('/m1_load_sensing_data', methods=['POST'])
def m1_load_sensing_data():
    global stored_sensor_data_m1
    try:
        print("센서 데이터 가공중")
        sensor_file = request.files.get('sensor_file')
        if not sensor_file:
            return jsonify({'error': 'No sensor file provided'}), 400

        sensor_data = m1_sensor_data_processor.load_sensing_data(sensor_file)
        sensor_data = m1_sensor_data_processor.process_sensing_data(sensor_data)
        sensor_data = m1_sensor_data_processor.aggregate_sensing_data(sensor_data)
        sensor_data = m1_sensor_data_processor.reorganize_column_names(sensor_data)

        # 메모리에 저장
        stored_sensor_data_m1 = sensor_data
        return jsonify({'message': 'Sensor data loaded successfully'}), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/m1_load_data', methods=['POST'])
def m1_load_data():
    global stored_location_data_m1, stored_sensor_data_m1, stored_merged_data_m1
    try:

        if stored_location_data_m1 is None or stored_sensor_data_m1 is None:
            raise ValueError("저장된 location 또는 sensor 데이터가 없습니다.")
        # CRF와 Trait 파일 확인
        crf_file = request.files.get('crf_file')
        trait_file = request.files.get('trait_file')

        # 추가 데이터 로드
        crf_data = pd.read_csv(crf_file) if crf_file else None
        trait_data = pd.read_csv(trait_file) if trait_file else None

        if trait_data is None or crf_data is None:
            raise ValueError("CRF 또는 Trait 파일이 누락되었습니다.")

        print("CRF 및 Trait 데이터 로드 완료")
        print("Trait Data Head:\n", trait_data.head())

         # 데이터 로드 및 병합 수행
        m1_data_processor.load_data(
            stored_location_data_m1, stored_sensor_data_m1, crf_data, trait_data
        )

        print("Location과 Sensor 데이터 병합 중...")
        m1_data_processor.merge_location_and_sensor()
        print("Location과 Sensor 데이터 병합 완료")

        print("CRF 데이터 처리 중...")
        m1_data_processor.process_crf_data()
        print("CRF 데이터 처리 완료")

        print("Trait 데이터 병합 중...")
        merged_data = m1_data_processor.merge_trait_data()
        print("Trait 데이터 병합 완료:\n", merged_data.head())
        
        print("자해 플래그 데이터 받아오는 중...")
        # JSON 데이터 파싱
        json_data = request.form.get('json_data')
        if not json_data:
            raise ValueError("JSON 데이터가 누락되었습니다.")

        suicide_flags = json.loads(json_data)['suicide_flags']
        print(f"자해 플래그 데이터: {suicide_flags}")

        # 자해 플래그를 데이터프레임으로 변환
        suicide_flags_df = pd.DataFrame(suicide_flags)
        suicide_flags_df['time'] = pd.to_datetime(suicide_flags_df['time'])
        print("자해 플래그 데이터 로드 완료:", suicide_flags_df.head())

        # suicide_flags를 리스트의 튜플 형식으로 변환 (이름, 시간)
        suicide_flags_list = list(suicide_flags_df.itertuples(index=False, name=None))

        
        # 데이터 병합 후 suicide 플래그 설정
        merged_data = m1_data_processor.clean_and_set_suicide_flag(suicide_flags_list)
        print("최종 데이터:", merged_data.head())

        stored_merged_data_m1 = merged_data
        print("데이터 로드 및 병합 완료")
        return jsonify({'message': 'All data loaded and processed successfully'}), 200

    except ValueError as ve:
        print(f"ValueError: {ve}")
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        print(f"Exception: {e}")
        return jsonify({'error': str(e)}), 500


###################################### m1_model ######################################


@app.route('/m1_predict', methods=['POST'])
def m1_predict():
    global stored_merged_data_m1  # 전역 변수 사용

    try:
        # 병합된 데이터 유효성 확인
        if stored_merged_data_m1 is None:
            raise ValueError("병합된 데이터가 없습니다. 데이터를 먼저 로드하세요.")
        if stored_merged_data_m1.empty:
            raise ValueError("병합된 데이터가 비어 있습니다.")

        print("Predicting with the following data:\n", stored_merged_data_m1.head())

        # DataFrame을 임시 파일로 저장하고 경로 반환
        temp_file_path = save_to_temp_file(stored_merged_data_m1)

        try:
            # PredictionHandler 초기화 (임시 파일 경로 전달)
            m1_predictor = saferx.PredictionHandler(
                [temp_file_path], batch_size=16, device='cpu'
            )

        except Exception as e:
            print(f"Preprocessing error: {e}")
            raise ValueError(f"데이터 전처리 중 오류 발생: {e}")

        # 예측 수행
        try:
            predictions = m1_predictor.predict()
            print("예측 완료:", predictions)

        except Exception as e:
            print(f"Prediction error: {e}")
            raise ValueError(f"예측 중 오류 발생: {e}")

        finally:
            # 임시 파일 삭제
            os.remove(temp_file_path)

        # 예측 결과 반환
        return jsonify({
            'message': 'Prediction completed successfully',
            'predictions': predictions.tolist()
        }), 200

    except ValueError as ve:
        print(f"ValueError: {ve}")
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        print(f"Exception: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
