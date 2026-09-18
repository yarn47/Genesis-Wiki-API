# 위키 데이터

게임 데이터를 JSON으로 관리하고 `scripts/db-sync.sh`로 서버 DB에 반영합니다.
여기 있는 항목은 **이 파일이 원본**입니다. 관리자 화면에서 같은 항목을 고쳐도 다음 반영 때 JSON 내용으로 덮어씁니다.

## 반영

```bash
ssh vultr
cd ~/apps/genesis-API && git pull && ./scripts/db-sync.sh
```

DB 구조가 바뀌는 커밋(`db/migrations/`에 파일 추가)이 있으면 순서가 중요합니다.

```bash
git pull
./scripts/db-migrate.sh   # 아직 적용 안 된 마이그레이션만 적용 (schema_migrations에 기록)
./deploy.sh               # 백엔드 재배포 (엔티티가 새 컬럼을 요구하므로 마이그레이션 뒤에)
./scripts/db-sync.sh      # 데이터 반영
```

- 반영 전 DB 전체를 `~/db-backups/`에 백업 (최근 30개 보관)
- 하나의 트랜잭션으로 반영 → 중간에 에러가 나면 아무것도 바뀌지 않음
- 이름 기준으로 추가/갱신하므로 여러 번 실행해도 결과 동일
- `./scripts/db-sync.sh --dry-run` 은 생성될 SQL만 출력 (로컬에서는 `python3 scripts/gen_sql.py`)

## 파일

| 경로 | 내용 |
|---|---|
| `tags.json` | 태그 목록 `{ "name", "color" }` (color: gray/red/orange/yellow/green/blue/purple) |
| `buffs/*.json` | 버프 (파일은 캐릭터별 등 자유롭게 나눔, 이름은 전체에서 중복 불가) |
| `debuffs/*.json` | 디버프 (버프와 같은 형식) |
| `classes/*.json` | 클래스 (클래스 계열별 파일, 이름은 전체에서 중복 불가) |
| `weapons/*.json` | 전용무기 (이름은 전체에서 중복 불가) |
| `characters/*.json` | 캐릭터 (클래스·전용무기는 이름으로 연결) |

### 버프/디버프 형식

```json
[
  {
    "name": "아찔한 회피",
    "description": "레벨 없는 버프의 효과 텍스트",
    "duration": 2,
    "maxStack": 3,
    "tags": ["해제 불가"]
  },
  {
    "name": "아브라소",
    "tags": ["해제 불가"],
    "levels": [
      { "level": 1, "duration": 1, "maxStack": 1, "effect": "공격력 [+30%]{red}. ..." }
    ]
  }
]
```

- `levels`가 있으면 레벨 버프, 레벨 이름은 생략 시 `"{name} {level}"`
- `iconUrl`을 생략하면 기존 아이콘을 유지
- 지속/중첩/해제 불가는 본문에 쓰지 않고 `duration`/`maxStack`/`tags`로 입력
- `duration`: 턴 수 또는 `"영구"` (DB에는 -1로 저장), 게임에 지속 표시가 없으면 생략

### 클래스 형식

```json
{
  "name": "씨프",
  "tier": 2,
  "parent": "로그",
  "weaponType": "쌍수단검",
  "defenseType": "미디엄",
  "attackRange": 1,
  "moveRange": 4,
  "description": "클래스 설명",
  "attackType": "관통",
  "passive": { "name": "잠행", "lv1": "...[잠행 1]{green}...", "lv2": "...[잠행 2]{green}...", "iconUrl": "/icons/classes/passive/thief.png" },
  "skills": [
    { "name": "자도섬", "tpCost": 1, "range": [1, 1], "area": "단일", "allowedWeapon": "쌍수단검", "cooldown": 2,
      "tags": ["근거리", "TP 제거", "전투"], "iconUrl": "/icons/skills/jadoseom.png",
      "effect": "적을 공격해 공격력의 [130%]{red}만큼 ..." }
  ]
}
```

