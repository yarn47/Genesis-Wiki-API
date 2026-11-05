import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load(kind):
    return json.loads((ROOT / 'data' / kind / 'silver.json').read_text())

class SilverDataTests(unittest.TestCase):
    def test_identity(self):
        c = load('characters')[0]
        self.assertEqual(c['releaseDate'], '2025-02-04')
        self.assertEqual(c['appearedIn'], '서풍의 광시곡')
        self.assertEqual((c['faction'], c['subFaction']), ('무소속', '제피르팰컨'))
        self.assertNotIn('stats', c)
        self.assertEqual(c['artifacts'], ['바람 걸음', '전사의 정수', '생명의 맥동'])

    def test_ultimate(self):
        u = load('characters')[0]['ultimate']
        self.assertEqual([l['step'] for l in u['levels']], [0, 1, 3, 5])
        self.assertEqual((u['tpCost'], u['range'], u['cooldown']), (5, [1,5], 5))
        for i, l in enumerate(u['levels']):
            self.assertIn(f'[{190+i*20}%]', l['effect'])
            self.assertEqual('날카로운 시선' in l['effect'], i >= 2)
            self.assertIn('반격하거나 호위할 수 없습니다', l['effect'])

    def test_passive_progression(self):
        ls = load('characters')[0]['passive']['levels']
        self.assertEqual([(l['type'],l['step']) for l in ls], [('각성',3),('각성',4),('각성',5),('각성',6),('발현',2),('발현',4),('발현',6)])
        for l, chance in zip(ls, [50,60,70,80,90]):
            self.assertIn(f'[{chance}%]', l['effect'])
        for l in ls[5:]:
            self.assertNotIn('확률로', l['effect'])
        for l in ls:
            self.assertIn('이동 제어 디버프가 없을 경우', l['effect'])
            self.assertIn('추가 행동', l['effect'])

    def test_class_connections(self):
        cs = load('classes')
        self.assertEqual([c['parent'] for c in cs], ['레인저','커세어','커세어'])
        self.assertEqual([c['skills'][0]['cooldown'] for c in cs], [1,1,3])
        self.assertEqual(cs[2]['skills'][0]['range'], [2,7])
        b = {x['name']:x for x in load('buffs')}
        self.assertNotIn('무력 탈취', b['하늘 감시자']['levels'][0]['effect'])
        self.assertIn('무력 탈취', b['하늘 감시자']['levels'][1]['effect'])
        self.assertEqual((b['무력 탈취']['duration'], b['무력 탈취']['maxStack']), (2,4))
        d = load('debuffs')[0]
        self.assertEqual((d['duration'], d['maxStack']), (2,2))

    def test_weapon(self):
        w = load('weapons')[0]
        self.assertEqual([s['maxHp'] for s in w['baseStats']], [141,142,143,145,146,147])
        self.assertEqual([s['attack'] for s in w['baseStats']], [316,319,323,327,330,334])
        self.assertEqual([s['physPen'] for s in w['baseStats']], [10,11,12,13,14,15])
        ls = w['effects'][0]['levels']
        for l, cooldown in zip(ls, [3,3,3,2,2,2]):
            self.assertIn(f'쿨타임 [{cooldown}]', l['effect'])
        buffs = {x['name']:x for x in load('buffs')}
        ls = buffs['불공정 거래']['levels']
        for i, l in enumerate(ls):
            self.assertEqual('훔칩니다' in l['effect'], i >= 3)
            self.assertNotIn('duration', l)
        self.assertIn('모두 훔칩니다', ls[-1]['effect'])

if __name__ == '__main__':
    unittest.main()
