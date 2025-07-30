import requests
import time
from bs4 import BeautifulSoup 

# --- scrape_page 함수 (디버깅 강화) ---
def scrape_page(page_number):
    """지정된 페이지 번호의 채용 공고를 가져옵니다."""
    print(f"--- scrape_page 함수 실행 (페이지: {page_number}) ---")
    
    api_url = "https://www.gojobs.go.kr/apmList.do"
    payload = {
        'flag': '', 'searchDetail': '', 'searchJobsecode': '020', 'searchEmpmnsecode': '',
        'recentEmploy': '', 'empmnsn': '0', 'employStep': '', 'prgl': 'apmList',
        'searchWorkareaname': '전체', 'areanm': '전국', 'menuNo': '401', 'selMenuNo': '400',
        'upperMenuNo': '', 'wd': '', 'isShowBtn': 'N', 'searchSelectninsttnm': '',
        'searchKeyword': '인턴', 'detailKeyword': '', 'searchInsttsecode': '',
        'searchType': '', 'serachAreaClassCd': '00000', 'searchWorkareacode': '00000',
        'searchSdate': '', 'searchEdate': '', 'searchOrdr': '',
        'pageIndex': str(page_number)
    }
    
    try:
        print(f"  - 서버에 POST 요청을 보냅니다...")
        response = requests.post(api_url, data=payload, timeout=10) # 10초 타임아웃 추가
        
        print(f"  - 서버로부터 응답을 받았습니다. 상태 코드: {response.status_code}")
        if response.status_code == 200:
            print(f"  - 요청 성공! HTML 내용을 반환합니다.")
            return response.text
        else:
            print(f"  - 요청 실패! None을 반환합니다.")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"  - 요청 중 심각한 에러 발생: {e}")
        return None

# --- parse_data_from_list 함수는 이전과 동일 ---
def parse_data_from_list(html_content):
    """HTML 목록 페이지에서 채용 공고 상세 정보를 추출합니다."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # <tbody> 안에 있는 모든 <tr> (table row) 태그를 선택합니다.
    # 각 <tr> 태그가 하나의 채용 공고에 해당합니다.
    postings = soup.select('#apmTbl > tbody > tr')
    
    results = []
    for post in postings:
        # 각 tr 안에 있는 모든 td (table data) 태그를 리스트로 가져옵니다.
        # td 태그는 각 칼럼(번호, 공고명, 기관명...)에 해당합니다.
        cells = post.find_all('td')
        
        # 정상적인 공고 줄은 6개의 칼럼(td)을 가집니다.
        # 구조가 다른 행(ex: 빈 행)은 건너뛰기 위한 안전장치입니다.
        if len(cells) == 6:
            try:
                # 각 칼럼 순서에 맞게 데이터를 추출합니다.
                number = cells[0].get_text(strip=True)
                title_element = cells[1].find('a') # 공고명은 <a> 태그 안에 있음
                organization = cells[2].get_text(strip=True)
                start_date = cells[3].get_text(strip=True)
                end_date = cells[4].get_text(strip=True)
                views = cells[5].get_text(strip=True)
                
                # title_element가 존재하는지 확인 (간혹 없는 경우가 있을 수 있음)
                if title_element:
                    title = title_element.get_text(strip=True)
                    href_value = title_element['href']
                    
                    # href에서 고유 ID 추출
                    params_str = href_value.split('(')[1].split(')')[0]
                    params = [p.strip().strip("'") for p in params_str.split(',')]
                    post_id = params[1]
                else:
                    title = "N/A"
                    post_id = "N/A"

                # 추출한 정보들을 딕셔너리 형태로 정리
                job_info = {
                    'number': number,
                    'title': title,
                    'organization': organization,
                    'start_date': start_date,
                    'end_date': end_date,
                    'views': views,
                    'post_id': post_id
                }
                results.append(job_info)

            except Exception as e:
                print(f"파싱 중 에러 발생: {e}, 해당 행 건너뜀")

    return results


# --- 메인 실행 부분 (디버깅 강화) ---
print(">>> 스크립트 실행 시작 <<<")

# 1페이지만 테스트
html = scrape_page(1)

if html:
    # 완성된 파싱 함수 호출
    data_list = parse_data_from_list(html)
    
    print("--- 1페이지 파싱 결과 ---")
    if data_list:
        # 추출된 데이터를 보기 좋게 출력
        for item in data_list:
            print(item)
    else:
        print("파싱된 데이터가 없습니다.")