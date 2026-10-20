import json
import re
import unittest
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / "data"


def read(kind):
    return json.loads((DATA / kind / "elizabeth.json").read_text())


class ElizabethTests(unittest.TestCase):
    def test_profile_and_unique_references(self):
        c = read("characters")[0]
        self.assertEqual((c["releaseDate"], c["appearedIn"]), ("2024-05-28", "템페스트"))
        self.assertEqual((c["birthYear"], c["height"], c["cv"]), ("에스겔력 1254년", "170cm", "김가령"))
        self.assertNotIn("stats", c)
        for kind, names in [("classes", c["classTree"]), ("artifacts", c["artifacts"]), ("weapons", [c["exclusiveWeapon"]])]:
            available = [x["name"] for p in (DATA / kind).glob("*.json") for x in json.loads(p.read_text())]
            for name in names:
                self.assertEqual(available.count(name), 1)
        available = set()
        for kind in ["buffs", "debuffs"]:
            for p in (DATA / kind).glob("*.json"):
                for b in json.loads(p.read_text()):
                    available.add(b["name"])
                    available.update(l.get("name", f'{b["name"]} {l["level"]}') for l in b.get("levels", []))
        for kind in ["characters", "classes", "buffs", "debuffs", "weapons", "artifacts"]:
            for name in re.findall(r"\[([^\[\]]+)\]\{(?:green|orange)\}", json.dumps(read(kind), ensure_ascii=False)):
                self.assertIn(name, available)

    def test_passive_and_blank(self):
        levels = read("characters")[0]["passive"]["levels"]
        self.assertEqual([(l["type"], l["step"]) for l in levels],
                         [("각성", s) for s in [3, 4, 5, 6]] + [("발현", s) for s in [2, 4, 6]])
        for i, (level, heal) in enumerate(zip(levels, [20, 30, 35, 45, 50, 55, 60])):
            self.assertIn("게임 중 한번", level["effect"])
            self.assertIn("공격력의 [" + str(heal) + "%]", level["effect"])
            self.assertIn(f"블랭크 {i+1}", level["effect"])
            self.assertIn("전투 후" if i == 6 else "전투 공격 후", level["effect"])
        blank = read("debuffs")[0]["levels"]
        self.assertEqual([l["duration"] for l in blank], [3, 3, 2, 2, 2, 2, 2])
        for i, level in enumerate(blank):
            self.assertEqual("받는 피해량" in level["effect"], i < 4)
            self.assertEqual("체력 회복" in level["effect"], i >= 5)
            self.assertEqual("모든 디버프" in level["effect"], i == 6)
        petals = read("buffs")[0]["levels"]
        for i, (level, damage) in enumerate(zip(petals, [5, 7, 8, 10, 13, 16, 20])):
            self.assertEqual((level["duration"], level["maxStack"]), ("영구", 4))
            self.assertIn(f"[+{damage}%]", level["effect"])
            self.assertEqual("쿨타임" in level["effect"], i >= 4)

    def test_ultimate(self):
        u = read("characters")[0]["ultimate"]
        self.assertEqual((u["tpCost"], u["cooldown"], u["range"]), (5, 5, [1, 1]))
        self.assertEqual([l["step"] for l in u["levels"]], [0, 1, 3, 5])
        for i, level in enumerate(u["levels"]):
            self.assertIn(f"[{220+10*i}%]", level["effect"])
            self.assertIn(f"[{50+10*i}%]", level["effect"])
            self.assertIn("반격당하지 않습니다", level["effect"])

    def test_classes_and_artifact(self):
        inheritor, crimson, princess = read("classes")
        self.assertEqual([x["parent"] for x in [inheritor, crimson, princess]], ["파이터", "나이트", "인헤리터"])
        self.assertEqual(crimson["skills"][0]["attackType"], "마법")
        self.assertIn("자신의 디버프 [2]", crimson["skills"][0]["effect"])
        self.assertIn("적의 버프 [2]", crimson["skills"][0]["effect"])
        self.assertIn("대형 몬스터", princess["skills"][0]["effect"])
        self.assertIn("추가로 공격하거나 스킬", inheritor["skills"][0]["effect"])
        for l, n in zip(read("artifacts")[0]["levels"], [15, 30, 45, 60]):
            self.assertIn(f"[+{n}%]", l["effect"])
            self.assertIn("[치유 불가]", l["effect"])

    def test_weapon(self):
        w = read("weapons")[0]
        self.assertEqual([s["maxHp"] for s in w["baseStats"]], [130, 131, 132, 134, 135, 136])
        self.assertEqual([s["attack"] for s in w["baseStats"]], [342, 345, 349, 353, 356, 360])
        for effect in w["effects"]:
            self.assertEqual([l["step"] for l in effect["levels"]], list(range(1, 7)))
            for i, l in enumerate(effect["levels"]):
                self.assertIn(f"[{10+i}%]", l["effect"])
                exclusive = effect["type"] == "전용"
                self.assertEqual("주문력" in l["effect"], exclusive)
                self.assertEqual("블랭크 지속시간" in l["effect"], exclusive and i >= 4)
                self.assertEqual("받는 피해" in l["effect"], exclusive)


if __name__ == "__main__":
    unittest.main()
