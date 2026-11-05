import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load(kind):
    return json.loads((ROOT/'data'/kind/'phantom_sharnhorst.json').read_text())

class PhantomSharnhorstTests(unittest.TestCase):
    def test_identity_and_ultimate(self):
        c = load('characters')[0]
        self.assertEqual(c['releaseDate'], '2025-03-04')
        self.assertEqual(c['appearedIn'], '서풍의 광시곡')
        self.assertNotIn('stats', c)
        u = c['ultimate']
        self.assertEqual([l['step'] for l in u['levels']], [0,1,3,5])
        for i, l in enumerate(u['levels']):
            self.assertIn(f'[{220+10*i}%]', l['effect'])
            self.assertIn('반격당하지 않습니다', l['effect'])
        self.assertEqual((u['tpCost'],u['range'],u['cooldown']), (5,[1,4],5))

    def test_passive_unlocks(self):
        ls = load('characters')[0]['passive']['levels']
        self.assertEqual([(l['type'],l['step']) for l in ls], [('각성',3),('각성',4),('각성',5),('각성',6),('발현',2),('발현',4),('발현',6)])
        for i,l in enumerate(ls):
            self.assertIn(f'기만의 표식 {i+1}',l['effect'])
            self.assertEqual('버프를 복사' in l['effect'],i>=3)
            self.assertEqual('[집중]' in l['effect'],i>=5)

    def test_classes_and_artifacts(self):
        cls=load('classes')
        self.assertEqual([c['parent'] for c in cls], ['로그','킬러','트릭스터'])
        self.assertEqual([c['skills'][0]['tpCost'] for c in cls],[2,2,3])
        a=load('artifacts')[0]
        self.assertEqual([l['step'] for l in a['levels']],[3,4,5,6])
        self.assertNotIn('피의 결의',a['levels'][1]['effect'])
        self.assertIn('피의 결의 2',a['levels'][3]['effect'])

    def test_weapon_variants(self):
        w=load('weapons')[0]
        self.assertEqual([s['attack'] for s in w['baseStats']],[381,384,388,392,395,399])
        ds={d['name']:d for d in load('debuffs')}
        for i in range(6):
            self.assertNotIn('주문력',ds['신경독']['levels'][i]['effect'])
            self.assertEqual('주문력' in ds['신경독 (전용)']['levels'][i]['effect'],i>=2)
        for i,l in enumerate(w['effects'][0]['levels']):
            self.assertEqual('공격력 [+' in l['effect'],i>=4)

if __name__ == '__main__':
    unittest.main()
