from flask import Flask, jsonify, render_template
import pandas as pd

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

@app.route('/')
def index():
    return render_template('index.html')

postings_data = []
try:
    df = pd.read_csv('geocoded_postings.csv')
    df.dropna(subset=['latitude', 'longitude'], inplace=True)
    postings_data = df.to_dict(orient='records')
    print(f"[정보] {len(postings_data)}개의 유효한 위치 데이터 로드 완료.")
except Exception as e:
    print(f"[ERROR] 데이터를 로드하는 중 심각한 에러 발생: {e}")

@app.route('/api/postings')
def get_postings():
    response = jsonify(postings_data)
    response.headers['Cache-Control'] = 'public, max-age=600'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)