import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load(kind):
    return json.loads((ROOT / 'data' / kind / 'ice_pandragon.json').read_text())

class IcePandragonDataTests(unittest.TestCase):
    def test_identity_and_links(self):
        c = load('characters')[0]
        self.assertEqual((c['releaseDate'], c['appearedIn']), ('2024-11-26', '창세기전2'))
        self.assertEqual((c['faction'], c['element']), ('팬드래건', '지성의결정체'))
        self.assertTrue(c['published'])
        self.assertNotIn('stats', c)
        for key, kind in [('classTree','classes'), ('artifacts','artifacts')]:
            names = {x['name'] for p in (ROOT/'data'/kind).glob('*.json') for x in json.loads(p.read_text())}
            self.assertTrue(set(c[key]) <= names)
        self.assertEqual(c['exclusiveWeapon'], load('weapons')[0]['name'])

    def test_observed_unmanifested_ultimate(self):
        u = load('characters')[0]['ultimate']
        self.assertEqual([l['step'] for l in u['levels']], [0,1,3,5])
        for l, dmg, chance in zip(u['levels'], [125,130,135,140], [35,50,75,100]):
            self.assertIn(f'[{dmg}%]', l['effect'])
            self.assertIn(f'[{chance}%]', l['effect'])
        self.assertEqual((u['tpCost'],u['range'],u['cooldown']), (5,[1,3],5))

    def test_passive_progression(self):
        ls = load('characters')[0]['passive']['levels']
        self.assertEqual([(l['type'],l['step']) for l in ls], [('각성',3),('각성',4),('각성',5),('각성',6),('발현',2),('발현',4),('발현',6)])
        for l, damage in zip(ls[:4],[15,20,25,30]):
            self.assertIn('[100%]',l['effect'])
            self.assertIn(f'[{damage}%]',l['effect'])
        for l, threshold, damage in zip(ls[4:],[90,80,70],[30,35,40]):
            self.assertIn(f'[{threshold}%]',l['effect'])
            self.assertEqual(l['effect'].count(f'[{damage}%]'),2)

    def test_certainty_trigger_and_duration(self):
        b = {x['name']:x for x in load('buffs')}
        ls = b['확신의 검']['levels']
        self.assertEqual([l['duration'] for l in ls], [2,2,3,3,4,4,4])
        for i,l in enumerate(ls):
            self.assertIn('적 처치 시' if i<4 else '죽음에 이르는 피해',l['effect'])
            self.assertIn('[오만의 대가]',l['effect'])
        self.assertEqual(b['유아 독존']['duration'],'영구')
        self.assertEqual(load('debuffs')[0]['duration'],'영구')

    def test_class_connections_and_skills(self):
        cs=load('classes')
        self.assertEqual([c['parent'] for c in cs], ['소드맨','나이트'])
        self.assertEqual([c['skills'][0]['range'] for c in cs], [[4,4],[1,3]])
        self.assertEqual([c['skills'][0]['tpCost'] for c in cs], [2,3])
        self.assertEqual([c['skills'][0]['cooldown'] for c in cs], [2,3])
        for c in cs:
            self.assertEqual((c['attackRange'],c['moveRange']),(1,3))
            self.assertEqual(c['skills'][0]['element'],'빙한')

    def test_chill_and_ice_wall(self):
        b={x['name']:x for x in load('buffs')}
        d={x['name']:x for x in load('debuffs')}
        self.assertEqual((d['한기']['maxStack'],d['한기']['duration']),(3,2))
        self.assertEqual((b['서리 빙벽']['maxStack'],b['서리 빙벽']['duration']),(2,'영구'))
        self.assertEqual(b['서리 빙벽']['description'].count('중첩되지 않음'),2)
        self.assertNotIn('duration',b['빙정'])

    def test_weapon_unlocks_and_stats(self):
        w=load('weapons')[0]
        self.assertEqual([s['maxHp'] for s in w['baseStats']], [122,123,124,126,127,128])
        self.assertEqual([s['attack'] for s in w['baseStats']], [364,367,371,375,378,382])
        self.assertEqual([e['type'] for e in w['effects']], ['전용','일반'])
        for i,l in enumerate(w['effects'][0]['levels']):
            self.assertEqual('추가 공격' in l['effect'],i>=2)
            self.assertEqual('[빙정]' in l['effect'],i==5)
            self.assertIn('쿨타임 [3]',l['effect'])
        self.assertTrue(all('TP' not in l['effect'] for l in w['effects'][1]['levels']))

    def test_artifact_progression(self):
        b=next(x for x in load('buffs') if x['name']=='서리 권좌')
        for l,n,radius in zip(b['levels'],[25,35,40,50],[2,2,3,3]):
            self.assertIn(f'[+{n}%]',l['effect'])
            self.assertIn(f'[-{n}%]',l['effect'])
            self.assertIn(f'[{radius}]',l['effect'])
            self.assertNotIn('duration',l)
        self.assertEqual([l['step'] for l in load('artifacts')[0]['levels']],[3,4,5,6])

if __name__ == '__main__':
    unittest.main()
