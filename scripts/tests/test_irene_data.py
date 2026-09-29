import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('gen_sql', ROOT / 'scripts/gen_sql.py')
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

def read(path):
    return json.loads((ROOT / 'data' / path).read_text())

class IreneTests(unittest.TestCase):
    def test_profile_and_manifest_without_ultimate(self):
        c = read('characters/irene.json')[0]
        ariana = read('characters/ariana.json')[0]
        for key in ['releaseDate', 'appearedIn']:
            self.assertEqual(c[key], ariana[key])
        self.assertEqual(gen.FACTIONS[c['faction']], 'garad')
        self.assertTrue(c['hasManifestation'])
        self.assertNotIn('ultimate', c)
        self.assertNotIn('stats', c)
        self.assertEqual([(l['type'], l['step']) for l in c['passive']['levels']], [('각성',i) for i in range(3,7)]+[('발현',i) for i in [2,4,6]])
        sql = gen.character_sql(c)
        self.assertNotIn('INSERT INTO ultimate_skills', sql)
        self.assertIn('INSERT INTO character_manifestation', sql)
        self.assertIn('(@id, 4,', sql)

    def test_two_linear_class_trees(self):
        classes = read('classes/priest_mage_line.json')
        self.assertEqual(len(classes), 6)
        self.assertEqual([c['name'] for c in classes if c['tier']==1], ['시스터','위치'])
        self.assertEqual({c['name']:c.get('parent') for c in classes if c['tier']>1}, {'클레릭':'시스터','카발리스트':'클레릭','다크메이지':'위치','블러드메이지':'다크메이지'})
        self.assertEqual(sum(len(c['skills']) for c in classes), 10)
        self.assertEqual(classes[2]['skills'][0]['range'], '자신')
        self.assertIn('광휘', gen.ELEMENT_TYPES)

    def test_artifact_order_and_edge_values(self):
        artifacts = read('artifacts/irene.json')
        self.assertEqual(read('characters/irene.json')[0]['artifacts'], [a['name'] for a in artifacts])
        self.assertEqual([a['name'] for a in artifacts], ['핏빛 마력 구슬','원소통달: 광휘','순례자의 덧신'])
        for a in artifacts:
            self.assertEqual([l['step'] for l in a['levels']], [3,4,5,6])
        buffs = {b['name']:b for b in read('buffs/irene.json')}
        overflow = buffs['넘치는 마력']['levels']
        self.assertIn('[+10%]{red}',overflow[1]['effect'])
        self.assertEqual([l['duration'] for l in overflow], [1,1,1,2])
        self.assertNotIn('쿨타임', artifacts[0]['levels'][1]['effect'])
        self.assertIn('쿨타임', artifacts[0]['levels'][2]['effect'])

    def test_manifest_four_matches_screenshot_6219(self):
        buffs = {b['name']:b for b in read('buffs/irene.json')}
        expected = {
            '정화의 장막': '물리/마법 관통 [+10%]{red}. 주문력의 [40%]{red} 보호막. 이 효과 적용 시 디버프 [1]{red}개 해제.',
            '보호의 장막': '받는 치명타 확률 [-20%]{red}. 주문력의 [50%]{red} 보호막.',
        }
        for name, effect in expected.items():
            stage4 = next(l for l in buffs[name]['levels'] if l['level']==4)
            self.assertEqual(stage4['effect'], effect)
            self.assertEqual(stage4['duration'], 2)

    def test_unknown_values_are_not_invented(self):
        buffs = {b['name']:b for b in read('buffs/irene.json')}
        for l in buffs['회복']['levels']:
            self.assertNotIn('duration',l)
        w = read('weapons/irene.json')[0]
        self.assertEqual([s['maxHp'] for s in w['baseStats']], [130,131,132,134,135,136])
        self.assertTrue(all(set(s)=={'step','maxHp'} for s in w['baseStats']))
        for e in w['effects']:
            self.assertEqual([l['step'] for l in e['levels']], list(range(1,7)))

if __name__ == '__main__':
    unittest.main()
