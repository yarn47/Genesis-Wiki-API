# 크리스티나 여제 등록 확인

## 입력 근거

- 크리스티나.zip의 Screenshot_20261110_151526~151948, 총 39장.
- 출시일: 이자벨(2025-04-01)에서 2주 뒤인 2025-04-15. 출현작: 창세기전3.
- 전설 / 지성의결정체 / 게이시르. 에스겔력 1250년, 166cm, CV 김하루.
- 분류 '이너브레이크'는 소속과 다른 항목이므로 현재 별도 필드 없이 이 기록에 보존.
- 각성 3~6 및 발현 2/4/6 패시브 모두 원본 확인. 지원 사격 시점은 각성: 전투 공격을 당한 후, 발현 2/4: 전투 준비 단계, 발현 6: 적이 공격하기 전.
- 여제의 인장 1~4는 2턴, 5~7은 3턴 및 버프 해제 면역. 체력 회복은 각성 6부터.
- 궁 발현 1/3/5의 피해 100/110/120%, 추가 피해 확률 40/45/50%. 사용자 공통 지시에 따라 노발현은 90%, 35%로 역산. 추가 피해 계수 50%와 멍해짐 2턴 유지. 노발현 원본을 확인한 값은 아님.
- 멍해짐의 '호위 불가'를 151633 및 151623에서 확인하여 기존 공용 설명에 보완.
- 트리: 거너→건슬링어→에이스/스페셜리스트, 거너→임페리얼거너→엠프레스거너.
- 스페셜리스트의 공용 부모 에이전트는 변경하지 않음. 기존 화면의 부모 보정이 크리스티나에도 적용됨을 회귀 테스트로 확인.
- 아티팩트: 초과 장전기 / 초기 철갑 탄창 / 치밀한 준비. 사진의 1성과 기존 공용 데이터가 일치해 재사용. 상위 단계는 기존 등록 자료 기준.
- 전용무기 로얄 버밀리온: 전용 황가의 특권은 4성부터 탄환 최대치 +2, 일반 자동 연사는 모든 단계 +1.
- 무기 추가타 확률 25/40/55/70/85%, 6성은 확정 발동. 추가타 계수 30% 고정.
- 황가의 특권 버프는 최대 중첩 3, 해제 불가. 지속 턴 표시는 없어 임의 입력하지 않음.
- 현재 캐릭터 스탯은 장비 등의 영향을 받으므로 등록하지 않음.

## 이미지

- 초상화와 스킬은 원본 크롭. 목록/상세는 151529의 (425,260,875,860) 동일 3:4 구도로 420×560 / 600×800.
- 클래스 엠블럼은 151650의 비선택 원형 노드. 패시브/스킬은 151656 및 151907 획득 스킬 타일.
- 고유 패시브/궁은 151620의 타일.
- 무기 카드만 imagegen 스킬의 내장 도구 편집 모드 사용. 글자에 가린 손잡이 끝과 배경 복원은 추정.
- 최종 저장: /Users/choecheolin/Documents/WorkSpace/The-War-Of-Genesis-Mobile-Wiki/public/icons/weapons/royal_vermilion.png
- 최종 프롬프트:

> Use case: precise-object-edit. Image 1 is the edit target, a vertical game weapon card. Remove only the Lv 50 text, bottom rarity stars, and lower-right padlock with its dark square. Fill those small regions with matching golden brown background; infer only the weapon grip tip obscured by the text. Preserve exactly the revolver design, position, proportions, colors, gold rectangular frame and corner decorations. No redesign, rotation, enlargement or global sharpening. Output one complete vertical card with all four frame edges, no text or UI symbols. Opaque background.

## 검증 및 후속 사항

- SQL 생성 경고 없음. 데이터 테스트 225개 통과.
- 프런트 빌드, 일반 테스트 6개 및 클래스 연결 테스트 4개 통과.
- 로컬 모의 API 데이터로 목록/상세, 신규 클래스 2종과 스페셜리스트, 발현 아티팩트 3개 및 무기 표시 확인. 운영 DB 미반영.
- 브라우저 오류/이미지 누락 없음.
- 모바일 390px에서 문서 가로 넘침은 없으나 기존 상세 헤더의 고정 너비 초상화 옆에 정보가 좁게 배치되어 이름·정보 줄바꿈이 과도함. 별도 반응형 레이아웃 개선 필요. 이번 등록에서 공통 UI 레이아웃은 변경하지 않음.
- 커밋·푸시·배포하지 않음.

