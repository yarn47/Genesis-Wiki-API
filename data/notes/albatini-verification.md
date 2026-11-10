# 알바티니 데 메디치 등록 검증

## 기준

- 사용자 자료: 알바티니.zip, Screenshot_20261110_153219~153543 (44장).
- 출시일: 사용자 "2주뒤" → 크리스티나 여제 2025-04-15에서 14일 뒤인 **2025-04-29**.
- 출현작: 사용자 지정 **창세기전3**.
- 창천일섬: 제공된 발현 1/3/5단 140/150/160%를 기준으로 사용자 기존 지시에 따라 노발현 **130%**로 역산.
- 프로필의 이너브레이크는 별도 분류로 확인했으나 현재 입력 스키마에 임의로 추가하지 않음.

## 남은 확인

- 기사의 서약 각성 3성: 153254/153257에서 설명 첫 줄이 위로 잘려 버프 획득 조건을 확인할 수 없음. 확인 가능한 TP 회수 이후 본문만 입력. "스킬로 버프를 얻을 때마다 기사의 서약 1 효과를 얻습니다"가 맞는지 사용자에게 질문한 상태이며, 답변 전에는 추가하지 않음.
- 저스티카·엠프레스로얄 클래스 엠블럼: 모든 제공 클래스 화면에서 설명창이 원형 문양을 가림. 아이콘을 임의 복원하거나 다른 클래스 문양을 사용하지 않고 iconUrl 생략. 설명창을 닫은 클래스 트리 화면 요청 중.
- 기사의 서약 버프 1~4: 툴팁에 지속 표기가 없어 duration 생략. 5~7은 영구 확인. 최대 중첩은 모두 5.

## 대조 사항

- 클래스 연결: 파이터 → 나이트 → 로얄나이트/스톰나이트, 파이터 → 저스티카 → 엠프레스로얄. 공용 스톰나이트 자료 재사용.
- 사일도: TP 전부 소모, 130% + TP당 25%, 치명타 확률은 화면대로 1%.
- 비밀 경호: 2턴, 해제 불가, 3칸 이상 멀어지면 발동하지 않음. 조안의 별도 '경호' 버프와 잘못 연결하지 않음.
- 부활: 크리스티나 여제 동행 조건 유지. 각성 3~6은 40/50/60/70%, 발현 2/4/6은 80/90/100% 및 디버프 해제.
- TP 회수 쿨타임: 4/4/4/3/3/2/2. 가장 긴 스킬 쿨타임 감소는 발현 6에만 존재.
- 긍지의 대가: 받는 피해 15% 증가(감소 아님), 반격 두배. ★2~4 체력 +10/20/30%.
- 임페리얼 아르마다: 대상 체력 70% 이상 물리 관통 증가. 전투에서 치명타가 발생하지 않았을 때만 추가 발동. 6성은 확률 문구 없음.
- 속성 과부하·최상의 상태는 기존 공용 아티팩트 재사용.

## 이미지

- 프론트 public/icons/에 초상화·썸네일·패시브·궁·신규 클래스 패시브/액티브·아티팩트는 원본 크롭으로 저장.
- 초상화/썸네일: 153221, (430,180,970,900), 각각 600×800/420×560.
- 무기: 153508, (1471,286,1796,768) 카드에서 Lv/별/자물쇠만 제거 요청. 가려진 칼끝 복원은 추정.
- imagegen 스킬, 내장 편집 도구 사용. 최종 파일: The-War-Of-Genesis-Mobile-Wiki/public/icons/weapons/imperial_armada.png.
- 최종 프롬프트:

> Use case: precise-object-edit. Image 1 is the edit target, a vertical game weapon card. Remove only the Lv50 label, bottom rarity stars and lower right padlock with its dark square. Reconstruct covered background and the tiny covered sword tip following the existing shape. Preserve the exact sword design, position, proportions, colors, golden brown radiant background, all four frame edges and corner ornaments. No zoom, rotation, redesign, additional sharpening, text or symbols. Output the complete vertical card, opaque background.

## 검증

- SQL 생성: 경고 없이 통과.
- API 데이터 테스트 232개 통과.
- 프론트 빌드, 테스트 6개 및 클래스 연결 테스트 4개 통과.
- 로컬 임시 데이터 연결로 목록·상세·클래스 선택·발현·아티팩트·전용무기 확인. 화면 오류/깨진 이미지 없음. 미등록 클래스 문양은 텍스트 대체 표시.
- 390px 모바일의 기존 상세 헤더 고정 가로 배치로 긴 이름/메타데이터가 좁게 줄바꿈되는 문제는 기존 공통 UI 문제이며 이번 데이터 추가 범위에서는 변경하지 않음.
- 서버 DB 반영·커밋·푸시·배포는 하지 않음.
