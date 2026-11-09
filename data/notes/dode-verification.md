# 에스테 도데 등록 확인

## 출처와 입력 기준

- 도데.zip의 Screenshot_20261109_183326~183636, 총 40장.
- 출시일: 사용자 지시 '2주'에 따라 괴도 샤른호스트(2025-03-04) 다음인 2025-03-18.
- 출현작: 서풍의 광시곡. 소속: 게이시르 / 이너브레이크.
- 헤도닉 그랩: 발현 1/3/5단은 헤도닉 그랩 5/6/7, 해제 시 주문력의 100/120/140% 고정 피해.
- 노발현은 사용자 공통 지시에 따라 20%p 격차로 헤도닉 그랩 4, 80%를 적용했다. 기본 화면을 직접 확인한 값은 아니다. 1~3레벨은 자료가 없어 만들지 않았다.
- 고유 패시브: 각성 3~6 및 발현 2/4/6 개별 입력. 위상 도약 복귀 주문력 증가는 각성 4부터, TP 회수 쿨타임은 4/4/4/3/3/2/2.
- 클래스 연결: 메이지→위자드→다크위자드/플로리스트, 메이지→차밍메이지→드림위버.
- 매스 힙너시스는 사진 표기를 그대로 사용했다.
- 아티팩트 순서: 속성 과부하 / 최상의 상태 / 마력 파동. 앞의 두 개는 기존 공용 데이터 재사용.
- 마력 파동은 최대 4중첩, 주문력 10/15/20/25% 증가. 사진에 별도 지속 턴이 없어 생략했다.
- 전용무기 심리적 지배: 사거리 증가는 4성부터 2턴, 6성은 3턴. 일반 강박증에는 사거리 증가·추가타 강화·받는 피해 감소가 없다.
- 사진에 찍힌 현재 캐릭터 능력치는 기준 상태가 달라 별도 등록하지 않았다.

## 서버 반영 순서

이너브레이크를 faction/sub_faction ENUM 끝에 추가하는 019 마이그레이션 포함.
추후 배포 시 DB 백업 → 마이그레이션 → 서버 코드 배포 → 데이터 동기화 순서가 필요하다.
이번 작업에서는 커밋·푸시·서버 데이터 반영·배포를 하지 않았다.

## 검증

- SQL 생성 경고 없음, 데이터 테스트 213개 통과.
- 프런트엔드 빌드 및 테스트 9개 통과.
- 새 소속을 포함한 서버 코드 컴파일 성공. 전체 JVM 테스트는 22개 중 DB 인증이 필요한 contextLoads 1개 실패, 나머지 21개 통과.
- DB 연결 없는 DTO 테스트를 별도로 재실행해 통과했다. 신규 이미지 참조 15개 모두 파일 존재 확인.
- 로컬 테스트 데이터로 목록/상세, 신규 클래스 3종 선택, 발현 6단 아티팩트·패시브, 무기 화면을 확인했다. 브라우저 오류 및 이미지 로딩 실패 없음.
- 로컬 미리보기는 운영 DB 검증이 아니며 019 마이그레이션 실제 적용은 배포 단계에 남아 있다.

## 이미지

- 초상화·클래스·스킬·아티팩트는 원본 크롭, AI 재작화 없음.
- 초상화 183329의 (550,180,1075,880) 동일 3:4 영역 → 목록 420×560 / 상세 600×800.
- 클래스 엠블럼은 183515의 선택되지 않은 노드를 사용했다.
- 무기만 내장 이미지 편집 도구(imagegen)로 Lv50·별·잠금 표시 제거. 글자에 가린 손잡이 끝과 배경 복원은 추정이다.
- 저장 위치: 프런트엔드 public/icons/weapons/lure_butterfly.png.
- 최종 편집 프롬프트:

> Use case: precise-object-edit. Edit target: supplied vertical game weapon card. Remove ONLY bottom-left Lv50 text and six stars, and bottom-right padlock with its dark square. Fill these small areas with surrounding gold-brown background and minimally reconstruct the red staff tip occluded by text. Preserve the exact weapon design, butterfly cage, colors, placement, scale, golden frame and all four card edges. No redesign, rotation, zoom or overall sharpening. Return the complete vertical card with original proportions, no added text.
