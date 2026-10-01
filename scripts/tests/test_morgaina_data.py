import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2] / 'data'
def read(kind):
    return json.loads((ROOT / kind / 'morgaina.json').read_text())

class MorgainaTests(unittest.TestCase):
    def test_profile_and_passive(self):
        c = read('characters')[0]
        self.assertEqual(c['releaseDate'], '2024-01-09')
        self.assertIsNone(c['appearedIn'])
        self.assertNotIn('ultimate', c)
        levels = c['passive']['levels']
        self.assertEqual([(l['type'], l['step']) for l in levels], [('각성', n) for n in [3,4,5,6]] + [('발현', n) for n in [2,4,6]])
        for n, (l, hp) in enumerate(zip(levels, [35,40,45,50,60,80,100]), 1):
            self.assertIn(f'[{hp}%]', l['effect'])
            self.assertIn(f'[달의 의지 {n}]', l['effect'])
            self.assertIn(f'[달의 이면 {n}]', l['effect'])
        self.assertIn('[모든 TP]', levels[-1]['effect'])

    def test_classes_reuse_existing(self):
        all_classes = [c for p in (ROOT/'classes').glob('*.json') for c in json.loads(p.read_text())]
        by_name = {c['name']: c for c in all_classes}
        self.assertEqual(len(by_name), len(all_classes))
        for name in read('characters')[0]['classTree']: self.assertIn(name, by_name)
        self.assertEqual(by_name['프리스트']['parent'], '시스터')
        self.assertEqual(by_name['하이프리스트']['parent'], '프리스트')
        suns = [s for c in all_classes for s in c.get('skills', []) if s['name'] == '썬 라이트']
        self.assertEqual(len(suns), 2)
        self.assertEqual(suns[0], suns[1])
        for kind in ['buffs','debuffs','artifacts']:
            names = [v['name'] for p in (ROOT/kind).glob('*.json') for v in json.loads(p.read_text())]
            self.assertEqual(len(names), len(set(names)))

    def test_weapon_and_buffs(self):
        w = read('weapons')[0]
        self.assertEqual([s['maxHp'] for s in w['baseStats']], [130,131,132,134,135,136])
        self.assertEqual([s['spellAttack'] for s in w['baseStats']], [342,345,349,353,356,360])
        for effect in w['effects']: self.assertEqual([l['step'] for l in effect['levels']], list(range(1,7)))
        buffs = {b['name']:b for b in read('buffs')}
        for name in ['치유 의지','맹공 의지','보호 의지','공격 의지','월광']:
            self.assertEqual(len(buffs[name]['levels']), 6)
        for l, shield in zip(buffs['월광']['levels'], [25,30,35,40,45,50]):
            self.assertEqual(l['duration'], 3)
            self.assertIn(f'[{shield}%]', l['effect'])
            self.assertIn('[2]{yellow}턴', l['effect'])
        for name in ['달의 의지','달의 이면']:
            self.assertEqual(buffs[name]['tags'], ['해제 불가'])
            self.assertEqual(len(buffs[name]['levels']), 7)

    def test_artifacts(self):
        self.assertEqual(read('characters')[0]['artifacts'], ['치밀한 준비','마력의 공명석','그림자의 빛'])
        for a in read('artifacts'): self.assertEqual([l['step'] for l in a['levels']], [3,4,5,6])
        for l, v in zip(read('artifacts')[0]['levels'], [8,12,16,20]): self.assertIn(f'[+{v}%]', l['effect'])
        for l, v in zip(read('artifacts')[1]['levels'], [40,60,80,100]): self.assertIn(f'[{v}%]', l['effect'])

if __name__ == '__main__': unittest.main()
