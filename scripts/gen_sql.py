#!/usr/bin/env python3
"""data/ 의 JSON(태그·버프·디버프·클래스)을 이름 기준 upsert SQL로 변환해 stdout으로 출력.

- 이름으로 찾아서 없으면 추가, 있으면 갱신 → 여러 번 실행해도 결과 동일
- 버프/디버프의 레벨·태그 매핑은 JSON 내용으로 전부 교체
- iconUrl 키가 없으면 기존 아이콘은 건드리지 않음 (관리자 화면에서 넣은 값 유지)
- 클래스는 기본 정보·패시브·액티브 스킬을 갱신 (수치 base_hp/base_attack은 건드리지 않음)
- 전용무기는 기본 정보와 효과(각성 단계별)를 갱신
- 아티팩트는 캐릭터 공용 목록 (data/artifacts) — 캐릭터는 이름으로 연결만 한다\n- 캐릭터는 기본 정보·클래스 트리·고유 패시브·필살기·아티팩트 연결·발현을 갱신 (스탯은 stats 키가 있을 때만)
- 스킬은 (클래스, 스킬 이름) 기준으로 추가/갱신, JSON에서 빠진 스킬을 지우지는 않음
- 전체가 하나의 트랜잭션이라 중간에 에러가 나면 아무것도 반영되지 않음
- 효과 텍스트의 {green}/{orange} 이름이 data에 없는 버프/디버프면 경고만 출력 (stderr)
"""
import json
import re
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"

TAG_COLORS = {"gray", "red", "orange", "yellow", "green", "blue", "purple"}
TEXT_TAG = re.compile(r"\[([^\]]+)\]\{(\w+)\}")
TEXT_TAG_COLORS = {"red", "yellow", "green", "orange", "blue", "purple"}

# 지속 "영구"는 DB에 -1로 저장 (NULL은 지속 표시 없음)
PERMANENT_DURATION = -1

# (data 폴더, 테이블 접두어)
KINDS = [("buffs", "buff"), ("debuffs", "debuff")]

ITEM_KEYS = {"name", "description", "iconUrl", "duration", "maxStack", "tags", "levels"}
LEVEL_KEYS = {"level", "name", "effect", "duration", "maxStack"}
CLASS_KEYS = {"name", "tier", "parent", "weaponType", "defenseType", "attackType", "attackRange", "moveRange",
              "description", "iconUrl", "passive", "skills"}
SKILL_KEYS = {"name", "tpCost", "range", "area", "attackType", "allowedWeapon", "cooldown", "effect", "tags", "iconUrl"}
SELF_RANGE = "자신"  # 사거리 "자신"은 0-0으로 저장
PASSIVE_KEYS = {"name", "lv1", "lv2", "iconUrl"}
WEAPON_KEYS = {"name", "weaponType", "grade", "baseStats", "extraStats", "description", "iconUrl", "effects"}
WEAPON_EFFECT_KEYS = {"name", "type", "baseEffect", "iconUrl", "levels"}
WEAPON_LEVEL_KEYS = {"step", "effect"}
GRADES = {"희귀": "rare", "영웅": "hero", "전설": "legend",
          "rare": "rare", "hero": "hero", "legend": "legend"}
EFFECT_TYPES = {"일반": "normal", "전용": "exclusive", "normal": "normal", "exclusive": "exclusive"}

CHARACTER_KEYS = {"name", "grade", "faction", "element", "birthYear", "height", "cv", "profileText",
                  "releaseDate", "appearedIn",
                  "thumbnailUrl", "portraitUrl", "fullImageUrl", "published", "stats",
                  "classTree", "exclusiveWeapon", "passive", "ultimate", "artifacts"}
STATS_KEYS = {"hp", "attack", "spellAttack", "defense", "critRate", "critDamage", "physPen", "magicPen", "effectResist"}
CHAR_PASSIVE_KEYS = {"name", "iconUrl", "levels"}
CHAR_PASSIVE_LEVEL_KEYS = {"type", "step", "effect"}
ULTIMATE_KEYS = {"name", "iconUrl", "tpCost", "range", "area", "cooldown", "levels"}
ULTIMATE_LEVEL_KEYS = {"step", "tpCost", "range", "cooldown", "effect"}
ARTIFACT_KEYS = {"name", "grade", "iconUrl", "description", "levels"}
ARTIFACT_LEVEL_KEYS = {"step", "effect"}
FACTIONS = {"게이시르": "geysir", "팬드래건": "pendragon", "무소속": "independent",
            "아스타니아": "astania", "제피르팰컨": "zephyrfalcon", "다갈": "dagal"}
ELEMENTS = {"신념의빛": "light", "욕망의그림자": "dark", "자유의불꽃": "fire",
            "지성의결정체": "crystal", "활력의나무": "nature"}
CHAR_GRADES = {"희귀": "rare", "영웅": "hero", "전설": "legend", "아우터원": "outer"}
UNLOCK_TYPES = {"각성": "awaken", "발현": "manifest"}
# 고유 패시브/필살기/아티팩트가 붙는 발현 단계 (constants/manifest.ts 와 같은 규칙)
MANIFEST_ULTIMATE_STEPS = [3, 5]
MANIFEST_PASSIVE_STEPS = [4, 6]
MANIFEST_HUB_STEPS = [3, 4, 5, 6]
DEFENSE_TYPES = {"라이트": "light", "미디엄": "medium", "헤비": "heavy",
                 "light": "light", "medium": "medium", "heavy": "heavy"}


class DataError(Exception):
    pass


