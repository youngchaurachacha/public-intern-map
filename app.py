from flask import Flask, jsonify, render_template
import pandas as pd
import os
from dotenv import load_dotenv

# .env 파일에서 환경변수를 가장 먼저 불러옴
load_dotenv()

app = Flask(__name__)
# 한글을 ASCII로 인코딩하지 않고, Content-Type 헤더에 charset=utf-8을 포함시킴
app.config['JSON_AS_ASCII'] = False

# --- 데이터 로딩 ---
postings_data = []
try:
    df = pd.read_csv('geocoded_postings.csv')
    # 위도 또는 경도가 없는 행은 지도에 표시할 수 없으므로 미리 제거
    df.dropna(subset=['latitude', 'longitude'], inplace=True)
    postings_data = df.to_dict(orient='records')
    print(f"[정보] {len(postings_data)}개의 유효한 위치 데이터 로드 완료.")
except FileNotFoundError:
    print("[경고] geocoded_postings.csv 파일을 찾을 수 없습니다. API가 빈 데이터를 반환합니다.")
except Exception as e:
    print(f"[에러] 데이터를 로드하는 중 예외 발생: {e}")

# --- 모든 서버 응답에 공통 헤더를 추가하는 부분 ---
@app.after_request
def add_common_headers(response):
    # 브라우저의 MIME 타입 스니핑 공격을 방지 (보안)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

# --- 라우트 (페이지 및 API) ---
@app.route('/')
def index():
    # .env 파일에서 KAKAO_MAP_KEY 값을 읽어와서 HTML 템플릿에 전달
    kakao_key = os.getenv('KAKAO_MAP_KEY')
    return render_template('index.html', kakao_api_key=kakao_key)

@app.route('/api/postings')
def get_postings():
    response = jsonify(postings_data)
    # API 응답을 10분(600초) 동안 캐시하도록 설정 (성능)
    response.headers['Cache-Control'] = 'public, max-age=600'
    return response

if __name__ == '__main__':
    # 개발용 서버 실행. debug=True는 코드 수정 시 자동 재시작
    app.run(host='0.0.0.0', port=5000, debug=True)