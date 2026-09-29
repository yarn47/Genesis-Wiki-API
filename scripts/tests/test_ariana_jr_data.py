import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('gen_sql', ROOT / 'scripts/gen_sql.py')
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

def read(path):
    return json.loads((ROOT / 'data' / path).read_text())[0]

class ArianaJrTests(unittest.TestCase):
    def test_profile_and_passive(self):
        c = read('characters/ariana_jr.json')
        self.assertFalse(c['hasManifestation'])
        self.assertEqual(c['grade'], '희귀')
        self.assertNotIn('stats', c)
        self.assertEqual([l['step'] for l in c['passive']['levels']], list(range(1,7)))
        for i,(l,n) in enumerate(zip(c['passive']['levels'],[5,6,6,8,8,10])):
            self.assertEqual(l['type'],'각성')
            self.assertIn(f'[{n}%]{{red}}',l['effect'])
            if i >= 2:
                self.assertIn(f'사거리가 [{2 if i >= 4 else 1}]{{red}}',l['effect'])
            else:
                self.assertNotIn('다음 턴', l['effect'])

    def test_no_manifest_keeps_ultimate_owner(self):
        c = read('characters/ariana_jr.json')
        self.assertEqual([l['step'] for l in c['ultimate']['levels']], [0])
        self.assertEqual(c['ultimate']['levels'],read('characters/ariana.json')['ultimate']['levels'][:1])
        generated = gen.character_sql(c)
        hub = generated.split('INSERT INTO character_manifestation')[1]
        self.assertIn('(@id, 0, @ult, NULL, NULL, NULL, NULL, NULL)', hub)
        self.assertNotIn('(@id, 3,',hub)
        self.assertIn('(@id, 3,',gen.character_sql(read('characters/ariana.json')).split('INSERT INTO character_manifestation')[1])

    def test_shared_classes_and_metadata(self):
        c = read('characters/ariana_jr.json')
        father = read('characters/ariana.json')
        for key in ['releaseDate','appearedIn','exclusiveWeapon']:
            self.assertEqual(c[key],father[key])
        self.assertEqual(c['classTree'],father['classTree'][:-1]+['샤프슈터'])
        cls = read('classes/sharpshooter.json')
        self.assertEqual(cls['parent'],'막스맨')
        self.assertEqual(cls['skills'][0]['name'],'유성시')
        self.assertIn('[40%]{red}',cls['passive']['lv2'])
        self.assertEqual(c['artifacts'],[])

if __name__ == '__main__':
    unittest.main()
