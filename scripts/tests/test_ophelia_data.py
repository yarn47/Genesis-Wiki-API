import json
import re
import unittest
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / 'data'


def read(kind):
    return json.loads((DATA / kind / 'ophelia.json').read_text())


class OpheliaTests(unittest.TestCase):
    def test_profile_and_references(self):
        c = read('characters')[0]
        elizabeth = json.loads((DATA / 'characters/elizabeth.json').read_text())[0]
        self.assertEqual(c['releaseDate'], elizabeth['releaseDate'])
        self.assertEqual(c['appearedIn'], '템페스트')
        self.assertEqual((c['birthYear'], c['height'], c['cv']), ('에스겔력 1253년', '167cm', '최하리'))
        self.assertNotIn('stats', c)
        for kind, names in [('classes', c['classTree']), ('artifacts', c['artifacts']), ('weapons', [c['exclusiveWeapon']])]:
            available = [x['name'] for p in (DATA / kind).glob('*.json') for x in json.loads(p.read_text())]
            for name in names:
                self.assertEqual(available.count(name), 1)
        available = set()
        for kind in ['buffs', 'debuffs']:
            for p in (DATA / kind).glob('*.json'):
                for b in json.loads(p.read_text()):
                    available.add(b['name'])
                    available.update(l.get('name', f'{b["name"]} {l["level"]}') for l in b.get('levels', []))
        for kind in ['characters', 'classes', 'buffs', 'weapons', 'artifacts']:
            for name in re.findall(r'\[([^\[\]]+)\]\{(?:green|orange)\}', json.dumps(read(kind), ensure_ascii=False)):
                self.assertIn(name, available)

    def test_cube_progression(self):
        levels = read('characters')[0]['passive']['levels']
        self.assertEqual([(l['type'], l['step']) for l in levels], [('각성', s) for s in [3,4,5,6]] + [('발현', s) for s in [2,4,6]])
        buffs = read('buffs')[0]['levels']
        for i, (l, b, atk, dr) in enumerate(zip(levels, buffs, [5,6,8,10,12,14,16], [2,3,4,5,6,7,8])):
            self.assertIn(f'효과를 [{3 if i == 6 else 2}]', l['effect'])
            self.assertEqual('스킬 사거리' in l['effect'], i >= 5)
            self.assertIn(f'카오스 큐브 {i+1}', l['effect'])
            self.assertIn(f'[+{atk}%]', b['effect'])
            self.assertIn(f'[-{dr}%]', b['effect'])
            self.assertEqual('모든 디버프' in b['effect'], i >= 2)
            self.assertEqual(b['maxStack'], 4 if i == 6 else 3)

    def test_ultimate(self):
        u = read('characters')[0]['ultimate']
        self.assertEqual((u['tpCost'], u['cooldown'], u['range']), (5,5,[1,3]))
        self.assertEqual([l['step'] for l in u['levels']], [0,1,3,5])
        for i, l in enumerate(u['levels']):
            self.assertIn(f'[{140+10*i}%]', l['effect'])
            self.assertIn(f'[{65+5*i}%]', l['effect'])
            self.assertIn(f'주위 [{4 if i == 3 else 3}]', l['effect'])
        self.assertNotIn('element', u)

    def test_classes_and_artifacts(self):
        fatima, ultimate = read('classes')
        self.assertEqual((fatima['parent'], ultimate['parent']), ('메이지', '파티마'))
        for key in ['lv1', 'lv2']:
            self.assertIn('피해를 입혔다면', ultimate['passive'][key])
            self.assertNotIn('피해를 입었다면', ultimate['passive'][key])
        self.assertEqual(ultimate['skills'][0]['range'], [1,3])
        self.assertEqual(ultimate['skills'][0]['tpCost'], 4)
        for i, l in enumerate(read('artifacts')[0]['levels']):
            self.assertEqual(l['step'], i+3)
            self.assertIn(f'[{15+5*i}%]', l['effect'])
        ice = next(b for b in read('buffs') if b['name'] == '얼음 방패')
        for i, l in enumerate(ice['levels']):
            self.assertEqual(l['duration'], 2)
            self.assertIn(f'[{15+5*i}%]', l['effect'])

    def test_weapon(self):
        w = read('weapons')[0]
        self.assertEqual([s['maxHp'] for s in w['baseStats']], [116,117,118,120,121,122])
        self.assertEqual([s['spellAttack'] for s in w['baseStats']], [381,384,388,392,395,399])
        for e in w['effects']:
            exclusive = e['type'] == '전용'
            self.assertEqual([l['step'] for l in e['levels']], [1,2,3,4,5,6])
            for i, l in enumerate(e['levels']):
                self.assertIn(f'[{i+(10 if exclusive else 5)}%]', l['effect'])
                self.assertEqual('카오스 큐브' in l['effect'], exclusive)
                self.assertIn(f'쿨타임 [{2 if exclusive and i >= 4 else 3}]', l['effect'])
                self.assertEqual('확률' in l['effect'], not (exclusive and i == 5))


if __name__ == '__main__':
    unittest.main()
