import json
from pathlib import Path
import unittest

DATA = Path(__file__).resolve().parents[2] / 'data'
def read(kind):
    return json.loads((DATA / kind / 'may_nautilen.json').read_text())

class MayTests(unittest.TestCase):
    def test_profile_and_shared_references(self):
        c=read('characters')[0]
        self.assertEqual((c['releaseDate'],c['appearedIn']),('2024-04-02','창세기전'))
        self.assertNotIn('stats',c)
        for kind,names in [('classes',c['classTree']),('artifacts',c['artifacts'])]:
            existing=[x['name'] for p in (DATA/kind).glob('*.json') for x in json.loads(p.read_text())]
            for name in names: self.assertEqual(existing.count(name),1)

    def test_passive_conditions_and_buffs(self):
        levels=read('characters')[0]['passive']['levels']
        self.assertEqual([(l['type'],l['step']) for l in levels],[('각성',s) for s in [3,4,5,6]]+[('발현',s) for s in [2,4,6]])
        for i,l in enumerate(levels):
            self.assertIn(f'[{[15,20,25,30,35,45,50][i]}%]',l['effect'])
            self.assertIn(f'[{[20,30,40,50,55,60,70][i]}%]',l['effect'])
            self.assertEqual('인접한 아군이 없다면' in l['effect'], i<4)
            self.assertIn('반격 사거리가 [1]',l['effect'])
        b=read('buffs')[0]
        self.assertEqual(b['duration'],2)
        self.assertIn('해제 불가',b['tags'])
        for i,l in enumerate(b['levels']):
            self.assertIn(f'[{[15,25,30][i]}%]',l['effect'])
            self.assertEqual('1 TP' in l['effect'],i==2)

    def test_ultimate_and_classes(self):
        u=read('characters')[0]['ultimate']
        self.assertEqual((u['tpCost'],u['range'],u['cooldown']),(5,[1,1],5))
        for l,n in zip(u['levels'],[120,130,140,150]):
            self.assertIn(f'[{n}%]',l['effect'])
            self.assertIn('[3×4]',l['effect'])
            self.assertIn('[제압]',l['effect'])
            self.assertIn('[도발]',l['effect'])
        d,v=read('classes')
        self.assertEqual((d['parent'],v['parent']),('비프로스트발키리','스카우트'))
        self.assertIn('[80%]',d['passive']['lv2'])
        self.assertIn('추가 행동',d['skills'][0]['effect'])
        self.assertEqual(v['skills'][0]['range'],'자신')

    def test_weapon_healing_limit_and_stats(self):
        w=read('weapons')[0]
        self.assertEqual([s['maxHp'] for s in w['baseStats']],[141,142,143,145,146,147])
        self.assertEqual([s['attack'] for s in w['baseStats']],[316,319,323,327,330,334])
        for e,start in zip(w['effects'],[15,10]):
            for i,l in enumerate(e['levels']):
                self.assertIn(f'[{start+i}%]',l['effect'])
                self.assertIn(f'턴 당 [{1 if i<4 else 2}]',l['effect'])
        b=read('buffs')[2]
        self.assertEqual(b['duration'],1)
        for i,l in enumerate(b['levels']): self.assertIn(f'[+{i+5}%]',l['effect'])

if __name__=='__main__': unittest.main()
