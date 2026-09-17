# 위키 데이터

게임 데이터를 JSON으로 관리하고 `scripts/db-sync.sh`로 서버 DB에 반영합니다.
여기 있는 항목은 **이 파일이 원본**입니다. 관리자 화면에서 같은 항목을 고쳐도 다음 반영 때 JSON 내용으로 덮어씁니다.

## 반영

```bash
ssh vultr
cd ~/apps/genesis-API && git pull && ./scripts/db-sync.sh
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

### 효과 텍스트 색 태그

`[텍스트]{색}` — red: 수치, yellow: 턴·쿨타임·TP·중첩, green: 버프 이름, orange: 디버프 이름, blue/purple: 미정
