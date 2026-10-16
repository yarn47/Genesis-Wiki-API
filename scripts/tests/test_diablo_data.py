import json
from pathlib import Path
import unittest

DATA = Path(__file__).resolve().parents[2] / 'data'

def read(kind):
    return json.loads((DATA / kind / 'diablo.json').read_text())

class DiabloTests(unittest.TestCase):
    def test_profile_and_shared_resources(self):
        c = read('characters')[0]
        self.assertEqual((c['releaseDate'], c['appearedIn']), ('2024-03-05', '창세기전2'))
        self.assertEqual(c['subFaction'], '암흑신')
        self.assertNotIn('stats', c)
        self.assertEqual(c['artifacts'], ['간이 보호 부적', '넘치는 통찰', '깜빡이는 보주'])
        for kind, names in [('classes', c['classTree']), ('artifacts', c['artifacts'])]:
            existing = [x['name'] for p in (DATA/kind).glob('*.json') for x in json.loads(p.read_text())]
            for name in names:
                self.assertEqual(existing.count(name), 1)

    def test_passive_progression(self):
        levels = read('characters')[0]['passive']['levels']
        self.assertEqual([(x['type'], x['step']) for x in levels],
                         [('각성', s) for s in [3,4,5,6]] + [('발현', s) for s in [2,4,6]])
        for l, defense, spell, count in zip(levels, [2,3,4,5,6,6,6], [15,25,30,40,50,55,60], [1,1,2,2,2,2,2]):
            self.assertIn(f'[{defense}%]', l['effect'])
            self.assertIn(f'[{spell}%]', l['effect'])
            self.assertIn(f'스킬 [{count}]', l['effect'])
            self.assertIn('사용하지 않은 스킬이 우선', l['effect'])
        self.assertNotIn('최대 체력이', levels[4]['effect'])
        self.assertIn('[10%]', levels[5]['effect'])
        self.assertIn('[20%]', levels[6]['effect'])
        self.assertIn('디버프 하나당 [2]', levels[6]['effect'])

    def test_ultimate(self):
        u = read('characters')[0]['ultimate']
        self.assertEqual((u['tpCost'],u['range'],u['cooldown']), (5,[3,3],5))
        self.assertEqual([l['step'] for l in u['levels']], [0,1,3,5])
        for i,l in enumerate(u['levels']):
            for n in [35,45,55]:
                self.assertIn(f'[{n+i*5}%]', l['effect'])

    def test_weapon_ranges_and_stats(self):
        w = read('weapons')[0]
        self.assertEqual([s['maxHp'] for s in w['baseStats']], [116,117,118,120,121,122])
        self.assertEqual([s['spellAttack'] for s in w['baseStats']], [381,384,388,392,395,399])
        d = {x['name']: x for x in read('debuffs')}
        for i,l in enumerate(d['영혼 폭발']['levels']):
            self.assertIn(f'[{25+i*5}%]', l['effect'])
            self.assertIn(['[1칸]', '[1칸]', '[1바퀴]', '[1바퀴]', '[2칸]', '[2칸]'][i], l['effect'])
        for i,l in enumerate(d['내파']['levels']):
            self.assertIn(f'[{15+i*5}%]', l['effect'])
            self.assertIn('[1]', l['effect'])

    def test_new_classes_and_artifact(self):
        classes = read('classes')
        self.assertEqual([c['name'] for c in classes], ['헬인보커','나이트메어'])
        for c in classes:
            self.assertEqual((c['attackRange'],c['moveRange']), (3,3))
        for i,l in enumerate(read('artifacts')[0]['levels']):
            self.assertEqual(l['step'], i+3)
            self.assertIn(f'[+{[5,6,8,10][i]}%]', l['effect'])
            self.assertIn('절반만큼 내림', l['effect'])

if __name__ == '__main__':
    unittest.main()