- 1티어는 `parent` 없음, 2·3티어는 바로 위 티어 클래스 이름 (계열 구조는 모든 캐릭터 공통)
- `defenseType`: 라이트/미디엄/헤비
- 아이콘 파일은 프론트 저장소 `public/icons/`에 두고 `/icons/...` 경로로 연결
- `attackType`: 클래스 기본 공격 타입 (관통/타격 등). 스킬이 다를 때만 스킬에 `attackType`
- `skills`: 액티브 스킬, 배열 순서 = 습득 순서. (클래스, 스킬 이름) 기준으로 추가/갱신
  - `tpCost`: 게임에 `TP -`면 생략 / `range`: `[최소, 최대]` 또는 `"자신"`(0-0으로 저장)
  - `allowedWeapon`: 게임에 "허용 무기" 표시가 있을 때만 / `tags`: tags.json에 있는 스킬 태그
- 체력·공격력 등 수치는 아직 JSON으로 관리하지 않음 (반영 시 건드리지 않음)

### 전용무기 형식

```json
{
  "name": "라 사바흐",
  "weaponType": "쌍수단검",
  "grade": "전설",
  "iconUrl": "/icons/weapons/la_sabah.png",
  "extraStats": "치명타 확률 +10~15%, 물리 관통 +10~15% (각성 1~6단)",
  "description": "무기 설명 (줄바꿈은 \n)",
  "baseStats": [{ "step": 1, "maxHp": 116, "attack": 381, "critRate": 10, "physPen": 10 }],
  "effects": [
    { "name": "고고한 에투알", "type": "전용",
      "levels": [{ "step": 1, "effect": "...[새벽의 빛 1]{green}..." }] }
  ]
}
```

- `grade`: 희귀/영웅/전설 · `type`: 일반/전용(캐릭터 전용)
- `levels`의 `step`은 각성(=돌파) 단계
- `baseStats`는 각성 단계별 수치 배열 (캐릭터 상세에서 표로 표시)

### 캐릭터 형식

```json
{
  "name": "자드",
  "grade": "전설", "faction": "무소속", "element": "욕망의그림자",
  "birthYear": "에스겔력 1256년", "height": "165cm", "cv": "이주은",
  "profileText": "소개글 (줄바꿈은 \n)",
  "published": true,
  "classTree": ["로그", "씨프", "카덴차", "섀도우댄서", "얀크", "프리마"],
  "exclusiveWeapon": "라 사바흐",
  "passive": { "name": "관능의 아라베스크",
    "levels": [{ "type": "각성", "step": 3, "effect": "..." }, { "type": "발현", "step": 2, "effect": "..." }] },
  "ultimate": { "name": "메테오 스트라이크", "tpCost": 5, "range": [1, 1], "area": "광역", "cooldown": 5,
    "levels": [{ "step": 1, "effect": "..." }] },
  "artifacts": [{ "name": "아티팩트 이름", "order": 1, "levels": [{ "step": 3, "effect": "..." }] }]
}
```

- `grade` 희귀/영웅/전설/아우터원 · `faction` 게이시르/팬드래건/무소속/아스타니아/제피르팰컨/다갈 · `element` 신념의빛/욕망의그림자/자유의불꽃/지성의결정체/활력의나무
- `passive.levels`: `type` 각성(3~6) 또는 발현(2/4/6) · `ultimate.levels`: 발현 0/1/3/5 · `artifacts[].levels`: 발현 3~6
- `stats` 키를 넣으면 스탯도 반영 (hp/attack/spellAttack/defense/critRate/critDamage/physPen/magicPen/effectResist)
- `published: false`면 공개 목록·상세에 안 나옴 (관리자만 확인 가능)
- 발현 3~6단 연결(필살기 3·5, 패시브 4·6, 아티팩트)은 자동으로 생성

### 효과 텍스트 색 태그

`[텍스트]{색}` — red: 수치, yellow: 턴·쿨타임·TP·중첩, green: 버프 이름, orange: 디버프 이름, blue/purple: 미정

green/orange 이름이 data의 버프/디버프 이름(또는 `"이름 레벨"`)과 다르면 반영 시 경고가 출력됩니다.

## 캐릭터 한 명 추가하기 — 스크린샷 체크리스트

순서는 **버프/디버프 → 클래스 → 전용무기 → 캐릭터**. 뒤 단계가 앞 단계를 이름으로 참조하기 때문에 순서를 지켜야 합니다.

### 0. 먼저 확인 (이미 있으면 건너뜀)

