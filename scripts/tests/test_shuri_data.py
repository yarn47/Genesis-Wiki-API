import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2] / 'data'
def read(kind):
    return json.loads((ROOT / kind / 'shuri.json').read_text())

class ShuriTests(unittest.TestCase):
    def test_character_and_progression(self):
        c = read('characters')[0]
        self.assertEqual(c['name'], '슈리 스탐가르드')
        self.assertEqual(c['artifacts'], ['최상의 상태', '나선 문장', '광란의 파동'])
        levels = c['passive']['levels']
        self.assertEqual([(x['type'], x['step']) for x in levels], [('각성', n) for n in [3,4,5,6]] + [('발현', n) for n in [2,4,6]])
        for i, l in enumerate(levels):
            self.assertEqual('적 공격 시' in l['effect'], i >= 2)
            self.assertEqual('디버프 피해' in l['effect'], i >= 4)
        self.assertEqual([l['step'] for l in c['ultimate']['levels']], [0,1,3,5])
        for l, v in zip(c['ultimate']['levels'], [130,140,150,160]):
            self.assertIn(f'[{v}%]', l['effect'])

    def test_classes_and_shared_references(self):
        classes = read('classes')
        self.assertEqual(len(classes), 6)
        self.assertEqual(sum(len(c['skills']) for c in classes), 8)
        self.assertEqual(set(read('characters')[0]['classTree']), {c['name'] for c in classes})
        self.assertEqual(next(c for c in classes if c['name']=='로얄랜서')['parent'], '랜서')
        for kind in ['buffs','debuffs','classes','artifacts']:
            names = [v['name'] for p in (ROOT/kind).glob('*.json') for v in json.loads(p.read_text())]
            self.assertEqual(len(names), len(set(names)))

    def test_weapon(self):
        w = read('weapons')[0]
        self.assertEqual([s['maxHp'] for s in w['baseStats']], [127,128,129,131,132,133])
        self.assertEqual([s['attack'] for s in w['baseStats']], [347,350,354,358,361,365])
        for i, l in enumerate(w['effects'][0]['levels']):
            self.assertIn(f'[{30+2*i}%]', l['effect'])
            self.assertIn(f'[{50+10*i}%]', l['effect'])
        for e in w['effects']:
            self.assertEqual([l['step'] for l in e['levels']], list(range(1,7)))

    def test_buffs_and_artifacts(self):
        buffs = read('buffs')
        for row, values in zip(buffs[:2], [[5,7,9,10,15,17,20],[20,25,30,40,50,55,60]]):
            for l, v in zip(row['levels'], values): self.assertIn(f'[+{v}%]', l['effect'])
        for a, values in zip(read('artifacts'), [[10,20,30,40],[15,20,25,30]]):
            self.assertEqual([l['step'] for l in a['levels']], [3,4,5,6])
            for l,v in zip(a['levels'], values): self.assertIn(f'[+{v}%]', l['effect'])
        for l in read('artifacts')[0]['levels']: self.assertIn('[3]{yellow}턴', l['effect'])

if __name__ == '__main__': unittest.main()