def sql(value):
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str):
        return "'" + value.replace("\\", "\\\\").replace("'", "''") + "'"
    raise DataError(f"SQL로 바꿀 수 없는 값: {value!r}")


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise DataError(f"{path.relative_to(DATA)}: JSON 형식 오류 ({e})")


def load_folder(folder):
    """폴더의 *.json 배열을 (파일경로, 항목) 순서대로 반환"""
    for path in sorted((DATA / folder).glob("*.json")):
        rel = path.relative_to(DATA)
        for item in load_json(path):
            yield rel, item


def check_keys(where, obj, allowed):
    unknown = set(obj) - allowed
    if unknown:
        raise DataError(f"{where}: 알 수 없는 항목 {sorted(unknown)}")


def check_text(where, text):
    if text is None:
        return
    for label, color in TEXT_TAG.findall(text):
        if color not in TEXT_TAG_COLORS:
            raise DataError(f"{where}: 알 수 없는 색 태그 [{label}]{{{color}}}")


def duration(where, value):
    if value is None or (isinstance(value, int) and not isinstance(value, bool) and value > 0):
        return value
    if value == "영구":
        return PERMANENT_DURATION
    raise DataError(f"{where}: duration은 1 이상의 숫자 또는 \"영구\" ({value!r})")


def skill_range(where, value):
    if value is None:
        return None, None
    if value == SELF_RANGE:
        return 0, 0
    if (isinstance(value, list) and len(value) == 2 and all(isinstance(v, int) for v in value)
            and 0 < value[0] <= value[1]):
        return value[0], value[1]
    raise DataError(f"{where}: range는 [최소, 최대] 또는 \"자신\" ({value!r})")


def level_name(item, lvl):
    return lvl.get("name") or f"{item['name']} {lvl['level']}"


# ─── 로드 · 검증 ─────────────────────────────────────────

def load_tags():
    tags = load_json(DATA / "tags.json")
    names = set()
    for t in tags:
        if t.get("color", "gray") not in TAG_COLORS:
            raise DataError(f"tags.json: '{t['name']}' 색상 오류 ({t.get('color')})")
        if t["name"] in names:
            raise DataError(f"tags.json: 중복 태그 '{t['name']}'")
        names.add(t["name"])
    return tags, names


def load_items(folder, tag_names):
    items, seen = [], {}
    for rel, item in load_folder(folder):
        where = f"{rel} '{item.get('name')}'"
        check_keys(where, item, ITEM_KEYS)
        if not item.get("name"):
            raise DataError(f"{rel}: name 없는 항목")
        if item["name"] in seen:
            raise DataError(f"{where}: {seen[item['name']]} 에도 같은 이름이 있음")
        seen[item["name"]] = rel
        for tag in item.get("tags", []):
            if tag not in tag_names:
                raise DataError(f"{where}: tags.json에 없는 태그 '{tag}'")
        check_text(where, item.get("description"))
        duration(where, item.get("duration"))
        levels = set()
        for lvl in item.get("levels", []):
            lvl_where = f"{where} 레벨 {lvl.get('level')}"
            check_keys(lvl_where, lvl, LEVEL_KEYS)
            if lvl["level"] in levels:
                raise DataError(f"{where}: 레벨 {lvl['level']} 중복")
            levels.add(lvl["level"])
            check_text(lvl_where, lvl.get("effect"))
            duration(lvl_where, lvl.get("duration"))
        items.append(item)
    return items


def load_classes(tag_names):
    classes = {}
    for rel, cls in load_folder("classes"):
        where = f"{rel} '{cls.get('name')}'"
        check_keys(where, cls, CLASS_KEYS)
        if not cls.get("name"):
            raise DataError(f"{rel}: name 없는 클래스")
        if cls["name"] in classes:
            raise DataError(f"{where}: 같은 이름의 클래스가 이미 있음")
        if cls.get("tier") not in (1, 2, 3):
            raise DataError(f"{where}: tier는 1/2/3 ({cls.get('tier')!r})")
        if "defenseType" in cls and cls["defenseType"] not in DEFENSE_TYPES:
            raise DataError(f"{where}: defenseType은 라이트/미디엄/헤비 ({cls['defenseType']!r})")
        passive = cls.get("passive", {})
        check_keys(f"{where} passive", passive, PASSIVE_KEYS)
        check_text(where, cls.get("description"))
        check_text(f"{where} passive lv1", passive.get("lv1"))
        check_text(f"{where} passive lv2", passive.get("lv2"))
        skill_names = set()
        for skill in cls.get("skills", []):
            skill_where = f"{where} 스킬 '{skill.get('name')}'"
            check_keys(skill_where, skill, SKILL_KEYS)
            if not skill.get("name") or skill["name"] in skill_names:
                raise DataError(f"{skill_where}: 스킬 이름이 없거나 중복")
            skill_names.add(skill["name"])
            skill_range(skill_where, skill.get("range"))
            check_text(skill_where, skill.get("effect"))
            for tag in skill.get("tags", []):
                if tag not in tag_names:
                    raise DataError(f"{skill_where}: tags.json에 없는 태그 '{tag}'")
        classes[cls["name"]] = (rel, cls)

    for name, (rel, cls) in classes.items():
        where = f"{rel} '{name}'"
        parent = cls.get("parent")
        if cls["tier"] == 1:
            if parent:
                raise DataError(f"{where}: 1티어는 parent가 없어야 함")
        elif parent not in classes:
            raise DataError(f"{where}: parent '{parent}' 클래스가 data/classes에 없음")
        elif classes[parent][1]["tier"] != cls["tier"] - 1:
            raise DataError(f"{where}: parent '{parent}'는 {cls['tier'] - 1}티어여야 함")

    # 부모가 먼저 들어가도록 티어 순
    return sorted((c for _, c in classes.values()), key=lambda c: c["tier"])


