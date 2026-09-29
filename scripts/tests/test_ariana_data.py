"""Source-backed regression checks; does not connect to any database."""
import json
import unittest
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / 'data'

def read(path):
    return json.loads((DATA / path).read_text())

class ArianaDataTests(unittest.TestCase):
    def test_character_and_steps(self):
        c = read('characters/ariana.json')[0]
        self.assertEqual((c['releaseDate'], c['appearedIn'], c['faction']), ('2024-01-09', '창세기전2', '커티스'))
        self.assertNotIn('stats', c)
        self.assertEqual([(l['type'], l['step']) for l in c['passive']['levels']], [('각성', n) for n in [3,4,5,6]] + [('발현', n) for n in [2,4,6]])
        u=c['ultimate']
        self.assertEqual((u['name'], u['attackType'], u['element']), ('화염인','관통','화염'))
        self.assertEqual([l['step'] for l in u['levels']], [0,1,3,5])
        for l,damage,chance in zip(u['levels'], [90,100,110,120], [25,30,30,35]):
            self.assertIn(f'[{damage}%]{{red}}',l['effect'])
            self.assertIn(f'[{chance}%]{{red}}',l['effect'])
        self.assertEqual(c['artifacts'], ['속성 과부하','최상의 상태','질풍의 깃'])

    def test_classes_and_skills(self):
        classes=read('classes/archer_line.json')
        self.assertEqual(len(classes),6)
        self.assertEqual(sum(len(c['skills']) for c in classes),8)
        parents={c['name']:c.get('parent') for c in classes}
        self.assertEqual(parents, {'아처':None,'헌터':'아처','막스맨':'아처','이글':'헌터','보우마스터':'헌터','스나이퍼':'막스맨'})
        self.assertEqual([s['name'] for s in classes[0]['skills']], ['궁수의 징표','귀살인','경계 사격'])

    def test_weapon_owners_and_duration(self):
        w=read('weapons/ariana.json')[0]
        for e,chance,turn in zip(w['effects'],[50,30,25],[2,2,1]):
            self.assertEqual([l['step'] for l in e['levels']],list(range(1,7)))
            for l in e['levels']:
                self.assertIn(f'[{chance}%]{{red}}',l['effect'])
                self.assertIn(f'[{turn}]{{yellow}}턴',l['effect'])
        self.assertIn('Jr. 전용',w['effects'][1]['levels'][0]['effect'])
        mark=next(d for d in read('debuffs/ariana.json') if d['name']=='화염 낙인')
        self.assertNotIn('duration',mark)
        self.assertEqual(len(mark['levels']),6)

    def test_shared_effects_not_duplicated(self):
        for kind in ['buffs','debuffs','artifacts','classes','characters','weapons']:
            names=[o['name'] for path in sorted((DATA/kind).glob('*.json')) for o in json.loads(path.read_text())]
            self.assertEqual(len(names),len(set(names)),kind)
        self.assertEqual([l['step'] for l in read('artifacts/ariana.json')[0]['levels']],[3,4,5,6])

if __name__ == '__main__':
    unittest.main()
