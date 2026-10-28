import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load(kind):
    return json.loads((ROOT / 'data' / kind / 'emilio.json').read_text())

class EmilioDataTests(unittest.TestCase):
    def test_identity(self):
        c = load('characters')[0]
        self.assertEqual(c['releaseDate'], '2024-11-12')
        self.assertEqual(c['appearedIn'], '템페스트')
        self.assertEqual((c['faction'], c['subFaction']), ('템페스트 서커스단', '주신'))
        self.assertTrue(c['published'])
        self.assertNotIn('stats', c)

    def test_ultimate_gap(self):
        u = load('characters')[0]['ultimate']
        self.assertEqual([l['step'] for l in u['levels']], [0,1,3,5])
        for l, dmg in zip(u['levels'], [150,160,170,180]):
            self.assertIn(f'[{dmg}%]', l['effect'])
            self.assertIn('버프를 모두 지우고', l['effect'])
        self.assertEqual((u['tpCost'], u['range'], u['cooldown']), (5, '자신', 5))

    def test_passive(self):
        ls = load('characters')[0]['passive']['levels']
        self.assertEqual([(l['type'],l['step']) for l in ls], [('각성',3),('각성',4),('각성',5),('각성',6),('발현',2),('발현',4),('발현',6)])
        self.assertNotIn('TP', ls[1]['effect'])
        self.assertIn('[1 TP]', ls[2]['effect'])
        for l, attack in zip(ls[4:], [5,8,10]):
            self.assertIn(f'[{attack}%]', l['effect'])

    def test_mind_sword_and_immunities(self):
        b = {x['name']:x for x in load('buffs')}
        self.assertEqual(b['심검']['maxStack'], 5)
        self.assertEqual(b['심검']['duration'], '영구')
        self.assertIn('[70%]', b['심검']['description'])
        ls=b['신비한 관리인']['levels']
        for i,l in enumerate(ls):
            self.assertEqual('이동 방해' in l['effect'], i>=1)
            self.assertEqual('TP 제거' in l['effect'], i==2)

    def test_classes(self):
        cs=load('classes')
        self.assertEqual([c['parent'] for c in cs], ['파이터','기검사','기검사'])
        self.assertEqual([c['name'] for c in cs], ['기검사','검선','아르젠센티넬'])
        self.assertEqual([c['skills'][0]['tpCost'] for c in cs], [1,2,1])
        self.assertEqual([c['skills'][0]['cooldown'] for c in cs], [4,3,4])
        for c in cs:
            self.assertEqual((c['attackRange'],c['moveRange']), (1,3))

    def test_weapon_and_buff_progression(self):
        w=load('weapons')[0]
        self.assertEqual([s['maxHp'] for s in w['baseStats']], [130,131,132,134,135,136])
        self.assertEqual([s['attack'] for s in w['baseStats']], [342,345,349,353,356,360])
        b={x['name']:x for x in load('buffs')}
        for l,count in zip(b['월식']['levels'], [1,1,2,2,3,None]):
            self.assertIn('모두' if count is None else f'[{count}]', l['effect'])
            self.assertNotIn('duration',l)
        for l in b['달빛 충전']['levels']:
            self.assertIn('[1]',l['effect'])
        for e in w['effects']:
            self.assertEqual(len(e['levels']),6)
            self.assertTrue(all('[0.1%]' in l['effect'] for l in e['levels']))

    def test_artifact(self):
        a=load('artifacts')[0]
        self.assertEqual(a['name'], '시간의 비수')
        for l, atk, heal in zip(a['levels'], [15,20,25,30], [30,40,50,60]):
            self.assertIn(f'[+{atk}%]',l['effect'])
            self.assertIn(f'[{heal}%]',l['effect'])

    def test_faction_wiring(self):
        self.assertIn('"주신": "jushin"', (ROOT/'scripts/gen_sql.py').read_text())
        self.assertIn('jushin', (ROOT/'Wiki-API/src/main/kotlin/com/genesis/wiki/entity/Enums.kt').read_text())
        migration=(ROOT/'db/migrations/017_jushin_faction.sql').read_text()
        self.assertEqual(migration.count("'jushin'"),2)

if __name__ == '__main__':
    unittest.main()