def load_weapons():
    weapons, seen = [], set()
    for rel, w in load_folder("weapons"):
        where = f"{rel} '{w.get('name')}'"
        check_keys(where, w, WEAPON_KEYS)
        if not w.get("name") or w["name"] in seen:
            raise DataError(f"{where}: 무기 이름이 없거나 중복")
        seen.add(w["name"])
        if w.get("grade") not in GRADES:
            raise DataError(f"{where}: grade는 희귀/영웅/전설 ({w.get('grade')!r})")
        if "baseStats" in w and not isinstance(w["baseStats"], (list, dict)):
            raise DataError(f"{where}: baseStats는 JSON 배열/객체")
        check_text(where, w.get("description"))
        for eff in w.get("effects", []):
            eff_where = f"{where} 효과 '{eff.get('name')}'"
            check_keys(eff_where, eff, WEAPON_EFFECT_KEYS)
            if eff.get("type") not in EFFECT_TYPES:
                raise DataError(f"{eff_where}: type은 일반/전용 ({eff.get('type')!r})")
            check_text(eff_where, eff.get("baseEffect"))
            steps = set()
            for lvl in eff.get("levels", []):
                check_keys(f"{eff_where} {lvl.get('step')}단", lvl, WEAPON_LEVEL_KEYS)
                if lvl["step"] in steps:
                    raise DataError(f"{eff_where}: {lvl['step']}단 중복")
                steps.add(lvl["step"])
                check_text(f"{eff_where} {lvl['step']}단", lvl.get("effect"))
        weapons.append(w)
    return weapons


def load_artifacts():
    """아티팩트는 캐릭터 공용 목록 (발현 3~6단 = 아티팩트 ★1~★4)"""
    artifacts, seen = [], set()
    for rel, a in load_folder("artifacts"):
        where = f"{rel} '{a.get('name')}'"
        check_keys(where, a, ARTIFACT_KEYS)
        if not a.get("name") or a["name"] in seen:
            raise DataError(f"{where}: 아티팩트 이름이 없거나 중복")
        seen.add(a["name"])
        if "grade" in a and a["grade"] not in GRADES:
            raise DataError(f"{where}: grade는 희귀/영웅/전설 ({a.get('grade')!r})")
        check_text(where, a.get("description"))
        steps = set()
        for lvl in a.get("levels", []):
            lw = f"{where} {lvl.get('step')}단"
            check_keys(lw, lvl, ARTIFACT_LEVEL_KEYS)
            if lvl["step"] in steps:
                raise DataError(f"{lw}: 중복")
            steps.add(lvl["step"])
            check_text(lw, lvl.get("effect"))
        artifacts.append(a)
    return artifacts


def load_characters(class_names, weapon_names, artifact_names):
    characters, seen = [], set()
    for rel, c in load_folder("characters"):
        where = f"{rel} '{c.get('name')}'"
        check_keys(where, c, CHARACTER_KEYS)
        if not c.get("name") or c["name"] in seen:
            raise DataError(f"{where}: 캐릭터 이름이 없거나 중복")
        seen.add(c["name"])
        for key, table in (("grade", CHAR_GRADES), ("faction", FACTIONS), ("element", ELEMENTS)):
            if c.get(key) not in table:
                raise DataError(f"{where}: {key}는 {'/'.join(table)} 중 하나 ({c.get(key)!r})")
        check_keys(f"{where} stats", c.get("stats", {}), STATS_KEYS)
        check_text(where, c.get("profileText"))
        for cls in c.get("classTree", []):
            if cls not in class_names:
                raise DataError(f"{where}: data/classes에 없는 클래스 '{cls}'")
        if "exclusiveWeapon" in c and c["exclusiveWeapon"] not in weapon_names:
            raise DataError(f"{where}: data/weapons에 없는 전용무기 '{c['exclusiveWeapon']}'")

        passive = c.get("passive")
        if passive:
            check_keys(f"{where} 고유 패시브", passive, CHAR_PASSIVE_KEYS)
            steps = set()
            for lvl in passive.get("levels", []):
                lw = f"{where} 고유 패시브 {lvl.get('type')} {lvl.get('step')}단"
                check_keys(lw, lvl, CHAR_PASSIVE_LEVEL_KEYS)
                if lvl.get("type") not in UNLOCK_TYPES:
                    raise DataError(f"{lw}: type은 각성/발현")
                if (lvl["type"], lvl["step"]) in steps:
                    raise DataError(f"{lw}: 중복")
                steps.add((lvl["type"], lvl["step"]))
                check_text(lw, lvl.get("effect"))

        ultimate = c.get("ultimate")
        if ultimate:
            check_keys(f"{where} 필살기", ultimate, ULTIMATE_KEYS)
            skill_range(f"{where} 필살기", ultimate.get("range"))
            steps = set()
            for lvl in ultimate.get("levels", []):
                lw = f"{where} 필살기 발현 {lvl.get('step')}단"
                check_keys(lw, lvl, ULTIMATE_LEVEL_KEYS)
                if lvl["step"] in steps:
                    raise DataError(f"{lw}: 중복")
                steps.add(lvl["step"])
                skill_range(lw, lvl.get("range"))
                check_text(lw, lvl.get("effect"))

        arts = c.get("artifacts", [])
        if len(arts) > 4:
            raise DataError(f"{where}: 아티팩트는 최대 4개")
        if len(set(arts)) != len(arts):
            raise DataError(f"{where}: 아티팩트 중복")
        for art in arts:
            if not isinstance(art, str):
                raise DataError(f"{where}: 아티팩트는 data/artifacts의 이름만 적는다 ({art!r})")
            if art not in artifact_names:
                raise DataError(f"{where}: data/artifacts에 없는 아티팩트 '{art}'")
        characters.append(c)
    return characters