- 클래스 계열이 기존 캐릭터와 같으면 **클래스 단계 전체를 건너뜁니다** (1티어는 특히 많이 겹침)
- 이미 등록된 버프/디버프면 다시 넣지 않습니다. 새로 나온 태그만 `tags.json`에 추가
- 전용무기는 캐릭터마다 새로 생깁니다

### 1. 버프 / 디버프

| 스크린샷 | 뽑는 정보 |
|---|---|
| 고유 패시브 상세 (아래쪽 버프 설명까지) | 버프 이름, 레벨별 효과, 지속 턴, 최대 중첩, 태그 |
| 클래스 패시브 상세 (클래스당 2개) | 클래스가 주는 버프 |
| 디버프를 거는 스킬 설명 | 디버프 이름·효과·지속·태그 |

- 레벨이 있는 버프는 **모든 레벨**이 필요합니다 (예: 관능의 아라베스크 1~7)
- 아이콘은 없어도 됩니다 (버프는 아이콘 없이 표시)

### 2. 클래스 (계열 단위, 한 번만)

| 스크린샷 | 뽑는 정보 |
|---|---|
| 클래스 트리 화면 | 티어 구조·상위 클래스 연결 |
| 클래스 상세 | 사용무기, 방어타입, 공격타입, 공격사거리, 이동거리 |
| 클래스 패시브 Lv.1 / Lv.2 | 패시브 이름·효과 |
| 스킬 상세 (클래스당 1~3개) | 이름, TP, 사거리, 범위, 쿨타임, 허용 무기, 태그, 설명 |

- 필요한 아이콘: **클래스 엠블럼**, **클래스 패시브 아이콘**, **스킬 아이콘**

### 3. 전용무기

| 스크린샷 | 뽑는 정보 |
|---|---|
| 무기 정보 | 이름, 종류, 등급, 설명, 추가 능력치 |
| 각성 수치표 | 각성 1~6단의 최대 체력·공격력·치명타 확률·물리 관통 |
| 전용효과 (캐릭터 전용) | 각성 단계별 효과 텍스트 |
| 일반효과 (공용 옵션) | 각성 단계별 효과 텍스트 |

- 필요한 아이콘: **무기 아이콘**
- 전용/일반 구분이 중요합니다 — 일반효과에서 나오는 버프는 캐릭터가 아니라 **무기 소속**으로 표시됩니다

### 4. 캐릭터

| 스크린샷 | 뽑는 정보 |
|---|---|
| 캐릭터 정보(프로필) | 이름, 등급, 진영, 속성, 출생연도, 신장, CV, 소개글 |
| 고유 패시브 | 각성 3·4·5·6 + 발현 2·4·6 (총 7단계) |
| 필살기 | 발현 0·1·3·5단 효과 + TP·사거리·쿨타임 |
| 아티팩트 (3~4개) | 각 아티팩트의 발현 3·4·5·6단 효과 |
| 발현 트리 | 아티팩트 순서 확인용 |

- 필요한 이미지: **썸네일**(목록·사용자 표시), **초상화**(상세 프로필), 전신(선택)
- 필요한 아이콘: **고유 패시브**, **필살기**, **아티팩트 각각**
- 스크린샷이 아니어도 되는 값: **출시일**, **출현작**

### 아직 넣지 않는 것

- **스탯** — 1레벨 기준 전시용으로 할지 시뮬레이션용으로 계산할지 미정
- 스킨, 인연

### 아이콘 파일 두는 곳 (프론트 저장소 `public/icons/`)

```
classes/emblem/<영문>.png     클래스 엠블럼
classes/passive/<영문>.png    클래스 패시브
skills/<영문>.png             스킬
weapons/<영문>.png            전용무기
characters/<영문>_thumb.png   목록 썸네일
characters/<영문>_portrait.png 상세 초상화
passives/<영문>.png           캐릭터 고유 패시브
ultimates/<영문>.png          필살기
artifacts/<영문>.png          아티팩트
```

### 작업 흐름

1. 스크린샷 → `data/*.json` 작성 (버프 → 클래스 → 무기 → 캐릭터 순)
2. `python3 scripts/gen_sql.py` 로 검증 (알 수 없는 키·태그·색, 끊어진 버프 이름 경고)
3. 아이콘은 프론트 저장소에 커밋
4. 서버에서 `git pull && ./scripts/db-sync.sh`
