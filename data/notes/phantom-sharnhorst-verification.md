# 괴도 샤른호스트 등록 확인

검증: SQL 생성 경고 없음, API 테스트 207개·프런트엔드 테스트 9개 통과, 프런트엔드 빌드 통과. 신규 이미지 참조 누락 없음. 로컬 테스트 데이터로 목록/상세·클래스 3종 선택·발현 6단 아티팩트/패시브·무기 화면 확인, 브라우저 오류 없음. 운영 데이터 변경·커밋·푸시·배포는 하지 않음.

- 원본: 괴도.zip, Screenshot_20261105_182843~183153, 총 48장.
- 출시일: 사용자 지시에 따라 카나(2025-02-18)에서 2주 뒤인 2025-03-04. 출현작: 서풍의 광시곡.
- 신월환영참: 발현 1/3/5단 230/240/250%. 노발현은 사용자 지시에 따라 동일 10%p 격차로 220% 적용. 원본 기본값 직접 확인은 아님.
- 고유 패시브: 각성 3~6성 및 발현 2/4/6단을 개별 입력. 버프 복사는 각성 6성부터, 기만 스킬의 집중 획득은 발현 4단부터.
- 화신 생성의 상세 툴팁은 자료에 없음. 선택지 이름만 등록하고 생성 위치·조건은 추정하지 않음. 화신 남기기와 화신 설명은 제공된 자료로 등록.
- 화신은 원본의 붉은 상태효과 헤더에 따라 디버프 사전으로 분류.
- 신경독은 전용 툴팁 3~6성에 공격력/주문력 -10%가 있지만 일반 툴팁에는 없음. 일반 신경독과 신경독 (전용)을 별도 등록. 괄호는 사이트 내 구분용이며 게임 원문 이름은 모두 신경독.
- 흑영살진은 기존 한조용 설명이 '한조에게 선제 공격 허용'으로 지정되어 있음. 기존 데이터를 덮어쓰지 않고 '시전자와 전투 시'인 괴도 버전을 흑영살진 (괴도)로 분리.
- 클래스 연결: 로그→킬러→섀도우킬러/섀도우디센던트, 로그→트릭스터→일루전위버.
- 아티팩트 순서: 바람 걸음, 학살의 징표, 위기 대응. 앞의 두 개는 공용 데이터 재사용.

## 이미지

초상화와 모든 클래스·스킬·아티팩트 아이콘은 원본 크롭. 목록과 상세 초상화는 동일 3:4 원본 영역 사용.
무기 카드만 내장 이미지 편집 도구 사용. 가려진 배경 복원은 추정이며 게임 원본이 아님.
저장: 프런트엔드 public/icons/weapons/moonfall_blades.png.
최종 편집 프롬프트:

> Use case: precise-object-edit. Edit this game weapon card only by removing the bottom-left Lv 50 and stars and bottom-right lock UI overlays, reconstructing their underlying gold background. Keep the two blue crescent daggers EXACTLY unchanged, same positions, shape, proportions, colors, golden background and outer ornate border. No new text or objects. Preserve portrait aspect ratio.