def warn_unknown_links(buffs, debuffs, classes, weapons, artifacts, characters):
    known = {
        "green": {n for b in buffs for n in [b["name"], *(level_name(b, l) for l in b.get("levels", []))]},
        "orange": {n for d in debuffs for n in [d["name"], *(level_name(d, l) for l in d.get("levels", []))]},
    }
    texts = []
    for kind, items in (("버프", buffs), ("디버프", debuffs)):
        for it in items:
            texts.append((f"{kind} '{it['name']}'", it.get("description")))
            texts += [(f"{kind} '{level_name(it, l)}'", l.get("effect")) for l in it.get("levels", [])]
    for c in classes:
        p = c.get("passive", {})
        texts += [(f"클래스 '{c['name']}' 패시브 lv1", p.get("lv1")), (f"클래스 '{c['name']}' 패시브 lv2", p.get("lv2"))]
        texts += [(f"클래스 '{c['name']}' 스킬 '{sk['name']}'", sk.get("effect")) for sk in c.get("skills", [])]
    for w in weapons:
        for eff in w.get("effects", []):
            texts.append((f"무기 '{w['name']}' 효과 '{eff['name']}'", eff.get("baseEffect")))
            texts += [(f"무기 '{w['name']}' 효과 '{eff['name']}' {l['step']}단", l.get("effect")) for l in eff.get("levels", [])]
    for a in artifacts:
        texts += [(f"아티팩트 '{a['name']}' {l['step']}단", l.get("effect")) for l in a.get("levels", [])]
    for c in characters:
        p = c.get("passive") or {}
        texts += [(f"캐릭터 '{c['name']}' 패시브 {l['type']} {l['step']}단", l.get("effect")) for l in p.get("levels", [])]
        u = c.get("ultimate") or {}
        texts += [(f"캐릭터 '{c['name']}' 필살기 {l['step']}단", l.get("effect")) for l in u.get("levels", [])]


    for where, text in texts:
        for label, color in TEXT_TAG.findall(text or ""):
            if color in known and label not in known[color]:
                kind = "버프" if color == "green" else "디버프"
                print(f"경고: {where}의 [{label}]{{{color}}} → data에 없는 {kind} 이름", file=sys.stderr)


# ─── SQL 생성 ────────────────────────────────────────────

def upsert_head(table, id_col, name, insert_cols):
    cols = ", ".join(["name", *insert_cols, "created_at", "updated_at"])
    vals = ", ".join([sql(name), *(sql(v) for v in insert_cols.values()), "NOW()", "NOW()"])
    return [
        f"-- {name}",
        f"SET @id = (SELECT {id_col} FROM {table} WHERE name = {sql(name)});",
        f"INSERT INTO {table} ({cols}) SELECT {vals} FROM DUAL WHERE @id IS NULL;",
        "SET @id = COALESCE(@id, LAST_INSERT_ID());",
    ]


def item_sql(prefix, item):
    table, id_col = f"{prefix}s", f"{prefix}_id"
    levels = sorted(item.get("levels", []), key=lambda l: l["level"])
    has_levels = bool(levels)

    out = upsert_head(table, id_col, item["name"], {"max_stack": 1, "has_levels": has_levels})
    sets = [
        f"description = {sql(item.get('description'))}",
        f"duration = {sql(duration(item['name'], item.get('duration')))}",
        f"max_stack = {sql(item.get('maxStack', 1))}",
        f"has_levels = {sql(has_levels)}",
    ]
    if "iconUrl" in item:
        sets.append(f"icon_url = {sql(item['iconUrl'])}")
    sets.append("updated_at = NOW()")
    out.append(f"UPDATE {table} SET {', '.join(sets)} WHERE {id_col} = @id;")

    out.append(f"DELETE FROM {prefix}_levels WHERE {id_col} = @id;")
    if levels:
        rows = ",\n".join(
            f"(@id, {sql(l['level'])}, {sql(level_name(item, l))}, {sql(l.get('effect'))}, "
            f"{sql(duration(item['name'], l.get('duration')))}, {sql(l.get('maxStack'))})"
            for l in levels
        )
        out.append(f"INSERT INTO {prefix}_levels ({id_col}, level, level_name, effect_text, duration, max_stack) VALUES\n{rows};")

    out.append(f"DELETE FROM {prefix}_tag_map WHERE {id_col} = @id;")
    if item.get("tags"):
        tag_list = ", ".join(sql(t) for t in item["tags"])
        out.append(f"INSERT INTO {prefix}_tag_map ({id_col}, tag_id) SELECT @id, tag_id FROM tags WHERE name IN ({tag_list});")
    return "\n".join(out)


