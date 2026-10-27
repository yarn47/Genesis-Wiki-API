import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
def load(kind):
    return json.loads((ROOT / 'data' / kind / 'clausewitz.json').read_text())

class ClausewitzDataTests(unittest.TestCase):
    def test_identity_and_levels(self):
        c = load('characters')[0]
        self.assertEqual(c['releaseDate'], '2024-09-17')
        self.assertEqual(c['appearedIn'], '서풍의 광시곡')
        self.assertEqual(c['classTree'], ['메이지','매지션','택티션','아크메이지','윈드윌더','스키머'])
        self.assertEqual([(l['type'], l['step']) for l in c['passive']['levels']], [('각성',3),('각성',4),('각성',5),('각성',6),('발현',2),('발현',4),('발현',6)])
        for l, v in zip(c['ultimate']['levels'], [110,120,130,140]):
            self.assertIn(f'[{v}%]', l['effect'])
            self.assertIn('[50%]', l['effect'])
            self.assertIn('저항력을 무시', l['effect'])
        self.assertEqual([l['step'] for l in c['ultimate']['levels']], [0,1,3,5])

    def test_passive_values(self):
        b = {x['name']: x for x in load('buffs')}
        for name in ['단단한 전선','전장의 깃발','마력 장막']:
            self.assertEqual([l['level'] for l in b[name]['levels']], list(range(1,8)))
            self.assertTrue(all(l['duration']==2 for l in b[name]['levels']))
        self.assertIn('[-70%]', b['단단한 전선']['levels'][-1]['effect'])
        self.assertIn('[150%]', b['마력 장막']['levels'][-1]['effect'])
        self.assertIn('[-65%]', b['마력 장막']['levels'][-1]['effect'])
        p = load('characters')[0]['passive']['levels']
        self.assertIn('[2]{yellow}턴 동안 이동 방해 면역', p[4]['effect'])
        self.assertIn('[3]{yellow}턴 동안 이동 방해 면역', p[5]['effect'])
        self.assertNotIn('영구', p[6]['effect'])

    def test_class_connections_and_summons(self):
        c = load('classes')
        self.assertEqual([x['parent'] for x in c], ['메이지','매지션','택티션'])
        self.assertEqual(c[1]['skills'][0]['element'], '전격')
        self.assertNotIn('allowedWeapon', c[1]['skills'][0])
        b = {x['name']: x for x in load('buffs')}
        self.assertNotIn('위치 사수', b)
        self.assertIn('[-30%]', b['위치 사수 (신비 병사)']['description'])
        self.assertIn('[위치 사수 (신비 병사)]', b['신비 병사']['description'])

    def test_weapon(self):
        w = load('weapons')[0]
        self.assertEqual([x['maxHp'] for x in w['baseStats']], [116,117,118,120,121,122])
        self.assertEqual([x['spellAttack'] for x in w['baseStats']], [381,384,388,392,395,399])
        self.assertEqual([x['magicPen'] for x in w['baseStats']], [15,17,19,21,23,25])
        self.assertIn('[80%]', w['effects'][0]['levels'][-1]['effect'])
        b = {x['name']: x for x in load('buffs')}
        self.assertTrue(all(x['maxStack']==2 for x in b['역동하는 마력']['levels']))
        self.assertNotIn('범위 피해', b['역동하는 마력']['levels'][1]['effect'])
        self.assertIn('[+5%]', b['역동하는 마력']['levels'][2]['effect'])
        self.assertIn('[+15%]', b['비산하는 힘']['levels'][-1]['effect'])

if __name__ == '__main__':
    unittest.main()
