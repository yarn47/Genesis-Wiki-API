# 카나 밀라노비치 입력 검증

- 출처: 사용자 제공 카나.zip, Screenshot_20261105_175837~180222 (43장).
- 출시일: 이전 실버 2025-02-04에서 2주 뒤인 2025-02-18. 출현작: 서풍의 광시곡.
- 사용자 요청에 따라 노발현 크림슨 인페르노는 기절 제외. 발현 1/3/5 직격 150/155/160%, 주변 90/95/100%의 단계 차이로 기본 145/85%를 산출했다. 기본 원문이 아닌 추정 수치다.
- 지옥불 지대 생성 확률은 발현 1/3에서 30%로 같아 기본도 30% 유지. 처치 시 쿨타임 감소는 발현 3부터 반영.
- 각성 3 패시브에는 추가 행동 없음. 각성 4/5/6 쿨타임 4/3/3턴, 발현 2/4/6 추가 행동 1/1/2회.
- 텐션 업 1~4의 피해 감소는 마법 피해에 한정, 5~7은 전체 피해. 1~4의 지속시간은 팝업에 없으므로 미지정.
- 기존 거너/건슬링어/스핏파이어/스페셜리스트와 공용 아티팩트 초과 장전기/치밀한 준비/바람 걸음 재사용.
- 카나의 건슬링어→스페셜리스트 연결은 프런트 트리 해석에서 적용. 제인 쇼어의 에이전트→스페셜리스트 원본은 보존.
- 초상화와 아이콘은 원본 크롭. .local-reference/kana에 원본 보존(비추적). 초상화는 175859의 (550,155,1090,875), 목록/상세 동일 3:4 구도.
- 무기 카드만 imagegen 편집: Lv50/별/자물쇠 제거, 가려진 영역 복원은 추정. 최종 프런트 경로 public/icons/weapons/crimson_revolution.png.
- 편집 프롬프트: Edit this exact game weapon card. Remove ONLY the lower left Lv50 text and stars and lower right padlock UI. Seamlessly reconstruct the brown gold background under those overlays. Preserve the exact red pistol, all its details, position, size, aspect ratio, gold border and background. Do not redesign or add anything.
- 운영 DB 적용/커밋/푸시/배포는 수행하지 않음.
- 검증: SQL 생성 경고 없음, API 테스트 203개 및 프런트 테스트 9개 통과, 프런트 빌드 통과. 로컬 화면에 임시 응답을 연결해 목록/상세 초상화·트리·무기 표시 확인, 브라우저 실행 오류 및 깨진 이미지 0개. 운영 API는 변경하지 않았다.
