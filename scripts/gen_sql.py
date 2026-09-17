#!/usr/bin/env python3
"""data/ 의 JSON(태그·버프·디버프·클래스)을 이름 기준 upsert SQL로 변환해 stdout으로 출력.

- 이름으로 찾아서 없으면 추가, 있으면 갱신 → 여러 번 실행해도 결과 동일
- 버프/디버프의 레벨·태그 매핑은 JSON 내용으로 전부 교체
- iconUrl 키가 없으면 기존 아이콘은 건드리지 않음 (관리자 화면에서 넣은 값 유지)
- 클래스는 기본 정보·패시브만 갱신 (수치 base_hp/base_attack, 스킬은 건드리지 않음)
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
CLASS_KEYS = {"name", "tier", "parent", "weaponType", "defenseType", "attackRange", "moveRange",
              "description", "iconUrl", "passive"}
PASSIVE_KEYS = {"name", "lv1", "lv2"}
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


def load_classes():
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


def warn_unknown_links(buffs, debuffs, classes):
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
        f"attack_range = {sql(cls.get('attackRange'))}",
        f"move_range = {sql(cls.get('moveRange'))}",
        f"description = {sql(cls.get('description'))}",
        f"passive1_name = {sql(passive.get('name'))}",
        f"passive1_lv1 = {sql(passive.get('lv1'))}",
        f"passive1_lv2 = {sql(passive.get('lv2'))}",
    ]
    if "iconUrl" in cls:
        sets.append(f"icon_url = {sql(cls['iconUrl'])}")
    sets.append("updated_at = NOW()")
    out.append(f"UPDATE classes SET {', '.join(sets)} WHERE class_id = @id;")
    return "\n".join(out)


def item_summary_sql(prefix, items):
    table, id_col = f"{prefix}s", f"{prefix}_id"
    names = ", ".join(sql(i["name"]) for i in items)
    return (
        f"SELECT '{prefix}' AS kind, x.{id_col} AS id, x.name,\n"
        f"  CASE x.duration WHEN {PERMANENT_DURATION} THEN '영구' ELSE x.duration END AS duration, x.max_stack,\n"
        f"  (SELECT COUNT(*) FROM {prefix}_levels l WHERE l.{id_col} = x.{id_col}) AS levels,\n"
        f"  (SELECT GROUP_CONCAT(t.name) FROM {prefix}_tag_map m JOIN tags t ON t.tag_id = m.tag_id WHERE m.{id_col} = x.{id_col}) AS tags\n"
        f"FROM {table} x WHERE x.name IN ({names}) ORDER BY x.{id_col};"
    )


def class_summary_sql(classes):
    names = ", ".join(sql(c["name"]) for c in classes)
    return (
        "SELECT c.class_id AS id, c.name, c.tier, p.name AS parent, c.weapon_type, c.defense_type,\n"
        "  c.attack_range, c.move_range, c.passive1_name\n"
        f"FROM classes c LEFT JOIN classes p ON p.class_id = c.parent_class_id WHERE c.name IN ({names}) ORDER BY c.tier, c.class_id;"
    )


def main():
    tags, tag_names = load_tags()
    kinds = [(prefix, load_items(folder, tag_names)) for folder, prefix in KINDS]
    classes = load_classes()
    warn_unknown_links(kinds[0][1], kinds[1][1], classes)

    parts = ["SET NAMES utf8mb4;", "START TRANSACTION;", "", "-- ─── 태그 ───"]
    if tags:
        rows = ", ".join(f"({sql(t['name'])}, {sql(t.get('color', 'gray'))})" for t in tags)
        parts.append(f"INSERT INTO tags (name, color) VALUES {rows} AS new ON DUPLICATE KEY UPDATE color = new.color;")
    for prefix, items in kinds:
        parts.append(f"\n-- ─── {prefix} ({len(items)}개) ───")
        parts.extend(item_sql(prefix, item) for item in items)
    parts.append(f"\n-- ─── class ({len(classes)}개) ───")
    parts.extend(class_sql(c) for c in classes)
    parts += ["", "COMMIT;", ""]
    parts.extend(item_summary_sql(prefix, items) for prefix, items in kinds if items)
    if classes:
        parts.append(class_summary_sql(classes))
    print("\n".join(parts))


if __name__ == "__main__":
    try:
        main()
    except (DataError, KeyError) as e:
        print(f"데이터 오류: {e}", file=sys.stderr)
        sys.exit(1)