def class_sql(cls):
    passive = cls.get("passive", {})
    parent = cls.get("parent")
    out = [f"SET @parent = {'(SELECT class_id FROM classes WHERE name = ' + sql(parent) + ')' if parent else 'NULL'};"]
    out += upsert_head("classes", "class_id", cls["name"], {"tier": cls["tier"]})
    sets = [
        f"tier = {sql(cls['tier'])}",
        "parent_class_id = @parent",
        f"weapon_type = {sql(cls.get('weaponType'))}",
        f"defense_type = {sql(DEFENSE_TYPES.get(cls.get('defenseType')))}",
        f"attack_type = {sql(cls.get('attackType'))}",
        f"attack_range = {sql(cls.get('attackRange'))}",
        f"move_range = {sql(cls.get('moveRange'))}",
        f"description = {sql(cls.get('description'))}",
        f"passive1_name = {sql(passive.get('name'))}",
        f"passive1_lv1 = {sql(passive.get('lv1'))}",
        f"passive1_lv2 = {sql(passive.get('lv2'))}",
    ]
    if "iconUrl" in cls:
        sets.append(f"icon_url = {sql(cls['iconUrl'])}")
    if "iconUrl" in passive:
        sets.append(f"passive1_icon_url = {sql(passive['iconUrl'])}")
    sets.append("updated_at = NOW()")
    out.append(f"UPDATE classes SET {', '.join(sets)} WHERE class_id = @id;")
    for order, skill in enumerate(cls.get("skills", []), start=1):
        out.append(skill_sql(skill, order))
    return "\n".join(out)


def skill_sql(skill, order):
    """@id(클래스)에 연결된 같은 이름의 스킬을 찾아 추가/갱신"""
    name = sql(skill["name"])
    range_min, range_max = skill_range(skill["name"], skill.get("range"))
    out = [
        f"-- 스킬: {skill['name']}",
        "SET @skill = (SELECT s.skill_id FROM skills s JOIN class_skills cs ON cs.skill_id = s.skill_id "
        f"WHERE cs.class_id = @id AND s.name = {name} LIMIT 1);",
        f"INSERT INTO skills (name, type, created_at, updated_at) SELECT {name}, 'active', NOW(), NOW() FROM DUAL WHERE @skill IS NULL;",
        "SET @skill = COALESCE(@skill, LAST_INSERT_ID());",
        f"INSERT INTO class_skills (class_id, skill_id, unlock_order) SELECT @id, @skill, {order} FROM DUAL "
        "WHERE NOT EXISTS (SELECT 1 FROM class_skills WHERE class_id = @id AND skill_id = @skill);",
        f"UPDATE class_skills SET unlock_order = {order} WHERE class_id = @id AND skill_id = @skill;",
    ]
    sets = [
        "type = 'active'",
        f"tp_cost = {sql(skill.get('tpCost'))}",
        f"range_min = {sql(range_min)}",
        f"range_max = {sql(range_max)}",
        f"area = {sql(skill.get('area'))}",
        f"attack_type = {sql(skill.get('attackType'))}",
        f"allowed_weapon = {sql(skill.get('allowedWeapon'))}",
        f"cooldown = {sql(skill.get('cooldown'))}",
        f"effect_text = {sql(skill.get('effect'))}",
    ]
    if "iconUrl" in skill:
        sets.append(f"icon_url = {sql(skill['iconUrl'])}")
    sets.append("updated_at = NOW()")
    out.append(f"UPDATE skills SET {', '.join(sets)} WHERE skill_id = @skill;")
    out.append("DELETE FROM skill_tag_map WHERE skill_id = @skill;")
    if skill.get("tags"):
        tag_list = ", ".join(sql(t) for t in skill["tags"])
        out.append(f"INSERT INTO skill_tag_map (skill_id, tag_id) SELECT @skill, tag_id FROM tags WHERE name IN ({tag_list});")
    return "\n".join(out)


def weapon_sql(w):
    name = sql(w["name"])
    out = [
        f"-- 전용무기: {w['name']}",
        f"SET @id = (SELECT weapon_id FROM exclusive_weapons WHERE name = {name});",
        f"INSERT INTO exclusive_weapons (name, grade, created_at, updated_at) "
        f"SELECT {name}, {sql(GRADES[w['grade']])}, NOW(), NOW() FROM DUAL WHERE @id IS NULL;",
        "SET @id = COALESCE(@id, LAST_INSERT_ID());",
    ]
    sets = [
        f"weapon_type = {sql(w.get('weaponType'))}",
        f"grade = {sql(GRADES[w['grade']])}",
        f"base_stats = {sql(json.dumps(w['baseStats'], ensure_ascii=False)) if 'baseStats' in w else 'NULL'}",
        f"extra_stats = {sql(w.get('extraStats'))}",
        f"description = {sql(w.get('description'))}",
    ]
    if "iconUrl" in w:
        sets.append(f"icon_url = {sql(w['iconUrl'])}")
    sets.append("updated_at = NOW()")
    out.append(f"UPDATE exclusive_weapons SET {', '.join(sets)} WHERE weapon_id = @id;")

    for eff in w.get("effects", []):
        eff_name = sql(eff["name"])
        eff_type = sql(EFFECT_TYPES[eff["type"]])
        out += [
            f"-- 효과: {eff['name']}",
            f"SET @eff = (SELECT effect_id FROM exclusive_weapon_effects WHERE weapon_id = @id AND effect_name = {eff_name} LIMIT 1);",
            f"INSERT INTO exclusive_weapon_effects (weapon_id, effect_name, effect_type) "
            f"SELECT @id, {eff_name}, {eff_type} FROM DUAL WHERE @eff IS NULL;",
            "SET @eff = COALESCE(@eff, LAST_INSERT_ID());",
        ]
        eff_sets = [f"effect_type = {eff_type}", f"base_effect = {sql(eff.get('baseEffect'))}"]
        if "iconUrl" in eff:
            eff_sets.append(f"icon_url = {sql(eff['iconUrl'])}")
        out.append(f"UPDATE exclusive_weapon_effects SET {', '.join(eff_sets)} WHERE effect_id = @eff;")
        out.append("DELETE FROM exclusive_weapon_effect_levels WHERE effect_id = @eff;")
        levels = sorted(eff.get("levels", []), key=lambda l: l["step"])
        if levels:
            rows = ",\n".join(f"(@eff, {sql(l['step'])}, {sql(l.get('effect'))})" for l in levels)
            out.append(f"INSERT INTO exclusive_weapon_effect_levels (effect_id, breakthrough_step, effect_text) VALUES\n{rows};")
    return "\n".join(out)


