# 공공인턴지도 (Public Intern Map)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

나라일터(gojobs.go.kr)에 올라오는 공공기관 인턴 채용 공고를 수집하여 지도 위에 시각화하는 오픈소스 프로젝트입니다.

## 🌟 주요 기능 (Features)

- **채용 공고 스크래핑**: `requests` 및 `BeautifulSoup4`를 사용하여 나라일터의 인턴 공고 목록을 주기적으로 수집합니다.
- **데이터 정제**: 수집한 HTML에서 공고명, 기관명, 접수 기간 등의 핵심 정보를 추출합니다.
- **(구현 예정) 지도 시각화**: 수집한 데이터를 카카오맵/네이버지도 API와 연동하여 기관 위치를 지도에 표시합니다.
- **(구현 예정) 필터링 및 검색**: 기관명, 근무지, 키워드 등으로 원하는 공고를 쉽게 찾을 수 있는 기능을 제공합니다.

## 💻 기술 스택 (Tech Stack)

- **Backend**: Python
- **Crawling**: `requests`, `BeautifulSoup4`
- **(Planned) Database**: `SQLite` or `PostgreSQL`
- **(Planned) API**: `Flask` or `FastAPI`
- **(Planned) Frontend**: `HTML/CSS`, `JavaScript`, `Kakao/Naver Map API`

## 🌟📈 앞으로의 개발 계획 (To-Do)
- [ ] 데이터베이스 모델 설계 및 연동
- [ ] 지도 API 연동 및 공고 위치 마커 표시 기능 구현
- [ ] 간단한 웹 프론트엔드 구축 (Flask/FastAPI 기반)
- [ ] 공고 데이터 자동 업데이트를 위한 스케줄러(APScheduler 등) 적용