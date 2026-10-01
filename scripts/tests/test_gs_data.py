import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2] / 'data'
def read(kind):
    return json.loads((ROOT / kind / 'gs.json').read_text())

class GSTests(unittest.TestCase):
    def test_character(self):
        c = read('characters')[0]
        self.assertEqual((c['name'], c['grade'], c['releaseDate'], c['appearedIn']), ('G.S', '영웅', '2024-01-09', '창세기전2'))
        self.assertFalse(c['hasManifestation'])
        self.assertNotIn('ultimate', c)
        self.assertNotIn('exclusiveWeapon', c)
        self.assertEqual(c['artifacts'], [])
        self.assertEqual(c['classTree'], ['레인저','파이터','스카우트','소드맨','하이마스터','소드마스터'])

    def test_passive_and_statuses(self):
        levels = read('characters')[0]['passive']['levels']
        self.assertEqual([v['step'] for v in levels], [2,3,4,5,6])
        for i, v in enumerate(levels):
            self.assertIn(f'[{i+5}%]', v['effect'])
            self.assertIn('느려짐 ' + ('1' if i < 3 else '2'), v['effect'])
            self.assertIn('[2]{yellow}턴', v['effect'])
            self.assertIn(f'잿빛 새벽 {i+1}', v['effect'])
        for v, amount in zip(read('buffs')[0]['levels'], [50,55,60,65,70]):
            self.assertIn(f'[-{amount}%]', v['effect'])
            self.assertIn(f'[{amount}%]', v['effect'])
        slow = next(v for v in json.loads((ROOT/'debuffs/defender_line.json').read_text()) if v['name']=='느려짐')
        self.assertEqual([v['level'] for v in slow['levels']], [1,2])
        self.assertEqual(slow['levels'][0]['duration'], 1)

    def test_classes_and_unique_names(self):
        cs = read('classes')
        self.assertEqual([v['name'] for v in cs], ['레인저','스카우트','하이마스터'])
        self.assertEqual(cs[1]['parent'], '레인저')
        self.assertEqual(cs[2]['parent'], '스카우트')
        self.assertEqual([s['name'] for c in cs for s in c['skills']], ['제식연','무극일섬혼','응급 처치','잠열섬','일점극파'])
        self.assertIn('추가 스킬 사용이나 공격기회', cs[0]['skills'][2]['effect'])
        self.assertEqual(cs[2]['skills'][0]['tpCost'], 3)
        for kind in ['classes','buffs','debuffs']:
            names = [v['name'] for p in (ROOT/kind).glob('*.json') for v in json.loads(p.read_text())]
            self.assertEqual(len(names),len(set(names)))
            if kind=='classes': self.assertTrue(set(read('characters')[0]['classTree']) <= set(names))

if __name__ == '__main__': unittest.main()
