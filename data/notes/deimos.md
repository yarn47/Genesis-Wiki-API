# 혼돈의 데이모스

- 출현작: 창세기전2 (사용자 확인). 출시일: 정의의 디에네 2025-06-10에서 2주 뒤인 2025-06-24.
- 제공 스크린샷 71장 기준으로 패시브 7단계, 클래스 6개, 아티팩트 3종 각 4단계, 전용무기 6단계를 등록.
- 기본 필살기 스크린샷은 없음. 사용자 공통 지시에 따라 발현 1·3·5단 피해 130/140/150%의 격차로 기본 피해 120%를 입력. 공포 확률은 1·3단에서 동일한 40%를 유지하고 TP 회복은 없음.
- 암흑혈/피의 교감/암흑 주입은 화면에 단계 번호가 없지만 패시브 단계별 수치가 다르므로 연결 정확성을 위해 1~7 레벨로 관리.
- 사망 방지 효과는 부활, 자비의 성녀, 결정화 등 치명적 피해 시 일시적으로 무적이 되는 효과를 뜻함.
- 다크메이지는 기존 공용 데이터 재사용. 기본 부모 위치는 변경하지 않으며 이 캐릭터에서는 화면의 단일 1티어 부모 보정으로 애콜라이트에 연결.
- 전용무기 혼돈의 균열 1~6은 제인 쇼어의 레벨 없는 혼돈의 균열(방어력/저항력 -25%)과 다른 효과. 별도 이름 '혼돈의 균열 (카오스 블러드)'에 원문 레벨 이름을 지정해 충돌 방지.
- 무기 카드: 내장 이미지 편집 도구로 Lv/별/자물쇠만 제거하도록 요청. UI에 가린 무기 끝은 추정 복원. 나머지 이미지는 원본 크롭.
- 검증: 데이터 생성 검증 및 249개 테스트, 프론트 빌드 통과. 로컬 API 모의 응답으로 목록/상세/클래스 6개/발현/아티팩트/무기 이미지 누락 및 실행 오류 없음. 기존 공통 상세 상단 레이아웃은 390px 모바일에서 사진과 텍스트가 가로 배치되어 텍스트가 좁고 일부 잘림. 이번 데이터 등록과 별개의 공통 UI 수정 사항으로 남김.
- 무기 편집 프롬프트: Remove ONLY bottom-left Lv50 text and rarity stars and bottom-right lock icon with its square backdrop. Restore gold-brown background locally and infer only the tiny weapon tip covered by UI. Preserve original weapon design, position, proportions, colors, jewel, spikes, whole shaft, frame and all four card borders. No redesign, no zoom, no rotation, no extra sharpening.
