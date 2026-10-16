import json
import re
from pathlib import Path
import unittest

DATA = Path(__file__).resolve().parents[2] / 'data'

def read(kind):
    return json.loads((DATA / kind / 'dunamis_rembrant.json').read_text())

class DunamisTests(unittest.TestCase):
    def test_profile_and_links(self):
        c = read('characters')[0]
        self.assertEqual((c['releaseDate'], c['appearedIn']), ('2024-04-30', '창세기전2'))
        self.assertNotIn('stats', c)
        for kind, names in [('classes', c['classTree']), ('artifacts', c['artifacts']), ('weapons', [c['exclusiveWeapon']])]:
            existing = [x['name'] for p in (DATA / kind).glob('*.json') for x in json.loads(p.read_text())]
            for name in names: self.assertEqual(existing.count(name), 1)
        names = set()
        for kind in ['buffs', 'debuffs']:
            for p in (DATA / kind).glob('*.json'):
                for b in json.loads(p.read_text()):
                    names.add(b['name'])
                    for l in b.get('levels', []): names.add(l.get('name', f"{b['name']} {l['level']}"))
        for kind in ['characters', 'classes', 'buffs', 'debuffs', 'weapons', 'artifacts']:
            for name in re.findall(r'\[([^\[\]]+)\]\{(?:green|orange)\}', json.dumps(read(kind), ensure_ascii=False)):
                self.assertIn(name, names)

    def test_passive_ranges_and_progression(self):
        levels = read('characters')[0]['passive']['levels']
        self.assertEqual([(x['type'], x['step']) for x in levels], [('각성', s) for s in [3,4,5,6]] + [('발현', s) for s in [2,4,6]])
        for i, l in enumerate(levels):
            self.assertIn('인접한 아군', l['effect'])
            self.assertIn(f'해방된 정신 {i+1}', l['effect'])
            self.assertEqual('이상이라면' in l['effect'], i < 4)
        self.assertIn('주변 1바퀴', levels[0]['effect'])
        self.assertIn('주위 2칸', levels[1]['effect'])
        self.assertIn('주위 2칸', levels[2]['effect'])
        self.assertIn('주변 2바퀴', levels[3]['effect'])
        for l, n in zip(read('buffs')[0]['levels'], [30,40,50,60,65,70,75]): self.assertIn(f'[{n}%]', l['effect'])

    def test_classes_and_distinct_debuff(self):
        white, ascetic = read('classes')
        self.assertEqual((white['parent'], ascetic['parent']), ('아머나이트', '팔라딘'))
        self.assertIn('[20%]', white['passive']['lv2'])
        self.assertIn('[60%]', ascetic['passive']['lv2'])
        debuffs = {x['name']:x for x in read('debuffs')}
        self.assertEqual(debuffs['고행']['maxStack'], 3)
        self.assertEqual(debuffs['억제 (고연섬)']['duration'], 2)
        self.assertNotIn('해제 불가', debuffs['억제 (고연섬)']['tags'])
        common = json.loads((DATA / 'debuffs/pandragon_line.json').read_text())[0]
        self.assertEqual(common['duration'], '영구')
        self.assertEqual(read('buffs')[1]['duration'], '영구')
        self.assertIn('[2]{yellow}턴', white['skills'][0]['effect'])

    def test_ultimate_and_artifacts(self):
        u = read('characters')[0]['ultimate']
        self.assertEqual([l['step'] for l in u['levels']], [0,1,3,5])
        for l, n in zip(u['levels'], [120,130,140,150]): self.assertIn(f'[{n}%]', l['effect'])
        for a, values in zip(read('artifacts'), [[40,60,80,100],[10,15,20,25]]):
            self.assertEqual([l['step'] for l in a['levels']], [3,4,5,6])
            for l,n in zip(a['levels'], values): self.assertIn(f'[+{n}%]', l['effect'])

    def test_weapon(self):
        w = read('weapons')[0]
        self.assertEqual([s['maxHp'] for s in w['baseStats']], [139,140,141,143,144,145])
        self.assertEqual([s['attack'] for s in w['baseStats']], [321,324,328,332,335,339])
        self.assertEqual([s['defense'] for s in w['baseStats']], [28,28,28,28,29,29])
        for e, values, heal in zip(w['effects'], [[15,17,19,21,23,25],[10,12,14,16,18,20]], [5,3]):
            for l,n in zip(e['levels'], values):
                self.assertIn(f'[{n}%]', l['effect'])
                self.assertIn(f'[{heal}%]', l['effect'])

if __name__ == '__main__': unittest.main()
