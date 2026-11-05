import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load(kind):
    return json.loads((ROOT / 'data' / kind / 'kana.json').read_text())

class KanaDataTests(unittest.TestCase):
    def test_identity(self):
        c = load('characters')[0]
        self.assertEqual(c['releaseDate'], '2025-02-18')
        self.assertEqual(c['appearedIn'], '서풍의 광시곡')
        self.assertEqual(c['artifacts'], ['초과 장전기', '치밀한 준비', '바람 걸음'])
        self.assertNotIn('stats', c)

    def test_base_ultimate_removes_stun_and_reduces_damage(self):
        u = load('characters')[0]['ultimate']
        self.assertEqual([l['step'] for l in u['levels']], [0, 1, 3, 5])
        for i, level in enumerate(u['levels']):
            e = level['effect']
            self.assertIn(f'[{145+i*5}%]', e)
            self.assertIn(f'[{85+i*5}%]', e)
            self.assertEqual('기절' in e, i > 0)
            self.assertEqual('쿨타임' in e, i >= 2)
            self.assertIn(f'[{35 if i == 3 else 30}%]', e)
        self.assertEqual((u['tpCost'], u['range'], u['cooldown']), (5,[2,5],5))

    def test_passive_progression(self):
        levels = load('characters')[0]['passive']['levels']
        self.assertEqual([(l['type'], l['step']) for l in levels], [('각성',3),('각성',4),('각성',5),('각성',6),('발현',2),('발현',4),('발현',6)])
        self.assertNotIn('추가 행동', levels[0]['effect'])
        for i, l in enumerate(levels):
            self.assertIn(f'텐션 업 {i+1}', l['effect'])
            self.assertEqual('뜨거운 응원' in l['effect'], i >= 4)
        buffs = {b['name']:b for b in load('buffs')}
        self.assertEqual(len(buffs['텐션 업']['levels']), 7)
        self.assertEqual(buffs['텐션 업']['maxStack'], 2)
        for i, l in enumerate(buffs['텐션 업']['levels']):
            self.assertEqual('마법' in l['effect'], i < 4)
            self.assertEqual('추가 이동' in l['effect'], i >= 4)

    def test_classes_and_weapon(self):
        self.assertEqual([c['parent'] for c in load('classes')], ['거너','인서전트'])
        w = load('weapons')[0]
        self.assertEqual([s['attack'] for s in w['baseStats']], [364,367,371,375,378,382])
        self.assertEqual([s['critRate'] for s in w['baseStats']], list(range(10,16)))
        for k, effect in enumerate(w['effects']):
            for i, l in enumerate(effect['levels']):
                self.assertIn(f'[{(50 if k else 60)+i*5}%]', l['effect'])
                self.assertEqual('럭키 카나' in l['effect'], k == 0)

if __name__ == '__main__':
    unittest.main()
