#!/usr/bin/env python3
"""data/ 의 JSON(태그·버프·디버프)을 이름 기준 upsert SQL로 변환해 stdout으로 출력.

- 이름으로 찾아서 없으면 추가, 있으면 갱신 → 여러 번 실행해도 결과 동일
- 레벨/태그 매핑은 JSON 내용으로 전부 교체
- iconUrl 키가 없으면 기존 아이콘은 건드리지 않음 (관리자 화면에서 넣은 값 유지)
- 전체가 하나의 트랜잭션이라 중간에 에러가 나면 아무것도 반영되지 않음
"""
import json
import re
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"

TAG_COLORS = {"gray", "red", "orange", "yellow", "green", "blue", "purple"}
TEXT_TAG = re.compile(r"\[([^\]]+)\]\{(\w+)\}")
TEXT_TAG_COLORS = {"red", "yellow", "green", "orange", "blue", "purple"}

# (data 폴더, 테이블 접두어)
KINDS = [("buffs", "buff"), ("debuffs", "debuff")]

ITEM_KEYS = {"name", "description", "iconUrl", "duration", "maxStack", "tags", "levels"}
LEVEL_KEYS = {"level", "name", "effect", "duration", "maxStack"}


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


def check_text(where, text):
    if text is None:
        return
    for label, color in TEXT_TAG.findall(text):
        if color not in TEXT_TAG_COLORS:
            raise DataError(f"{where}: 알 수 없는 색 태그 [{label}]{{{color}}}")


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
    for path in sorted((DATA / folder).glob("*.json")):
        rel = path.relative_to(DATA)
        for item in load_json(path):
            where = f"{rel} '{item.get('name')}'"
            unknown = set(item) - ITEM_KEYS
            if unknown:
                raise DataError(f"{where}: 알 수 없는 항목 {sorted(unknown)}")
            if not item.get("name"):
                raise DataError(f"{rel}: name 없는 항목")
            if item["name"] in seen:
                raise DataError(f"{where}: {seen[item['name']]} 에도 같은 이름이 있음")
            seen[item["name"]] = rel
            for tag in item.get("tags", []):
                if tag not in tag_names:
                    raise DataError(f"{where}: tags.json에 없는 태그 '{tag}'")
            check_text(where, item.get("description"))
            levels = set()
            for lvl in item.get("levels", []):
                unknown = set(lvl) - LEVEL_KEYS
                if unknown:
                    raise DataError(f"{where} 레벨 {lvl.get('level')}: 알 수 없는 항목 {sorted(unknown)}")
                if lvl["level"] in levels:
                    raise DataError(f"{where}: 레벨 {lvl['level']} 중복")
                levels.add(lvl["level"])
                check_text(f"{where} 레벨 {lvl['level']}", lvl.get("effect"))
            items.append(item)
    return items


def item_sql(prefix, item):
    table, id_col = f"{prefix}s", f"{prefix}_id"
    name = sql(item["name"])
    levels = sorted(item.get("levels", []), key=lambda l: l["level"])
    has_levels = bool(levels)

    out = [
        f"-- {item['name']}",
        f"SET @id = (SELECT {id_col} FROM {table} WHERE name = {name});",
        f"INSERT INTO {table} (name, max_stack, has_levels, created_at, updated_at) "
        f"SELECT {name}, 1, {sql(has_levels)}, NOW(), NOW() FROM DUAL WHERE @id IS NULL;",
        "SET @id = COALESCE(@id, LAST_INSERT_ID());",
    ]

    sets = [
        f"description = {sql(item.get('description'))}",
        f"duration = {sql(item.get('duration'))}",
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
            f"(@id, {sql(l['level'])}, {sql(l.get('name') or '%s %d' % (item['name'], l['level']))}, "
            f"{sql(l.get('effect'))}, {sql(l.get('duration'))}, {sql(l.get('maxStack'))})"
            for l in levels
        )
        out.append(f"INSERT INTO {prefix}_levels ({id_col}, level, level_name, effect_text, duration, max_stack) VALUES\n{rows};")

    out.append(f"DELETE FROM {prefix}_tag_map WHERE {id_col} = @id;")
    if item.get("tags"):
        tag_list = ", ".join(sql(t) for t in item["tags"])
        out.append(f"INSERT INTO {prefix}_tag_map ({id_col}, tag_id) SELECT @id, tag_id FROM tags WHERE name IN ({tag_list});")
    return "\n".join(out)


def summary_sql(prefix, items):
    if not items:
        return ""
    table, id_col = f"{prefix}s", f"{prefix}_id"
    names = ", ".join(sql(i["name"]) for i in items)
    return (
        f"SELECT '{prefix}' AS kind, x.{id_col} AS id, x.name, x.duration, x.max_stack,\n"
        f"  (SELECT COUNT(*) FROM {prefix}_levels l WHERE l.{id_col} = x.{id_col}) AS levels,\n"
        f"  (SELECT GROUP_CONCAT(t.name) FROM {prefix}_tag_map m JOIN tags t ON t.tag_id = m.tag_id WHERE m.{id_col} = x.{id_col}) AS tags\n"
        f"FROM {table} x WHERE x.name IN ({names}) ORDER BY x.{id_col};"
    )


def main():
    tags, tag_names = load_tags()
    kinds = [(prefix, load_items(folder, tag_names)) for folder, prefix in KINDS]

    parts = ["SET NAMES utf8mb4;", "START TRANSACTION;", "", "-- ─── 태그 ───"]
    if tags:
        rows = ", ".join(f"({sql(t['name'])}, {sql(t.get('color', 'gray'))})" for t in tags)
        parts.append(f"INSERT INTO tags (name, color) VALUES {rows} AS new ON DUPLICATE KEY UPDATE color = new.color;")
    for prefix, items in kinds:
        parts.append(f"\n-- ─── {prefix} ({len(items)}개) ───")
        parts.extend(item_sql(prefix, item) for item in items)
    parts += ["", "COMMIT;", ""]
    parts.extend(s for s in (summary_sql(prefix, items) for prefix, items in kinds) if s)
    print("\n".join(parts))


if __name__ == "__main__":
    try:
        main()
    except (DataError, KeyError) as e:
        print(f"데이터 오류: {e}", file=sys.stderr)
        sys.exit(1)
