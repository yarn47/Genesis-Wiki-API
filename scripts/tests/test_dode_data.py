import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load(kind):
    return json.loads((ROOT/'data'/kind/'dode.json').read_text())

class DodeTests(unittest.TestCase):
    def test_identity_and_ultimate(self):
        c = load('characters')[0]
        self.assertEqual((c['releaseDate'], c['appearedIn']), ('2025-03-18', '서풍의 광시곡'))
        self.assertEqual((c['faction'], c['subFaction'], c['element']), ('게이시르', '이너브레이크', '신념의빛'))
        self.assertNotIn('stats', c)
        u = c['ultimate']
        self.assertEqual([l['step'] for l in u['levels']], [0,1,3,5])
        self.assertEqual((u['tpCost'],u['range'],u['cooldown']), (5,[1,3],5))
        d = load('debuffs')[0]
        self.assertEqual([l['level'] for l in d['levels']], [4,5,6,7])
        for i,l in enumerate(d['levels']):
            self.assertIn(f'[{80+20*i}%]', l['effect'])
            self.assertIn('고정 피해', l['effect'])
        for i,l in enumerate(u['levels']):
            self.assertIn(f'헤도닉 그랩 {i+4}', l['effect'])
            self.assertIn('로베르토 데 메디치', l['effect'])

    def test_passive_differences(self):
        ls = load('characters')[0]['passive']['levels']
        self.assertEqual([(l['type'],l['step']) for l in ls], [('각성',3),('각성',4),('각성',5),('각성',6),('발현',2),('발현',4),('발현',6)])
        self.assertNotIn('돌아오면', ls[0]['effect'])
        for i,l in enumerate(ls):
            self.assertIn(f'쿨타임 : [{[4,4,4,3,3,2,2][i]}]', l['effect'])
            if i:
                self.assertIn(f'주문력이 [{[0,10,20,30,30,35,40][i]}%]', l['effect'])
        self.assertIn('효과를 [2]{yellow}개', ls[-1]['effect'])

    def test_classes_and_controls(self):
        cs = load('classes')
        self.assertEqual([c['parent'] for c in cs], ['메이지','위자드','차밍메이지'])
        self.assertEqual([c['skills'][0]['tpCost'] for c in cs], [1,2,3])
        self.assertEqual(cs[2]['skills'][0]['name'], '매스 힙너시스')
        ds = {d['name']:d for d in load('debuffs')}
        self.assertEqual(ds['최면']['duration'], 1)
        self.assertIn('정신지배', ds['헤도닉 그랩']['tags'])
        self.assertIn('미련', ds['데들리 참']['description'])
        self.assertIn('[-80%]', ds['미련']['description'])

    def test_artifacts(self):
        c = load('characters')[0]
        self.assertEqual(c['artifacts'], ['속성 과부하','최상의 상태','마력 파동'])
        self.assertEqual([l['step'] for l in load('artifacts')[0]['levels']], [3,4,5,6])
        b = next(b for b in load('buffs') if b['name']=='마력 파동')
        self.assertEqual(b['maxStack'], 4)
        for i,l in enumerate(b['levels']):
            self.assertIn(f'[+{10+i*5}%]',l['effect'])

    def test_weapon(self):
        w = load('weapons')[0]
        self.assertEqual([s['spellAttack'] for s in w['baseStats']], [381,384,388,392,395,399])
        self.assertEqual([s['maxHp'] for s in w['baseStats']], [116,117,118,120,121,122])
        for i,l in enumerate(w['effects'][0]['levels']):
            self.assertIn(f'[{15+i*3}%]', l['effect'])
            self.assertEqual('스킬 사거리' in l['effect'], i>=3)
        self.assertIn('[3]{yellow}턴 동안 스킬 사거리', w['effects'][0]['levels'][-1]['effect'])
        self.assertTrue(all('스킬 사거리' not in l['effect'] for l in w['effects'][1]['levels']))

    def test_new_faction_mapping(self):
        self.assertIn('"이너브레이크": "innerbreak"', (ROOT/'scripts/gen_sql.py').read_text())
        self.assertIn('innerbreak', (ROOT/'Wiki-API/src/main/kotlin/com/genesis/wiki/entity/Enums.kt').read_text())
        self.assertEqual((ROOT/'db/migrations/019_innerbreak_faction.sql').read_text().count("'innerbreak'"), 2)

if __name__ == '__main__':
    unittest.main()
