import json
import re
import unittest
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / "data"


def read(kind):
    return json.loads((DATA / kind / "lacid_young.json").read_text())


class YoungLacidTests(unittest.TestCase):
    def test_profile_and_references(self):
        c = read("characters")[0]
        self.assertEqual(c["name"], "라시드 팬드래건(청년)")
        self.assertEqual((c["releaseDate"], c["appearedIn"]), ("2024-05-14", "창세기전2"))
        self.assertNotIn("stats", c)
        old = json.loads((DATA / "characters/lacid.json").read_text())[0]
        self.assertEqual((old["grade"], old["height"]), ("영웅", "153cm"))
        for kind, names in [("classes", c["classTree"]), ("artifacts", c["artifacts"]), ("weapons", [c["exclusiveWeapon"]])]:
            all_names = [x["name"] for p in (DATA / kind).glob("*.json") for x in json.loads(p.read_text())]
            for name in names:
                self.assertEqual(all_names.count(name), 1)
        names = set()
        for kind in ["buffs", "debuffs"]:
            for p in (DATA / kind).glob("*.json"):
                for b in json.loads(p.read_text()):
                    names.add(b["name"])
                    names.update(l.get("name", f'{b["name"]} {l["level"]}') for l in b.get("levels", []))
        for kind in ["characters", "classes", "buffs", "debuffs", "weapons", "artifacts"]:
            for name in re.findall(r"\[([^\[\]]+)\]\{(?:green|orange)\}", json.dumps(read(kind), ensure_ascii=False)):
                self.assertIn(name, names)

    def test_passive_progression_and_trigger(self):
        levels = read("characters")[0]["passive"]["levels"]
        self.assertEqual([(l["type"], l["step"]) for l in levels], [("각성", s) for s in [3,4,5,6]] + [("발현", s) for s in [2,4,6]])
        for i, l in enumerate(levels):
            text = l["effect"]
            self.assertIn("아군에게 액티브 스킬로 버프를 받으면 턴 당 한번", text)
            self.assertIn(f'공격력이 [{[10,15,20,25,30,35,40][i]}%]', text)
            self.assertIn(f'공격력의 [{[15,20,25,30,40,50,60][i]}%]', text)
            self.assertEqual("쿨타임이 가장 긴" in text, i >= 2)
            self.assertEqual("스킬 사거리" in text, i >= 4)
            self.assertEqual("체력이" in text, i >= 5)
        resolve = read("buffs")[0]
        self.assertEqual((resolve["duration"], resolve["maxStack"]), ("영구", 2))

    def test_ultimate(self):
        u = read("characters")[0]["ultimate"]
        self.assertEqual((u["tpCost"], u["cooldown"], u["range"]), (5, 5, [3,3]))
        self.assertEqual([l["step"] for l in u["levels"]], [0,1,3,5])
        for l, power, chance in zip(u["levels"], [125,130,135,140], [35,40,45,50]):
            self.assertIn(f"공격력의 [{power}%]", l["effect"])
            self.assertIn(f"[{chance}%]{{red}}의 확률", l["effect"])
            self.assertIn("허용 무기: 검, 대검.", l["effect"])

    def test_classes_and_effects(self):
        saint, dragon, command = read("classes")
        self.assertEqual([c["parent"] for c in [saint, dragon, command]], ["소드맨","나이트","나이트"])
        self.assertEqual(dragon["skills"][0]["attackType"], "마법")
        self.assertNotIn("allowedWeapon", dragon["skills"][0])
        for n in [1,2]:
            self.assertIn("추가 공격이나 스킬 사용", command["passive"][f"lv{n}"])
            self.assertIn("디버프를 [1]", command["passive"][f"lv{n}"])
        self.assertEqual(read("debuffs")[0]["duration"], 2)
        blessing = next(b for b in read("buffs") if b["name"] == "자비에르의 축복")
        self.assertEqual(blessing["tags"], ["해제 불가"])
        for l, n in zip(blessing["levels"], [10,15,15,20]):
            self.assertIn(f"빙한 저항 [+{n}%]", l["effect"])
        for l, distance in zip(read("artifacts")[0]["levels"], [2,2,3,3]):
            self.assertIn(f"주위 [{distance}]", l["effect"])

    def test_weapon(self):
        w = read("weapons")[0]
        self.assertEqual([s["maxHp"] for s in w["baseStats"]], [122,123,124,126,127,128])
        self.assertEqual([s["attack"] for s in w["baseStats"]], [364,367,371,375,378,382])
        for effect in w["effects"]:
            self.assertEqual([l["step"] for l in effect["levels"]], [1,2,3,4,5,6])
            for i, l in enumerate(effect["levels"]):
                self.assertIn(f'피해량이 [{[3,3,4,4,5,5][i]}%]', l["effect"])
                self.assertIn("쿨타임 [1]", l["effect"])
                if effect["type"] == "전용":
                    self.assertIn(f"치명타 확률이 [{i+5}%]", l["effect"])
                    self.assertIn("후 [30%]", l["effect"])
                else:
                    self.assertNotIn("치명타 확률", l["effect"])
                    self.assertIn("후 [15%]", l["effect"])


if __name__ == "__main__":
    unittest.main()
