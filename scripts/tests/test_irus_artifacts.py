import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]

def read(path):
    return json.loads((ROOT / 'data' / path).read_text())

class IrusArtifactTests(unittest.TestCase):
    """Game screenshots 18–20 and 6233–6251, not wiki-derived expectations."""

    def test_retribution_counter_damage_and_cooldowns(self):
        artifact = next(a for a in read('artifacts/irus.json') if a['name'] == '응보의 문장')
        self.assertEqual([l['step'] for l in artifact['levels']], [3, 4, 5, 6])
        for level, damage, cooldown in zip(artifact['levels'], [20, 30, 40, 50], [2, 2, 1, 1]):
            self.assertIn(f'반격 피해량 [+{damage}%]{{red}}', level['effect'])
            self.assertIn(f'쿨타임 [{cooldown}]{{yellow}}', level['effect'])

    def test_shard_penetration_and_hp_boundaries(self):
        artifact = next(a for a in read('artifacts/irus.json') if a['name'] == '파멸의 파편')
        for level, value in zip(artifact['levels'], [15, 20, 25, 30]):
            self.assertIn(f'물리 관통 [+{value}%]{{red}}', level['effect'])
        buff = next(b for b in read('buffs/fighter_line.json') if b['name'] == '파멸의 파편')
        for level, values in zip(buff['levels'], [(10,20,30),(13,26,40),(16,32,50),(20,40,60)]):
            for boundary in ('[100%]{red}미만 [60%]{red}이상', '[60%]{red}미만 [20%]{red}이상', '[20%]{red}미만'):
                self.assertIn(boundary, level['effect'])
            for value in values:
                self.assertIn(f'[{value}%]{{red}} 증가', level['effect'])

    def test_pulse_conditions_and_values(self):
        artifact = next(a for a in read('artifacts/irus.json') if a['name'] == '생명의 맥동')
        for level in artifact['levels']:
            self.assertIn('다른 아군이 없고 보호막을 가지고 있지 않다면', level['effect'])
            self.assertIn('[2]{yellow}턴', level['effect'])
        buff = next(b for b in read('buffs/fighter_line.json') if b['name'] == '생명의 맥동')
        for level, base, tp in zip(buff['levels'], [10,15,20,25], [2,3,4,5]):
            self.assertIn(f'최대 체력의 [{base}%]{{red}} + 남은 TP당 최대 체력의 [{tp}%]{{red}} 보호막', level['effect'])
            self.assertIn(f'남은 TP당 최대 체력의 [{tp}%]{{red}}만큼 체력 회복', level['effect'])
        self.assertEqual(buff['duration'], 2)
        self.assertIn('해제 불가', buff['tags'])

    def test_weapon_image_is_connected(self):
        weapon = read('weapons/irus.json')[0]
        self.assertEqual(weapon['iconUrl'], '/icons/weapons/myeongwang_sword.png')

if __name__ == '__main__':
    unittest.main()
