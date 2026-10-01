import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2] / 'data'
def read(kind):
    return json.loads((ROOT/kind/'nina.json').read_text())

class NinaTests(unittest.TestCase):
    def test_profile_and_absent_features(self):
        c = read('characters')[0]
        self.assertEqual(c['grade'], '영웅')
        self.assertEqual(c['releaseDate'], '2024-01-09')
        self.assertIsNone(c['appearedIn'])
        self.assertFalse(c['hasManifestation'])
        self.assertNotIn('ultimate', c)
        self.assertNotIn('exclusiveWeapon', c)
        self.assertEqual(c['artifacts'], [])
        self.assertEqual((c['faction'],c['height'],c['cv']), ('가라드','168cm','송하림'))

    def test_passive_levels_and_range(self):
        ls = read('characters')[0]['passive']['levels']
        self.assertEqual([l['step'] for l in ls], [2,3,4,5,6])
        for l, heal in zip(ls, [20,30,35,45,50]):
            self.assertEqual(l['type'], '각성')
            self.assertIn(f'[{heal}%]', l['effect'])
            self.assertIn('체력이 [100%]{red}가 아니라면', l['effect'])
            self.assertIn('디버프를 [1]{red}개', l['effect'])
        for l in ls[:2]: self.assertIn('[2]{red}칸', l['effect'])
        for l in ls[2:4]: self.assertIn('[3]{red}칸', l['effect'])
        self.assertNotIn('칸', ls[4]['effect'])

    def test_classes_and_statuses(self):
        cs = {c['name']:c for c in read('classes')}
        self.assertEqual(set(cs), {'서머너','서먼로드','세인트'})
        self.assertEqual([cs[n]['parent'] for n in ['서머너','서먼로드','세인트']], ['시스터','서머너','클레릭'])
        gate = cs['서먼로드']['skills'][0]
        self.assertNotIn('tpCost', gate)
        self.assertIn('[TP]{yellow}를 모두 소모', gate['effect'])
        self.assertEqual((gate['range'],gate['cooldown']), ([1,2],3))
        for key,count in [('lv1',1),('lv2',2)]:
            self.assertIn(f'디버프를 [{count}]', cs['세인트']['passive'][key])
            self.assertIn('[30%]', cs['세인트']['passive'][key])
        bs = {b['name']:b for b in read('buffs')}
        self.assertEqual(bs['큐어 라이트']['duration'],2)
        self.assertIn('[30%]',bs['큐어 라이트']['description'])
        for name, values in [('힘의 인장',[15,20]),('영가',[25,30])]:
            for l,v in zip(bs[name]['levels'],values):
                self.assertEqual(l['duration'],2)
                self.assertIn(f'[+{v}%]',l['effect'])
        for kind in ['classes','buffs']:
            names = [v['name'] for p in (ROOT/kind).glob('*.json') for v in json.loads(p.read_text())]
            self.assertEqual(len(names),len(set(names)))
            if kind == 'classes': self.assertTrue(set(read('characters')[0]['classTree']) <= set(names))

if __name__ == '__main__': unittest.main()
