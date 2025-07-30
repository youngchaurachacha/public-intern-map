import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time

# Nominatim 지오코더 초기화 (OpenStreetMap 기반의 무료 서비스)
# user_agent는 식별을 위한 아무 이름이나 넣으면 된다.
geolocator = Nominatim(user_agent="public-intern-map")

# 너무 빠른 속도로 요청하면 차단될 수 있으므로, 요청 사이에 1초의 지연을 둔다.
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

def get_coordinates(address):
    """주소를 입력받아 (위도, 경도) 튜플을 반환합니다."""
    # 주소가 없거나, '전국' 처럼 특정할 수 없는 경우는 처리하지 않음
    if not address or address.strip() == '전국':
        print(f"  - 스킵: '{address}' (좌표를 특정할 수 없는 주소)")
        return None, None
        
    try:
        # 주소에 '대한민국'을 추가하면 더 정확한 결과를 얻을 수 있다.
        location = geocode(f"대한민국 {address}")
        if location:
            print(f"  - 변환 성공: '{address}' -> ({location.latitude}, {location.longitude})")
            return location.latitude, location.longitude
        else:
            print(f"  - 변환 실패: '{address}' (해당 주소를 찾을 수 없음)")
            return None, None
    except Exception as e:
        print(f"  - 에러 발생: '{address}' 처리 중 예외 발생 - {e}")
        return None, None

def main():
    """CSV 파일을 읽어 주소를 좌표로 변환하고, 여러 근무지를 개별 행으로 분리하여 새 파일로 저장합니다."""
    input_filename = 'gojobs_intern_postings_TEST.csv'
    output_filename = 'geocoded_postings.csv'
    
    print(f">>> '{input_filename}' 파일의 주소를 좌표로 변환합니다. <<<")
    
    try:
        df = pd.read_csv(input_filename)
    except FileNotFoundError:
        print(f"[에러] '{input_filename}' 파일을 찾을 수 없습니다. 스크래핑을 먼저 실행하세요.")
        return

    # 변환된 데이터를 저장할 새로운 리스트
    new_rows = []

    # DataFrame의 각 행을 순회
    for index, row in df.iterrows():
        # address가 비어있거나 문자열이 아닌 경우를 대비
        if not isinstance(row['address'], str):
            continue

        # 주소를 쉼표(,) 기준으로 분리
        addresses = row['address'].split(',')
        
        print(f"\n-> 처리 중인 공고: {row['title']}")
        # 분리된 각 주소에 대해 지오코딩 시도
        for address in addresses:
            cleaned_address = address.strip() # 주소 앞뒤의 공백 제거
            if not cleaned_address:
                continue

            lat, lon = get_coordinates(cleaned_address)

            # 좌표 변환에 성공한 경우에만 새 데이터 행을 생성
            if lat is not None and lon is not None:
                new_row = row.to_dict() # 기존 행의 모든 정보를 복사
                new_row['address'] = cleaned_address # 주소를 분리된 개별 주소로 교체
                new_row['latitude'] = lat
                new_row['longitude'] = lon
                new_rows.append(new_row)
    
    # 새로 생성된 행 리스트를 새로운 DataFrame으로 변환
    if not new_rows:
        print("\n[경고] 좌표로 변환할 수 있는 주소가 하나도 없습니다.")
        return
        
    final_df = pd.DataFrame(new_rows)
    
    # 결과 DataFrame을 새로운 CSV 파일로 저장
    final_df.to_csv(output_filename, index=False, encoding='utf-8-sig')
    
    print(f"\n>>> 좌표 변환 완료! 총 {len(final_df)}개의 위치 데이터가 '{output_filename}' 파일에 저장되었습니다. <<<")
    
if __name__ == '__main__':
    main()