def weapon_summary_sql(weapons):
    names = ", ".join(sql(w["name"]) for w in weapons)
    return (
        "SELECT w.weapon_id AS id, w.name, w.grade, w.weapon_type, e.effect_name, e.effect_type,\n"
        "  (SELECT COUNT(*) FROM exclusive_weapon_effect_levels l WHERE l.effect_id = e.effect_id) AS steps,\n"
        "  w.icon_url IS NOT NULL AS icon\n"
        "FROM exclusive_weapons w LEFT JOIN exclusive_weapon_effects e ON e.weapon_id = w.weapon_id\n"
        f"WHERE w.name IN ({names}) ORDER BY w.weapon_id, e.effect_id;"
    )


def artifact_sql(a):
    """아티팩트: 공용 목록 + 단계별 효과 (발현 3~6단)"""
    name = sql(a["name"])
    out = [
        f"-- 아티팩트: {a['name']}",
        f"SET @art = (SELECT artifact_id FROM artifacts WHERE name = {name});",
        f"INSERT INTO artifacts (name, created_at, updated_at) "
        f"SELECT {name}, NOW(), NOW() FROM DUAL WHERE @art IS NULL;",
        "SET @art = COALESCE(@art, LAST_INSERT_ID());",
    ]
    sets = [f"grade = {sql(GRADES[a['grade']])}" if "grade" in a else None,
            f"description = {sql(a.get('description'))}" if "description" in a else None,
            f"icon_url = {sql(a['iconUrl'])}" if "iconUrl" in a else None]
    sets = [x for x in sets if x] + ["updated_at = NOW()"]
    out.append(f"UPDATE artifacts SET {', '.join(sets)} WHERE artifact_id = @art;")
    out.append("DELETE FROM artifact_levels WHERE artifact_id = @art;")
    levels = sorted(a.get("levels", []), key=lambda l: l["step"])
    if levels:
        rows = ",\n".join(f"(@art, {sql(l['step'])}, {sql(l.get('effect'))})" for l in levels)
        out.append(f"INSERT INTO artifact_levels (artifact_id, manifest_step, effect_text) VALUES\n{rows};")
    return "\n".join(out)


def artifact_summary_sql(artifacts):
    names = ", ".join(sql(a["name"]) for a in artifacts)
    return (f"SELECT a.artifact_id AS id, a.name, a.grade,\n"
            f"  (SELECT COUNT(*) FROM artifact_levels l WHERE l.artifact_id = a.artifact_id) AS levels,\n"
            f"  (SELECT COUNT(*) FROM character_artifacts ca WHERE ca.artifact_id = a.artifact_id) AS used_by\n"
            f"FROM artifacts a WHERE a.name IN ({names}) ORDER BY a.artifact_id;")


