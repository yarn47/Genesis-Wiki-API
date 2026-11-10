import json
import unittest
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / 'data'
def read(kind):
    return json.loads((DATA / kind / 'christina.json').read_text())

class ChristinaDataTest(unittest.TestCase):
    def test_identity(self):
        c = read('characters')[0]
        self.assertEqual((c['name'], c['releaseDate'], c['appearedIn']), ('크리스티나 여제', '2025-04-15', '창세기전3'))
        self.assertNotIn('stats', c)

    def test_passive_timing(self):
        levels = read('characters')[0]['passive']['levels']
        self.assertEqual([(x['type'],x['step']) for x in levels], [('각성',3),('각성',4),('각성',5),('각성',6),('발현',2),('발현',4),('발현',6)])
        for x in levels[:4]: self.assertIn('공격을 당한 후', x['effect'])
        for x in levels[4:6]: self.assertIn('전투 준비 단계에', x['effect'])
        self.assertIn('적이 공격하기 전에', levels[-1]['effect'])
        self.assertNotIn('체력을 회복', levels[2]['effect'])
        self.assertIn('[30%]{red}만큼 체력을 회복', levels[3]['effect'])
        self.assertIn('[80%]{red}만큼 체력을 회복', levels[-1]['effect'])

    def test_ultimate_gap(self):
        u = read('characters')[0]['ultimate']
        self.assertEqual(u['range'], [1,5])
        for x, step, damage, chance in zip(u['levels'],[0,1,3,5],[90,100,110,120],[35,40,45,50]):
            self.assertEqual(x['step'],step)
            self.assertIn(f'[{damage}%]{{red}}만큼 피해', x['effect'])
            self.assertIn(f'[{chance}%]{{red}}확률', x['effect'])
            self.assertIn('[2]{yellow}턴 동안 [멍해짐]{orange}', x['effect'])

    def test_buffs(self):
        buffs = {x['name']:x for x in read('buffs')}
        self.assertEqual([x['duration'] for x in buffs['여제의 인장']['levels']], [2,2,2,2,3,3,3])
        self.assertEqual(buffs['황가의 특권']['maxStack'],3)
        self.assertNotIn('duration', buffs['황가의 특권'])
        self.assertEqual(buffs['여제의 깃발']['duration'],'영구')

    def test_classes_and_artifacts(self):
        self.assertEqual([(x['name'],x['parent']) for x in read('classes')],[('임페리얼거너','거너'),('엠프레스거너','임페리얼거너')])
        self.assertEqual(read('characters')[0]['artifacts'],['초과 장전기','초기 철갑 탄창','치밀한 준비'])
        self.assertEqual(read('classes')[0]['skills'][0]['range'],[2,4])

    def test_weapon_ammunition(self):
        w = read('weapons')[0]
        exclusive, normal = w['effects']
        for i, (e,n) in enumerate(zip(exclusive['levels'], normal['levels'])):
            self.assertIn(f'최대치가 [{1 if i<3 else 2}]{{red}}',e['effect'])
            self.assertIn('최대치가 [1]{red}',n['effect'])
            self.assertNotIn('황가의 특권',n['effect'])
            self.assertEqual('확률' in e['effect'],i<5)
        self.assertEqual(w['baseStats'][-1],{'step':6,'maxHp':122,'attack':382})

if __name__ == '__main__': unittest.main()
