import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
def load(kind):
    return json.loads((ROOT / 'data' / kind / 'jane.json').read_text())

class JaneDataTests(unittest.TestCase):
    def test_identity(self):
        c = load('characters')[0]
        self.assertEqual(c['releaseDate'], '2024-10-29')
        self.assertEqual(c['appearedIn'], '템페스트')
        self.assertEqual(c['faction'], '아스타니아')
        self.assertEqual(c['subFaction'], '템페스트 서커스단')
        self.assertNotIn('stats', c)
        self.assertTrue(c['published'])

    def test_passive_conditions(self):
        levels = load('characters')[0]['passive']['levels']
        self.assertEqual(len(levels), 7)
        for i, level in enumerate(levels):
            self.assertEqual('적이 남성이라면' in level['effect'], i < 2)
            self.assertIn('대상이 남성이라면', level['effect'])
            self.assertEqual('퀵 드로우' in level['effect'], i >= 4)
        buffs = {b['name']:b for b in load('buffs')}
        self.assertEqual(buffs['팜므파탈']['maxStack'], 4)
        self.assertEqual([x['maxStack'] for x in buffs['격발 준비']['levels']], [3,3,2])

    def test_classes(self):
        classes = load('classes')
        self.assertEqual([c['parent'] for c in classes], ['거너','에이전트','에이전트'])
        for c in classes:
            self.assertEqual(c['attackRange'], 4)
            self.assertEqual(c['moveRange'], 3)
            self.assertTrue(c['passive']['lv2'])
        specialist = classes[1]
        self.assertIn('[4]', specialist['passive']['lv1'])
        self.assertIn('[엄폐 사격]', specialist['passive']['lv2'])
        self.assertEqual(specialist['skills'][0]['name'], '전술탄 장전')
        self.assertEqual(classes[2]['skills'][0]['range'], [3,7])

    def test_weapon(self):
        w = load('weapons')[0]
        self.assertEqual([s['maxHp'] for s in w['baseStats']], [116,117,118,120,121,122])
        self.assertEqual([s['attack'] for s in w['baseStats']], [364,367,371,375,378,382])
        for lvl in w['effects'][0]['levels']:
            count = 2 if lvl['step'] >= 5 else 1
            self.assertIn(f'[{count}]{{yellow}}중첩', lvl['effect'])
            self.assertIn('쿨타임 [2]', lvl['effect'])
        debuffs = {b['name']:b for b in load('debuffs')}
        for name in ['악몽','소름 돋는 기운']:
            self.assertEqual([l['maxStack'] for l in debuffs[name]['levels']], [3,3,4,5,6,7])

    def test_ultimate_and_artifact(self):
        c = load('characters')[0]
        u = c['ultimate']
        self.assertEqual(u['range'], [1,5])
        self.assertEqual([l['step'] for l in u['levels']], [0,1,3,5])
        for lvl, damage, hp, cap in zip(u['levels'], [150,160,170,180], [5,6,7,8], [110,120,130,140]):
            for value in [damage,hp,cap]:
                self.assertIn(f'[{value}%]',lvl['effect'])
            self.assertIn('탄환을 소모하지 않습니다',lvl['effect'])
        self.assertEqual(c['artifacts'], ['초과 장전기','초기 철갑 탄창','혼돈의 파편'])
        for l in load('artifacts')[0]['levels']:
            self.assertEqual('이동력' in l['effect'], l['step'] >= 5)

if __name__ == '__main__':
    unittest.main()
