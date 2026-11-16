import json
import unittest
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / 'data'

def read(kind):
    return json.loads((DATA / kind / 'iskinderun.json').read_text())

class IskinderunDataTest(unittest.TestCase):
    def test_identity(self):
        c = read('characters')[0]
        self.assertEqual((c['name'], c['releaseDate'], c['appearedIn']), ('바다의 이스킨데룬', '2025-05-27', '창세기전2'))
        self.assertEqual((c['faction'], c['subFaction'], c['element']), ('암흑신', '이너브레이크', '지성의결정체'))
        self.assertNotIn('stats', c)

    def test_passive_progression(self):
        ls = read('characters')[0]['passive']['levels']
        self.assertEqual([(x['type'], x['step']) for x in ls], [('각성',3),('각성',4),('각성',5),('각성',6),('발현',2),('발현',4),('발현',6)])
        for i,x in enumerate(ls):
            self.assertIn(f'[청해의 가호 {i+1}]{{green}}', x['effect'])
            self.assertIn(f'[{10+i*5}%]{{red}}', x['effect'])
            self.assertEqual('TP' in x['effect'], i >= 4)
        self.assertIn('[2 TP]{yellow}', ls[-1]['effect'])

    def test_ultimate_options(self):
        u = read('characters')[0]['ultimate']
        self.assertEqual((u['tpCost'],u['range'],u['cooldown']), (5,'자신',5))
        for x,step,n in zip(u['levels'],[0,1,3,5],[100,110,120,130]):
            self.assertEqual(x['step'],step)
            self.assertEqual(x['effect'].count(f'[{n}%]{{red}}'), 2)
            self.assertIn('밍밍 버스트:', x['effect'])
            self.assertIn('밍밍 러쉬:', x['effect'])
            self.assertIn('[이온화 지대]{orange}', x['effect'])

    def test_buffs(self):
        b = {x['name']:x for x in read('buffs')}
        ls = b['응축된 의지']['levels']
        for i,n in enumerate([10,20,25,35,45,50,60]):
            self.assertIn(f'[+{n}%]{{red}}', ls[i]['effect'])
            self.assertEqual(ls[i]['duration'],1)
        self.assertNotIn('이동력', ls[1]['effect'])
        self.assertIn('이동력 [+1]{red}', ls[2]['effect'])
        self.assertIn('이동력 [+2]{red}', ls[5]['effect'])
        self.assertEqual(read('debuffs')[0]['tags'], ['쇼크'])

    def test_classes(self):
        cs = {x['name']:x for x in read('classes')}
        self.assertEqual({n:c['parent'] for n,c in cs.items()}, {'아쿠아랜스':'파이크','오션템플러':'템플러','탈라사크':'아쿠아랜스'})
        self.assertEqual(cs['오션템플러']['skills'][0]['range'], [3,3])
        self.assertIn('보호막을 하나 잃습니다', cs['아쿠아랜스']['skills'][0]['effect'])
        self.assertEqual(cs['탈라사크']['skills'][0]['cooldown'],4)

    def test_weapon_and_artifact(self):
        w = read('weapons')[0]
        self.assertEqual(w['baseStats'][-1], {'step':6,'maxHp':133,'attack':365})
        for i,n in enumerate([10,14,18,22,26,30]):
            self.assertIn(f'[{n}%]{{red}}', w['effects'][0]['levels'][i]['effect'])
            self.assertIn(f'[{(i+1)*10}%]{{red}}', w['effects'][0]['levels'][i]['effect'])
        a = read('artifacts')[0]
        self.assertEqual([x['step'] for x in a['levels']], [3,4,5,6])
        self.assertIn('[60%]{red}', a['levels'][-1]['effect'])

if __name__ == '__main__':
    unittest.main()
