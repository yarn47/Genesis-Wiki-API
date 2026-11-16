import json
import unittest
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / 'data'

def read(kind):
    return json.loads((DATA / kind / 'deimos.json').read_text())

class DeimosDataTest(unittest.TestCase):
    def test_identity_and_release(self):
        c = read('characters')[0]
        self.assertEqual((c['name'], c['appearedIn'], c['releaseDate']),
                         ('혼돈의 데이모스', '창세기전2', '2025-06-24'))

    def test_passive_and_ultimate_steps(self):
        c = read('characters')[0]
        self.assertEqual([x['step'] for x in c['passive']['levels']], [3,4,5,6,2,4,6])
        self.assertEqual([x['step'] for x in c['ultimate']['levels']], [0,1,3,5])
        for entry, damage in zip(c['ultimate']['levels'], [120,130,140,150]):
            self.assertIn(f'[{damage}%]', entry['effect'])

    def test_class_tree_and_shared_class(self):
        c = read('characters')[0]
        self.assertEqual(len(c['classTree']), 6)
        classes = {x['name']:x for x in read('classes')}
        self.assertNotIn('다크메이지', classes)
        self.assertEqual(classes['오멘세이지']['parent'], '다크메이지')
        self.assertEqual(classes['어비스프리스트']['parent'], '블러드컬티스트')
        self.assertEqual({x['name'] for x in classes['애콜라이트']['skills']},
                         {'수혈','엑스터시','다크 블래스트'})

    def test_artifacts_and_weapon(self):
        self.assertEqual(len(read('artifacts')), 3)
        for a in read('artifacts'):
            self.assertEqual([x['step'] for x in a['levels']], [3,4,5,6])
        w = read('weapons')[0]
        self.assertEqual([x['spellAttack'] for x in w['baseStats']], [342,345,349,353,356,360])
        for effect in w['effects']:
            self.assertEqual([x['step'] for x in effect['levels']], [1,2,3,4,5,6])

    def test_same_name_debuff_preserved(self):
        d = next(x for x in read('debuffs') if x['name']=='혼돈의 균열 (카오스 블러드)')
        self.assertEqual([x['name'] for x in d['levels']], [f'혼돈의 균열 {i}' for i in range(1,7)])
        jane = json.loads((DATA/'debuffs/jane.json').read_text())
        self.assertIn('[-25%]', next(x for x in jane if x['name']=='혼돈의 균열')['description'])

if __name__ == '__main__':
    unittest.main()