def character_sql(c):
    """캐릭터: 기본 정보 + 클래스 트리 + 고유 패시브 + 필살기 + 아티팩트 + 발현 연결"""
    name = sql(c["name"])
    out = [
        f"-- 캐릭터: {c['name']}",
        f"SET @id = (SELECT character_id FROM characters WHERE name = {name});",
        f"INSERT INTO characters (name, grade, faction, element, is_published, created_at, updated_at) "
        f"SELECT {name}, {sql(CHAR_GRADES[c['grade']])}, {sql(FACTIONS[c['faction']])}, {sql(ELEMENTS[c['element']])}, "
        f"{sql(bool(c.get('published')))}, NOW(), NOW() FROM DUAL WHERE @id IS NULL;",
        "SET @id = COALESCE(@id, LAST_INSERT_ID());",
    ]
    sets = [
        f"grade = {sql(CHAR_GRADES[c['grade']])}",
        f"faction = {sql(FACTIONS[c['faction']])}",
        f"element = {sql(ELEMENTS[c['element']])}",
        f"birth_year = {sql(c.get('birthYear'))}",
        f"height = {sql(c.get('height'))}",
        f"cv = {sql(c.get('cv'))}",
        f"release_date = {sql(c.get('releaseDate'))}",
        f"appeared_in = {sql(c.get('appearedIn'))}",
        f"profile_text = {sql(c.get('profileText'))}",
        f"is_published = {sql(bool(c.get('published')))}",
    ]
    for key, col in (("thumbnailUrl", "thumbnail_url"), ("portraitUrl", "portrait_url"), ("fullImageUrl", "full_image_url")):
        if key in c:
            sets.append(f"{col} = {sql(c[key])}")
    if "exclusiveWeapon" in c:
        sets.append(f"exclusive_weapon_id = (SELECT weapon_id FROM exclusive_weapons WHERE name = {sql(c['exclusiveWeapon'])})")
    sets.append("updated_at = NOW()")
    out.append(f"UPDATE characters SET {', '.join(sets)} WHERE character_id = @id;")

    # 스탯 (stats 키가 있을 때만)
    stats = c.get("stats")
    if stats:
        cols = {"hp": "hp", "attack": "attack", "spellAttack": "spell_attack", "defense": "defense",
                "critRate": "crit_rate", "critDamage": "crit_damage", "physPen": "phys_pen",
                "magicPen": "magic_pen", "effectResist": "effect_resist"}
        out.append(f"DELETE FROM character_stats WHERE character_id = @id;")
        names = ", ".join(cols[k] for k in stats)
        values = ", ".join(sql(stats[k]) for k in stats)
        out.append(f"INSERT INTO character_stats (character_id, {names}) VALUES (@id, {values});")

    # 클래스 트리
    out.append("DELETE FROM character_class_tree WHERE character_id = @id;")
    for order, cls in enumerate(c.get("classTree", []), start=1):
        out.append(f"INSERT INTO character_class_tree (character_id, class_id, order_in_tier) "
                   f"SELECT @id, class_id, {order} FROM classes WHERE name = {sql(cls)};")

    # 발현 연결은 매번 새로 만듦
    out.append("DELETE FROM character_manifestation WHERE character_id = @id;")

    passive = c.get("passive")
    if passive:
        out += [
            f"SET @passive = (SELECT passive_id FROM character_passives WHERE character_id = @id AND name = {sql(passive['name'])} LIMIT 1);",
            f"INSERT INTO character_passives (character_id, name, created_at, updated_at) "
            f"SELECT @id, {sql(passive['name'])}, NOW(), NOW() FROM DUAL WHERE @passive IS NULL;",
            "SET @passive = COALESCE(@passive, LAST_INSERT_ID());",
            f"UPDATE character_passives SET name = {sql(passive['name'])}"
            + (f", icon_url = {sql(passive['iconUrl'])}" if "iconUrl" in passive else "")
            + ", updated_at = NOW() WHERE passive_id = @passive;",
            "DELETE FROM character_passive_levels WHERE passive_id = @passive;",
        ]
        levels = sorted(passive.get("levels", []), key=lambda l: (l["type"], l["step"]))
        if levels:
            rows = ",\n".join(f"(@passive, {sql(UNLOCK_TYPES[l['type']])}, {sql(l['step'])}, {sql(l.get('effect'))})" for l in levels)
            out.append(f"INSERT INTO character_passive_levels (passive_id, unlock_type, unlock_step, effect_text) VALUES\n{rows};")
    else:
        out.append("SET @passive = NULL;")

    ultimate = c.get("ultimate")
    if ultimate:
        u_min, u_max = skill_range(c["name"], ultimate.get("range"))
        out += [
            f"SET @ult = (SELECT ultimate_id FROM ultimate_skills WHERE name = {sql(ultimate['name'])} LIMIT 1);",
            f"INSERT INTO ultimate_skills (name, created_at, updated_at) SELECT {sql(ultimate['name'])}, NOW(), NOW() FROM DUAL WHERE @ult IS NULL;",
            "SET @ult = COALESCE(@ult, LAST_INSERT_ID());",
            f"UPDATE ultimate_skills SET name = {sql(ultimate['name'])}"
            + (f", icon_url = {sql(ultimate['iconUrl'])}" if "iconUrl" in ultimate else "")
            + ", updated_at = NOW() WHERE ultimate_id = @ult;",
            "DELETE FROM ultimate_skill_levels WHERE ultimate_id = @ult;",
        ]
        levels = sorted(ultimate.get("levels", []), key=lambda l: l["step"])
        if levels:
            rows = []
            for l in levels:
                r_min, r_max = skill_range(c["name"], l.get("range")) if "range" in l else (u_min, u_max)
                rows.append(f"(@ult, {sql(l['step'])}, {sql(l.get('tpCost', ultimate.get('tpCost')))}, "
                            f"{sql(r_min)}, {sql(r_max)}, {sql(l.get('cooldown', ultimate.get('cooldown')))}, {sql(l.get('effect'))})")
            out.append("INSERT INTO ultimate_skill_levels (ultimate_id, manifest_step, tp_cost, range_min, range_max, cooldown, effect_text) VALUES\n"
                       + ",\n".join(rows) + ";")
    else:
        out.append("SET @ult = NULL;")

    # 아티팩트 연결 (아티팩트 자체는 data/artifacts에서 관리)
    out.append("DELETE FROM character_artifacts WHERE character_id = @id;")
    artifact_vars = []
    for idx, art_name in enumerate(c.get("artifacts", []), start=1):
        var = f"@art{idx}"
        artifact_vars.append(var)
        out += [
            f"SET {var} = (SELECT artifact_id FROM artifacts WHERE name = {sql(art_name)});",
            f"INSERT INTO character_artifacts (character_id, artifact_id, artifact_order) "
            f"VALUES (@id, {var}, {idx});",
        ]
    while len(artifact_vars) < 4:
        artifact_vars.append("NULL")

    # 발현 허브 (3~6단)
    rows = []
    for step in MANIFEST_HUB_STEPS:
        ult = "@ult" if step in MANIFEST_ULTIMATE_STEPS else "NULL"
        pas = "@passive" if step in MANIFEST_PASSIVE_STEPS else "NULL"
        rows.append(f"(@id, {step}, {ult}, {pas}, {', '.join(artifact_vars)})")
    out.append("INSERT INTO character_manifestation (character_id, manifest_level, ultimate_id, passive_id, "
               "artifact1_id, artifact2_id, artifact3_id, artifact4_id) VALUES\n" + ",\n".join(rows) + ";")
    return "\n".join(out)


