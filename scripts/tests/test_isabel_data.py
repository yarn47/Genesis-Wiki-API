import json
import unittest
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / 'data'

def read(kind):
    return json.loads((DATA / kind / 'isabel.json').read_text())

class IsabelDataTest(unittest.TestCase):
    def test_identity(self):
        c = read('characters')[0]
        self.assertEqual((c['releaseDate'], c['appearedIn']), ('2025-04-01', '서풍의 광시곡'))
        self.assertEqual((c['faction'], c['subFaction']), ('게이시르', '제피르팰컨'))
        self.assertNotIn('stats', c)

    def test_passive_user_confirmed_awaken_four(self):
        levels = read('characters')[0]['passive']['levels']
        self.assertEqual([(x['type'], x['step']) for x in levels], [('각성',3),('각성',4),('각성',5),('각성',6),('발현',2),('발현',4),('발현',6)])
        four = levels[1]['effect']
        self.assertIn('[+25%]{red}', four)
        self.assertIn('[15%]{red}', four)
        self.assertNotIn('반격 사정거리', four)
        self.assertIn('주위 [2]{red}칸', levels[-1]['effect'])

    def test_ultimate_gap(self):
        levels = read('characters')[0]['ultimate']['levels']
        for level, step, value in zip(levels, [0,1,3,5], [70,80,90,100]):
            self.assertEqual(level['step'], step)
            self.assertEqual(level['effect'].count(f'[{value}%]{{red}}'), 2)
            self.assertIn('[1]{yellow}턴 동안 [기절]{orange}', level['effect'])

    def test_tree_and_artifacts(self):
        self.assertEqual([(x['name'], x['parent']) for x in read('classes')], [('워로드','가드'),('랜스워든','가드'),('아이언가디언','가디언')])
        self.assertEqual(read('characters')[0]['artifacts'], ['최상의 상태','응징의 서약','방패의 공명','재기의 바람'])
        self.assertEqual([x['step'] for x in read('artifacts')[0]['levels']], [3,4,5,6])

    def test_weapon_before_after_and_dispel(self):
        weapon = read('weapons')[0]
        exclusive, normal = weapon['effects']
        for x in exclusive['levels']:
            self.assertIn('전투 전', x['effect'])
            self.assertIn('[50%]{red}만큼 물리 고정', x['effect'])
            self.assertEqual('버프를' in x['effect'], x['step'] >= 5)
        for x in normal['levels']:
            self.assertIn('전투 후', x['effect'])
            self.assertIn('[30%]{red}만큼 물리 고정', x['effect'])
            self.assertEqual('버프를' in x['effect'], x['step'] == 6)
        self.assertEqual(weapon['baseStats'][-1], {'step':6,'maxHp':143,'attack':339,'defense':30})

    def test_duration_variant(self):
        slow = next(x for x in read('debuffs') if x['name'] == '느려짐 1 (지면 분쇄)')
        self.assertEqual(slow['duration'], 2)
        self.assertEqual(slow['description'], '이동력 [-1]{red}.')

if __name__ == '__main__':
    unittest.main()
