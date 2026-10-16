import json
from pathlib import Path
import unittest

DATA = Path(__file__).resolve().parents[2] / 'data'

def read(kind):
    return json.loads((DATA / kind / 'sara_randgrid.json').read_text())

class SaraTests(unittest.TestCase):
    def test_profile_and_passive_conditions(self):
        c = read('characters')[0]
        self.assertEqual(c['releaseDate'], '2024-02-20')
        self.assertEqual(c['appearedIn'], '창세기전2')
        self.assertNotIn('stats', c)
        levels = c['passive']['levels']
        self.assertEqual([(x['type'], x['step']) for x in levels],
                         [('각성', x) for x in [3,4,5,6]] + [('발현', x) for x in [2,4,6]])
        for i, l in enumerate(levels):
            self.assertEqual('피해를 줬다면' in l['effect'], i < 4)
            self.assertEqual('게임 시작 시' in l['effect'], i == 6)

    def test_ultimate_inference_and_extra_action(self):
        levels = read('characters')[0]['ultimate']['levels']
        self.assertEqual([l['step'] for l in levels], [0,1,3,5])
        for i, l in enumerate(levels):
            self.assertIn(f'[{25+i*5}%]', l['effect'])
            self.assertIn('추가 이동' if i < 2 else '추가 행동', l['effect'])
            self.assertEqual('추정값' in l['effect'], i == 0)
            self.assertEqual('TP를 회복' in l['effect'], i >= 2)

    def test_weapon_all_six_steps(self):
        w = read('weapons')[0]
        self.assertEqual([s['maxHp'] for s in w['baseStats']], [141,142,143,145,146,147])
        self.assertEqual([s['attack'] for s in w['baseStats']], [316,319,323,327,330,334])
        for e in w['effects']:
            self.assertEqual([l['step'] for l in e['levels']], list(range(1,7)))
        for i, l in enumerate(w['effects'][0]['levels']):
            self.assertIn(f'호위 횟수가 [{1 if i < 4 else 2}]', l['effect'])

    def test_artifacts_and_buffs(self):
        artifacts = read('artifacts')
        self.assertEqual(read('characters')[0]['artifacts'], [a['name'] for a in artifacts])
        for a in artifacts:
            self.assertEqual([l['step'] for l in a['levels']], [3,4,5,6])
        for i, l in enumerate(artifacts[0]['levels']):
            self.assertIn(f'[+{[5,20,35,50][i]}%]', l['effect'])
        buffs = {b['name']: b for b in read('buffs')}
        for n in ['사수', '격전']:
            self.assertEqual(len(buffs[n]['levels']), 7)
            self.assertIn('해제 불가', buffs[n]['tags'])
        self.assertEqual(buffs['우아한 호흡']['maxStack'], 2)
        self.assertEqual(buffs['라이트닝 블레이드']['duration'], 2)

    def test_reused_classes_and_lightning(self):
        classes = read('classes')
        self.assertEqual(len(classes), 4)
        self.assertEqual(sum(len(c['skills']) for c in classes), 6)
        self.assertNotIn('패스파인더', [c['name'] for c in classes])
        lightning = classes[0]['skills'][2]
        self.assertEqual((lightning['tpCost'],lightning['range'],lightning['area'],lightning['cooldown']), (1,'자신','단일',3))

if __name__ == '__main__':
    unittest.main()
