from flask import Flask, request, jsonify
import saferx
import pandas as pd
import torch
import numpy as np

app = Flask(__name__)

m2_location_processor = saferx.M2LocationProcessor()
m2_sensor_data_processor = saferx.M2SensorDataProcessor()
data_processor = saferx.M2DataProcessor()

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
predictor = saferx.Predictor(device)




###################################### m2_data ######################################

###################################### m2_location ######################################
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

###################################### m2_sensor######################################

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



###################################### m2_crf ######################################



@app.route('/load_data', methods=['POST'])
def load_data():
    global stored_location_data, stored_sensor_data
    try:
        # 저장된 location 및 sensor 데이터 사용
        if stored_location_data is None or stored_sensor_data is None:
            raise ValueError("저장된 location 또는 sensor 데이터가 없습니다.")

        # 요청에서 추가 파일(CRF, trait) 추출
        crf_file = request.files.get('crf_file')
        trait_file = request.files.get('trait_file')

        # 추가 데이터 로드
        crf_data = pd.read_csv(crf_file) if crf_file else None
        trait_data = pd.read_csv(trait_file) if trait_file else None

        print("CRF 및 Trait 데이터 로드 완료")

        # 모든 데이터 처리 및 로드
        data_processor.load_data(
            stored_location_data, stored_sensor_data, crf_data, trait_data
        )

        return jsonify({'message': 'All data loaded successfully'}), 200

    except ValueError as ve:
        print(f"ValueError: {ve}")
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        print(f"Exception: {e}")
        return jsonify({'error': str(e)}), 500









@app.route('/merge_location_and_sensor', methods=['POST'])
def merge_location_and_sensor():
    try:
        data_processor.merge_location_and_sensor()
        return jsonify({'message': 'Location and sensor data merged successfully'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/process_crf_data', methods=['POST'])
def process_crf_data():
    try:
        data_processor.process_crf_data()
        return jsonify({'message': 'CRF data processed successfully'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/merge_trait_data', methods=['POST'])
def merge_trait_data():
    try:
        merged_data = data_processor.merge_trait_data()
        return jsonify({'message': 'Trait data merged successfully', 'merged_data': merged_data.to_dict()}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/preprocess_data', methods=['POST'])
def preprocess_data():
    try:
        data = request.get_json()
        data_df = pd.DataFrame(data)
        preprocessed_data = saferx.ModelDataProcessor.preprocess_data(data_df)
        return jsonify({'message': 'Data preprocessed successfully', 'preprocessed_data': preprocessed_data.to_dict()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

###################################### m2_model ######################################
@app.route('/predict', methods=['POST'])
def predict():
    try:
        data_file = request.files.get('data_file')
        if not data_file:
            return jsonify({'error': 'No data file provided'}), 400

        data_loader = predictor.preprocess_data(data_file)
        predictions = predictor.predict(data_loader)
        return jsonify({'message': 'Prediction completed successfully', 'predictions': predictions.tolist()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500



###################################### m1_data ######################################


###################################### m1_model ######################################

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
