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
