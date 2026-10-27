import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / 'data'
def load(kind):
    return json.loads((ROOT / kind / 'esmeralda.json').read_text())

class EsmeraldaDataTests(unittest.TestCase):
    def test_identity_and_progression(self):
        c = load('characters')[0]
        self.assertEqual(c['releaseDate'], '2024-08-20')
        self.assertEqual(c['appearedIn'], '서풍의 광시곡')
        self.assertEqual(len(c['classTree']), 6)
        self.assertEqual([(x['type'], x['step']) for x in c['passive']['levels']], [('각성',3),('각성',4),('각성',5),('각성',6),('발현',2),('발현',4),('발현',6)])
        self.assertEqual([x['step'] for x in c['ultimate']['levels']], [0,1,3,5])
        self.assertIn('[120%]', c['ultimate']['levels'][0]['effect'])
        self.assertIn('추정', (ROOT/'notes/esmeralda.md').read_text())

    def test_final_passive_distinguishes_cleanses(self):
        b = load('buffs')[0]['levels'][-1]
        self.assertIn('[2]{red}개 해제', b['effect'])
        self.assertIn('모두 해제', load('characters')[0]['passive']['levels'][-1]['effect'])
        self.assertEqual(b['duration'], 2)

    def test_weapon_steps(self):
        w = load('weapons')[0]
        self.assertEqual([s['spellAttack'] for s in w['baseStats']], [342,345,349,353,356,360])
        self.assertEqual([s['maxHp'] for s in w['baseStats']], [130,131,132,134,135,136])
        for x in w['effects'][0]['levels'][4:]:
            self.assertNotIn('이하인', x['effect'])
            self.assertIn('쿨타임 [2]', x['effect'])
        for x in w['effects'][1]['levels']:
            self.assertIn('쿨타임 [4]', x['effect'])

    def test_classes(self):
        cls = load('classes')
        self.assertEqual([x['parent'] for x in cls], ['시스터','힐러','힐러'])
        self.assertEqual(cls[1]['skills'][0]['range'], [1,2])
        self.assertEqual(cls[2]['skills'][0]['tags'], ['원거리','지향성','치유'])

if __name__ == '__main__':
    unittest.main()
