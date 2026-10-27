import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
def load(kind):
    return json.loads((ROOT / 'data' / kind / 'marie.json').read_text())

class MarieDataTests(unittest.TestCase):
    def test_identity_and_progression(self):
        c = load('characters')[0]
        self.assertEqual(c['releaseDate'], '2024-09-03')
        self.assertEqual(c['appearedIn'], '템페스트')
        self.assertEqual(c['subFaction'], '템페스트 서커스단')
        self.assertEqual([(x['type'],x['step']) for x in c['passive']['levels']], [('각성',3),('각성',4),('각성',5),('각성',6),('발현',2),('발현',4),('발현',6)])
        self.assertEqual([x['step'] for x in c['ultimate']['levels']], [0,1,3,5])
        self.assertEqual(c['ultimate']['tags'], ['지향성','위치제어'])
        for v,l in zip([115,120,130,140],c['ultimate']['levels']):
            self.assertIn(f'[{v}%]',l['effect'])
            self.assertIn('한명이라면 두배',l['effect'])

    def test_final_passive_and_stacks(self):
        p=load('characters')[0]['passive']['levels'][-1]['effect']
        self.assertIn('추가타 피해량이 [60%]',p)
        self.assertIn('협공 피해량이 [50%]',p)
        self.assertIn('공격력의 [50%]',p)
        b=load('buffs')[0]['levels']
        self.assertEqual([x['duration'] for x in b],[2,3,3,4,4,4,4])
        self.assertTrue(all(x['maxStack']==4 for x in b))
        self.assertIn('[-15%]',b[-1]['effect'])

    def test_weapon(self):
        w=load('weapons')[0]
        self.assertEqual([s['maxHp'] for s in w['baseStats']],[141,142,143,145,146,147])
        self.assertEqual([s['attack'] for s in w['baseStats']],[316,319,323,327,330,334])
        for e in w['effects']:
            self.assertEqual([l['step'] for l in e['levels']],list(range(1,7)))
            for cd,l in zip([3,3,2,2,1,1],e['levels']):
                self.assertIn(f'쿨타임 [{cd}]',l['effect'])
        effects=next(b for b in load('buffs') if b['name']=='황홀한 유린')['levels']
        self.assertTrue(all('약화' not in l['effect'] for l in effects[:3]))
        self.assertTrue(all('약화' in l['effect'] for l in effects[3:]))

    def test_classes_and_artifact(self):
        c=load('classes')
        self.assertEqual([x['parent'] for x in c],['레인저','도미넌트','도미넌트'])
        self.assertEqual(c[2]['skills'][0]['range'],[2,2])
        self.assertIn('디버프 개수만큼',c[1]['passive']['lv2'])
        self.assertIn('첫 피해',c[2]['passive']['lv2'])
        self.assertEqual([x['step'] for x in load('artifacts')[0]['levels']],[3,4,5,6])
        thorn=next(b for b in load('buffs') if b['name']=='질투의 가시')
        self.assertNotIn('duration',thorn)
        self.assertEqual([l['maxStack'] for l in thorn['levels']],[3]*4)

    def test_faction_definitions_match(self):
        self.assertIn('"템페스트 서커스단": "tempest_circus"',(ROOT/'scripts/gen_sql.py').read_text())
        self.assertIn('tempest_circus',(ROOT/'Wiki-API/src/main/kotlin/com/genesis/wiki/entity/Enums.kt').read_text())
        migration=(ROOT/'db/migrations/016_tempest_circus_faction.sql').read_text()
        self.assertEqual(migration.count("'tempest_circus'"),2)

if __name__=='__main__':
    unittest.main()
