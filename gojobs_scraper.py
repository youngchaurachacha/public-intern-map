import requests
import time
from bs4 import BeautifulSoup
import csv
import math
import re
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_page(page_number):
    """지정된 페이지 번호의 채용 공고 목록 HTML을 가져옵니다."""
    print(f"--- 페이지 목록 스크래핑 시작 (페이지: {page_number}) ---")
    
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
        response = requests.post(api_url, data=payload, timeout=10)
        if response.status_code == 200:
            return response.text
        else:
            print(f"  - [에러] 서버 응답 실패 (상태 코드: {response.status_code})")
            return None
    except requests.exceptions.RequestException as e:
        print(f"  - [에러] 요청 중 예외 발생: {e}")
        return None

def parse_data_from_list(html_content):
    """HTML 목록 페이지에서 채용 공고 기본 정보를 추출합니다."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    total_count = 0
    try:
        total_count_element = soup.select_one('div.left > span:first-child')
        if total_count_element:
            full_text = total_count_element.get_text(strip=True)
            total_count = int(full_text.split(' ')[1])
        else:
            print("  - [경고] 총 게시물 수를 찾지 못했습니다. 0으로 처리합니다.")
            return [], 0
    except Exception as e:
        print(f"  - [에러] 총 게시물 수 파싱 중 예외 발생: {e}")
        return [], 0

    postings = soup.select('#apmTbl > tbody > tr')
    results = []
    for post in postings:
        cells = post.find_all('td')
        if len(cells) != 6 or "검색 결과가 없습니다" in cells[0].get_text():
            continue

        try:
            title_element = cells[1].find('a')
            if not title_element or 'fn_apmView' not in title_element.get('href', ''):
                continue

            href_value = title_element['href']
            params_str = href_value.split('(')[1].split(')')[0]
            params = [p.strip().strip("'") for p in params_str.split(',')]
            
            # fn_apmView의 파라미터가 2개 이상인지 확인
            if len(params) < 2:
                continue

            # 올바른 데이터만 추출
            job_info = {
                'jobsecode': params[0], # '020' 같은 코드 추가
                'empmnSn': params[1],  # 공고 ID
                'title': title_element.get_text(strip=True),
                'organization': cells[2].get_text(strip=True)
            }
            results.append(job_info)
        except Exception as e:
            print(f"  - [에러] 목록 파싱 중 예상치 못한 예외 발생: {e}, 해당 행 건너뜀")
            
    return results, total_count

# Selenium 웹 드라이버를 한번만 실행하기 위해 전역 변수로 설정
driver = None

def setup_driver():
    """Selenium 엣지 드라이버를 설정하고 실행합니다."""
    global driver
    if driver is None:
        print("--- Selenium 엣지 드라이버를 처음 실행합니다. ---")
        options = Options()
        options.add_argument("--headless")  # 브라우저 창을 띄우지 않음
        options.add_argument("--log-level=3") # 콘솔 로그 최소화
        service = Service('msedgedriver.exe') # 프로젝트 폴더의 msedgedriver.exe 사용
        driver = webdriver.Edge(service=service, options=options)

def scrape_detail_page(post_info):
    """Selenium을 사용하여 상세 페이지를 로드하고 근무지역 정보를 가져옵니다. (정확한 URL 파라미터 적용)"""
    print(f"  - 상세 페이지 스크래핑 시작 (ID: {post_info['empmnSn']})")
    
    setup_driver()
    
    # 사용자가 제공한 실제 URL 구조에 맞춰 파라미터 재구성
    # empmnSn -> empmnsn (소문자), selMenuNo, upperMenuNo 추가
    detail_url = f"https://www.gojobs.go.kr/apmView.do?empmnsn={post_info['empmnSn']}&selMenuNo=400&menuNo=401&upperMenuNo="
    
    try:
        driver.get(detail_url)
        
        # 경고창 처리는 이제 필요 없을 가능성이 높지만, 안전을 위해 남겨둠
        try:
            WebDriverWait(driver, 1).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            print(f"    -> ID {post_info['empmnSn']} 에서 여전히 경고창 감지됨: {alert.text}")
            alert.accept()
            return "주소 정보 없음 (경고창)"
        except:
            pass # 경고창이 안 뜨면 정상

        # '근무지역' 정보를 찾음 (최대 10초 대기)
        wait = WebDriverWait(driver, 10)
        # XPath를 사용하여 '근무지역' 텍스트를 포함하는 th 태그를 찾음
        address_th = wait.until(EC.presence_of_element_located((By.XPATH, "//th[contains(text(), '근무지역')]")))
        
        address_td = address_th.find_element(By.XPATH, "./following-sibling::td")
        address_text = address_td.text.strip()
        
        print(f"    -> ID {post_info['empmnSn']} 근무지역 찾음: '{address_text}'")
        return address_text

    except Exception as e:
        print(f"    -> ID {post_info['empmnSn']} 에서 에러 발생: '근무지역'을 찾을 수 없거나 타임아웃.")
        # 디버깅을 위해 현재 페이지의 스크린샷 저장
        driver.save_screenshot(f"error_screenshot_ID_{post_info['empmnSn']}.png")
        print(f"    -> 에러 발생 시점의 스크린샷을 'error_screenshot_ID_{post_info['empmnSn']}.png' 파일로 저장함.")
        return "주소 정보 없음 (에러)"
                
# 프로그램이 끝날 때 드라이버 종료
def close_driver():
    global driver
    if driver:
        print("--- Selenium 웹 드라이버를 종료합니다. ---")
        driver.quit()

def save_to_csv(data_list, filename="gojobs_intern_postings.csv"):
    """추출된 전체 데이터를 CSV 파일로 저장합니다."""
    print(f"\n--- 수집된 데이터를 {filename} 파일로 저장합니다. ---")
    
    if not data_list:
        print("  - 저장할 데이터가 없습니다.")
        return

    with open(filename, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.DictWriter(file, fieldnames=data_list[0].keys())
        writer.writeheader()
        writer.writerows(data_list)
    
    print(f"  - 저장 완료! 총 {len(data_list)}개의 공고가 저장되었습니다.")

if __name__ == "__main__":
    max_pages_to_scrape = 1 # 테스트할 페이지 수
    print(f">>> 나라일터 '인턴' 채용 공고 스크래핑을 시작합니다. (테스트 모드: 최대 {max_pages_to_scrape}페이지) <<<")
    
    all_postings = []
    
    first_page_html = scrape_page(1)
    if not first_page_html:
        print(">>> 스크립트 실행 중단: 첫 페이지를 가져올 수 없습니다.")
    else:
        _, total_post_count = parse_data_from_list(first_page_html)
        
        if total_post_count == 0:
            print(">>> 스크립트 실행 중단: 총 게시물 수를 확인할 수 없어 페이지 계산이 불가능합니다.")
        else:
            total_pages = math.ceil(total_post_count / 10)
            pages_to_scrape = min(total_pages, max_pages_to_scrape)
            
            print(f">>> 총 {total_post_count}개의 게시물, 전체 {total_pages} 페이지 중 {pages_to_scrape} 페이지만 스크래핑합니다. <<<")

            for page in range(1, pages_to_scrape + 1):
                html_content = scrape_page(page) if page > 1 else first_page_html
                if not html_content:
                    continue

                post_list, _ = parse_data_from_list(html_content)
                if not post_list:
                    print(f"  - 페이지 {page}에서 수집된 공고가 없습니다.")
                    continue
                
                for post_info in post_list:
                    address = scrape_detail_page(post_info)
                    
                    full_post_data = {
                        'post_id': post_info['empmnSn'],
                        'title': post_info['title'],
                        'organization': post_info['organization'],
                        'address': address
                    }
                    all_postings.append(full_post_data)
                    time.sleep(0.5) # 서버 부하를 줄이기 위해 각 요청 사이에 0.5초 대기

            if all_postings:
                save_to_csv(all_postings, filename="gojobs_intern_postings_TEST.csv")
            else:
                print(">>> 최종적으로 수집된 데이터가 없습니다.")

    print("\n>>> 스크래핑 작업 완료 <<<")
    close_driver() # 드라이버 종료