def character_summary_sql(characters):
    names = ", ".join(sql(c["name"]) for c in characters)
    return (
        "SELECT c.character_id AS id, c.name, c.grade, c.faction, c.element, c.is_published AS published,\n"
        "  (SELECT COUNT(*) FROM character_class_tree t WHERE t.character_id = c.character_id) AS classes,\n"
        "  (SELECT COUNT(*) FROM character_passive_levels l JOIN character_passives p ON p.passive_id = l.passive_id "
        "WHERE p.character_id = c.character_id) AS passive_levels,\n"
        "  (SELECT COUNT(*) FROM character_artifacts ca WHERE ca.character_id = c.character_id) AS artifacts,\n"
        "  (SELECT COUNT(*) FROM ultimate_skill_levels ul JOIN character_manifestation m ON m.ultimate_id = ul.ultimate_id "
        "WHERE m.character_id = c.character_id) AS ult_levels,\n"
        "  w.name AS weapon\n"
        "FROM characters c LEFT JOIN exclusive_weapons w ON w.weapon_id = c.exclusive_weapon_id\n"
        f"WHERE c.name IN ({names}) ORDER BY c.character_id;"
    )


def item_summary_sql(prefix, items):
    table, id_col = f"{prefix}s", f"{prefix}_id"
    names = ", ".join(sql(i["name"]) for i in items)
    return (
        f"SELECT '{prefix}' AS kind, x.{id_col} AS id, x.name,\n"
        f"  CASE x.duration WHEN {PERMANENT_DURATION} THEN '영구' ELSE x.duration END AS duration, x.max_stack,\n"
        f"  (SELECT COUNT(*) FROM {prefix}_levels l WHERE l.{id_col} = x.{id_col}) AS levels,\n"
        f"  (SELECT GROUP_CONCAT(t.name ORDER BY t.tag_id) FROM {prefix}_tag_map m JOIN tags t ON t.tag_id = m.tag_id WHERE m.{id_col} = x.{id_col}) AS tags\n"
        f"FROM {table} x WHERE x.name IN ({names}) ORDER BY x.{id_col};"
    )


def class_summary_sql(classes):
    names = ", ".join(sql(c["name"]) for c in classes)
    return (
        "SELECT c.class_id AS id, c.name, c.tier, p.name AS parent, c.weapon_type, c.defense_type,\n"
        "  c.attack_type, c.attack_range, c.move_range, c.passive1_name, c.passive1_icon_url\n"
        f"FROM classes c LEFT JOIN classes p ON p.class_id = c.parent_class_id WHERE c.name IN ({names}) ORDER BY c.tier, c.class_id;"
    )


def skill_summary_sql(classes):
    names = ", ".join(sql(c["name"]) for c in classes)
    return (
        "SELECT c.name AS class, cs.unlock_order AS ord, s.name AS skill, s.tp_cost AS tp,\n"
        "  CASE WHEN s.range_min = 0 AND s.range_max = 0 THEN '자신' ELSE CONCAT(s.range_min, '-', s.range_max) END AS `range`,\n"
        "  s.area, COALESCE(s.attack_type, c.attack_type) AS attack, s.allowed_weapon AS weapon, s.cooldown AS cd,\n"
        "  (SELECT GROUP_CONCAT(t.name ORDER BY t.tag_id) FROM skill_tag_map m JOIN tags t ON t.tag_id = m.tag_id WHERE m.skill_id = s.skill_id) AS tags,\n"
        "  s.icon_url IS NOT NULL AS icon\n"
        "FROM classes c JOIN class_skills cs ON cs.class_id = c.class_id JOIN skills s ON s.skill_id = cs.skill_id\n"
        f"WHERE c.name IN ({names}) ORDER BY c.tier, c.class_id, cs.unlock_order;"
    )


def main():
    tags, tag_names = load_tags()
    kinds = [(prefix, load_items(folder, tag_names)) for folder, prefix in KINDS]
    classes = load_classes(tag_names)
    weapons = load_weapons()
    artifacts = load_artifacts()
    characters = load_characters({c["name"] for c in classes}, {w["name"] for w in weapons},
                                 {a["name"] for a in artifacts})
    warn_unknown_links(kinds[0][1], kinds[1][1], classes, weapons, artifacts, characters)

    parts = ["SET NAMES utf8mb4;", "START TRANSACTION;", "", "-- ─── 태그 ───"]
    if tags:
        rows = ", ".join(f"({sql(t['name'])}, {sql(t.get('color', 'gray'))})" for t in tags)
        parts.append(f"INSERT INTO tags (name, color) VALUES {rows} AS new ON DUPLICATE KEY UPDATE color = new.color;")
    for prefix, items in kinds:
        parts.append(f"\n-- ─── {prefix} ({len(items)}개) ───")
        parts.extend(item_sql(prefix, item) for item in items)
    parts.append(f"\n-- ─── class ({len(classes)}개) ───")
    parts.extend(class_sql(c) for c in classes)
    parts.append(f"\n-- ─── exclusive weapon ({len(weapons)}개) ───")
    parts.extend(weapon_sql(w) for w in weapons)
    parts.append(f"\n-- ─── artifact ({len(artifacts)}개) ───")
    parts.extend(artifact_sql(a) for a in artifacts)
    parts.append(f"\n-- ─── character ({len(characters)}개) ───")
    parts.extend(character_sql(c) for c in characters)
    parts += ["", "COMMIT;", ""]
    parts.extend(item_summary_sql(prefix, items) for prefix, items in kinds if items)
    if classes:
        parts.append(class_summary_sql(classes))
        parts.append(skill_summary_sql(classes))
    if weapons:
        parts.append(weapon_summary_sql(weapons))
    if artifacts:
        parts.append(artifact_summary_sql(artifacts))
    if characters:
        parts.append(character_summary_sql(characters))
    print("\n".join(parts))


if __name__ == "__main__":
    try:
        main()
    except (DataError, KeyError) as e:
        print(f"데이터 오류: {e}", file=sys.stderr)
        sys.exit(1)
