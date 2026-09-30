import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]

def read(path):
    return json.loads((ROOT / 'data' / path).read_text())

class BeradinTests(unittest.TestCase):
    """Expected values transcribed from user screenshots 6257–6383."""

    def test_class_tree_and_skills(self):
        classes = read('classes/mage_line.json')
        c = read('characters/beradin.json')[0]
        self.assertEqual(c['classTree'], [v['name'] for v in classes])
        self.assertEqual([v.get('parent') for v in classes], [None, '메이지', '메이지', '매지션', '위자드', '위자드'])
        self.assertEqual(sum(len(v['skills']) for v in classes), 8)
        self.assertEqual([s['tpCost'] for v in classes for s in v['skills']], [2, 1, 3, 2, 3, 4, 2, 5])

    def test_passive_unlocks_and_values(self):
        levels = read('characters/beradin.json')[0]['passive']['levels']
        self.assertEqual([(l['type'], l['step']) for l in levels], [('각성',3),('각성',4),('각성',5),('각성',6),('발현',2),('발현',4),('발현',6)])
        for i, (level, damage) in enumerate(zip(levels, [20,23,26,30,35,40,45]), 1):
            self.assertIn(f'[파멸의 고리 {i}]{{green}}', level['effect'])
            self.assertIn(f'[{damage}%]{{red}}만큼 피해', level['effect'])
        self.assertTrue(all('보호막' not in l['effect'] for l in levels[:4]))
        for level, shield in zip(levels[4:], [15,20,25]):
            self.assertIn(f'[{shield}%]{{red}}에 해당하는 보호막', level['effect'])

    def test_ring_buffs(self):
        ring = next(v for v in read('buffs/beradin.json') if v['name']=='파멸의 고리')
        self.assertEqual([l['maxStack'] for l in ring['levels']], [9,8,7,6,6,6,6])
        for level, bonus in zip(ring['levels'], [3,4,5,6,8,10,12]):
            self.assertIn(f'[+{bonus}%]{{red}}', level['effect'])
        self.assertIn('해제 불가', ring['tags'])

    def test_ultimate(self):
        u = read('characters/beradin.json')[0]['ultimate']
        self.assertEqual((u['tpCost'],u['range'],u['cooldown']), (5,'자신',5))
        self.assertEqual([l['step'] for l in u['levels']], [0,1,3,5])
        for l, damage in zip(u['levels'], [150,155,160,165]):
            self.assertIn(f'[{damage}%]{{red}}', l['effect'])
            self.assertIn('[불멸의 안식]{green}', l['effect'])

    def test_artifact_values_and_order(self):
        artifacts = read('artifacts/beradin.json')
        self.assertEqual(read('characters/beradin.json')[0]['artifacts'], [a['name'] for a in artifacts])
        for a in artifacts:
            self.assertEqual([l['step'] for l in a['levels']], [3,4,5,6])
        for l, n in zip(artifacts[0]['levels'], [40,60,80,100]):
            self.assertIn(f'[{n}%]{{red}}', l['effect'])
        for l, n, chance in zip(artifacts[2]['levels'], [10,11,13,15], [50,60,70,90]):
            self.assertIn(f'[+{n}%]{{red}}', l['effect'])
            self.assertIn(f'[{chance}%]{{red}}', l['effect'])

    def test_weapon_stats(self):
        w = read('weapons/beradin.json')[0]
        self.assertEqual([s['maxHp'] for s in w['baseStats']], [116,117,118,120,121,122])
        self.assertEqual([s['spellAttack'] for s in w['baseStats']], [381,384,388,392,395,399])
        self.assertEqual([s['magicPen'] for s in w['baseStats']], [15,17,19,21,23,25])
        for effect, values in zip(w['effects'], [[25,30,35,40,45,50],[15,18,21,24,27,30]]):
            for level, value in zip(effect['levels'], values):
                self.assertIn(f'[{value}%]{{red}}의 확률', level['effect'])

    def test_shared_names_are_not_duplicated(self):
        for folder in ['buffs','debuffs','classes','artifacts','weapons','characters']:
            names = [v['name'] for p in (ROOT/'data'/folder).glob('*.json') for v in json.loads(p.read_text())]
            self.assertEqual(len(names), len(set(names)), folder)

if __name__ == '__main__':
    unittest.main()
