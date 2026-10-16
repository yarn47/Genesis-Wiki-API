import json
from pathlib import Path
import unittest

DATA = Path(__file__).resolve().parents[2] / 'data'
def read(kind):
    return json.loads((DATA / kind / 'erica_myers.json').read_text())

class EricaTests(unittest.TestCase):
    def test_profile_and_references(self):
        c = read('characters')[0]
        self.assertEqual((c['releaseDate'], c['appearedIn']), ('2024-03-19', '창세기전2'))
        self.assertNotIn('stats', c)
        for kind, names in [('classes', c['classTree']), ('artifacts', c['artifacts'])]:
            existing = [x['name'] for p in (DATA/kind).glob('*.json') for x in json.loads(p.read_text())]
            for name in names:
                self.assertEqual(existing.count(name), 1)

    def test_passive_and_traps(self):
        levels = read('characters')[0]['passive']['levels']
        self.assertEqual([(x['type'], x['step']) for x in levels], [('각성',s) for s in [3,4,5,6]] + [('발현',s) for s in [2,4,6]])
        for i,l in enumerate(levels):
            self.assertIn('적을 공격하지 않았다면', l['effect'])
            self.assertIn(f'수면 폭발 덫 {i+1}', l['effect'])
            self.assertIn('스킬로 취급되지 않습니다', l['effect'])
        buffs = {b['name']: b for b in read('buffs')}
        for i,l in enumerate(buffs['수면 폭발 덫']['levels']):
            self.assertIn(f'[{[25,35,40,50,55,60,70][i]}%]', l['effect'])
            self.assertIn(f'[{1 if i<2 else 2}]{{yellow}}턴 동안 수면', l['effect'])
        for i,l in enumerate(buffs['숨 고르기']['levels']):
            self.assertIn(f'[{[10,20,20,30,35,40,50][i]}%]', l['effect'])
            self.assertEqual('쿨타임이 가장 긴' in l['effect'], i>=2)
        self.assertIn('모두', buffs['도움의 손길']['levels'][2]['effect'])

    def test_ultimate_and_classes(self):
        u=read('characters')[0]['ultimate']
        self.assertEqual((u['tpCost'],u['range'],u['cooldown']), (5,[2,7],5))
        for l,n in zip(u['levels'],[200,215,230,250]):
            self.assertIn(f'[{n}%]', l['effect'])
        s=read('classes')[1]['skills'][0]
        self.assertEqual((s['tpCost'],s['range'],s['cooldown']), (3,[2,5],3))
        self.assertIn('대상과 인접한 적들에게', s['effect'])
        self.assertIn('TP를 모두', s['effect'])

    def test_weapon_and_artifact(self):
        w=read('weapons')[0]
        self.assertEqual([s['maxHp'] for s in w['baseStats']], [118,119,120,122,123,124])
        self.assertEqual([s['attack'] for s in w['baseStats']], [376,379,383,387,390,394])
        for e,start,chance,heal in zip(w['effects'],[10,7],[30,15],[25,15]):
            for i,l in enumerate(e['levels']):
                for n in [start+2*i,chance,heal]: self.assertIn(f'[{n}%]',l['effect'])
        for i,l in enumerate(read('artifacts')[0]['levels']):
            self.assertEqual(l['step'],i+3)
            self.assertIn(f'[+{(i+1)*10}%]',l['effect'])
            self.assertIn(f'[-{(i+1)*10}%]',l['effect'])

if __name__ == '__main__':
    unittest.main()
