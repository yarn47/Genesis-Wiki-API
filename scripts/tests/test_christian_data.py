import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load(kind):
    return json.loads((ROOT / 'data' / kind / 'christian.json').read_text())

class ChristianDataTests(unittest.TestCase):
    def test_identity_and_ultimate(self):
        c = load('characters')[0]
        self.assertEqual(c['name'], '크리스티앙 데 메디치')
        self.assertEqual(c['releaseDate'], '2024-10-15')
        self.assertEqual(c['appearedIn'], '창세기전3')
        self.assertEqual(c['element'], '자유의불꽃')
        u = c['ultimate']
        self.assertEqual(u['range'], [1,4])
        self.assertEqual(u['element'], '전격')
        self.assertEqual([x['step'] for x in u['levels']], [0,1,3,5])
        for x,n in zip(u['levels'], [100,110,120,130]):
            self.assertIn(f'[{n}%]', x['effect'])
            self.assertIn('[4]{red}칸', x['effect'])
            self.assertIn('[감전]{orange}', x['effect'])

    def test_passive_progression(self):
        c = load('characters')[0]
        levels = c['passive']['levels']
        self.assertEqual([(x['type'],x['step']) for x in levels], [('각성',3),('각성',4),('각성',5),('각성',6),('발현',2),('발현',4),('발현',6)])
        self.assertNotIn('한 번 더', levels[0]['effect'])
        for x,n in zip(levels[1:], [1,2,2,2,2,3]):
            self.assertIn(f'최대 [{n}]', x['effect'])
        buffs = {x['name']:x for x in load('buffs')}
        a = buffs['아드레날린']['levels']
        self.assertEqual([x['maxStack'] for x in a], [5,6,7,8,8,8,8])
        for x,atk,crit in zip(a,[2,2,2,2,3,3,4],[4,4,4,4,4,5,5]):
            self.assertIn(f'공격력 [{atk}%]', x['effect'])
            self.assertIn(f'치명타 확률 [{crit}%]', x['effect'])
        for x,n in zip(buffs['확인 사살']['levels'],[80,80,80,80,85,90,90]):
            self.assertIn(f'[{n}%]', x['effect'])
            self.assertIn('탄환이 없어도', x['effect'])

    def test_classes_and_shared_artifacts(self):
        cls = load('classes')
        self.assertEqual([x['parent'] for x in cls], ['거너','ISS 파일럿'])
        self.assertEqual([x['moveRange'] for x in cls], [4,4])
        self.assertNotIn('tpCost', cls[0]['skills'][0])
        self.assertEqual(cls[1]['skills'][0]['range'], '자신')
        self.assertEqual(load('characters')[0]['artifacts'], ['초과 장전기','초기 철갑 탄창','바람 걸음'])

    def test_weapon_milestones(self):
        w = load('weapons')[0]
        self.assertEqual([x['maxHp'] for x in w['baseStats']], [116,117,118,120,121,122])
        self.assertEqual([x['attack'] for x in w['baseStats']], [364,367,371,375,378,382])
        for x in w['effects'][0]['levels']:
            self.assertEqual('추가 공격이나 스킬 사용' in x['effect'], x['step'] >= 3)
            self.assertEqual('최대치까지' in x['effect'], x['step'] >= 5)
            self.assertIn('쿨타임 [3]', x['effect'])
        self.assertEqual(w['effects'][1]['type'], '일반')
        for b in load('buffs'):
            if b['name'] in ['과감한 행동력','준비 완료']:
                for x in b['levels']:
                    self.assertEqual(x['duration'],1)
                    self.assertIn(f'[+{x["level"]+4}%]',x['effect'])

if __name__ == '__main__':
    unittest.main()
