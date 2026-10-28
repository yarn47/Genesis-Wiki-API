import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load(kind):
    return json.loads((ROOT / 'data' / kind / 'joan.json').read_text())

class JoanDataTests(unittest.TestCase):
    def test_identity_and_ultimate(self):
        c = load('characters')[0]
        self.assertEqual(c['name'], '죠안 카트라이트')
        self.assertEqual(c['releaseDate'], '2024-10-01')
        self.assertEqual(c['appearedIn'], '창세기전3')
        self.assertEqual(c['faction'], '게이시르')
        self.assertEqual(c['element'], '신념의빛')
        self.assertEqual([(v['type'],v['step']) for v in c['passive']['levels']], [('각성',3),('각성',4),('각성',5),('각성',6),('발현',2),('발현',4),('발현',6)])
        self.assertEqual([v['step'] for v in c['ultimate']['levels']], [0,1,3,5])
        for v,a,b in zip(c['ultimate']['levels'],[65,70,75,80],[25,30,35,40]):
            self.assertIn(f'[{a}%]',v['effect'])
            self.assertIn(f'[{b}%]',v['effect'])
            for absent in ['추가 이동','추가 행동','회복']:
                self.assertNotIn(absent,v['effect'])

    def test_special_jurisdiction(self):
        buffs = {b['name']: b for b in load('buffs')}
        b = buffs['특별 사법권']
        self.assertEqual(b['duration'],'영구')
        self.assertEqual(b['maxStack'],3)
        self.assertEqual([v['level'] for v in b['levels']],list(range(1,8)))
        self.assertNotIn('디버프',b['levels'][4]['effect'])
        self.assertIn('디버프를 모두 지우고',b['levels'][5]['effect'])
        self.assertNotIn('TP',b['levels'][5]['effect'])
        self.assertIn('[1]{yellow} TP',b['levels'][6]['effect'])
        for v in buffs['수사']['levels']:
            self.assertNotIn('duration',v)
            self.assertIn('캐릭터 턴 종료 시까지',v['effect'])
        for v,n in zip(buffs['경호']['levels'],[5,7,8,10,13,16,20]):
            self.assertEqual(v['duration'],2)
            self.assertIn(f'[{n}%]',v['effect'])
            self.assertEqual('선제 공격' in v['effect'],v['level']>=3)

    def test_classes_and_artifacts(self):
        cls=load('classes')
        self.assertEqual([c['parent'] for c in cls],['발키리','임페리얼발키리','임페리얼발키리'])
        self.assertEqual([c['skills'][0]['name'] for c in cls],['파쇄혼','역돌','크랙 다운'])
        self.assertNotIn('allowedWeapon',cls[2]['skills'][0])
        self.assertEqual(load('characters')[0]['classTree'],['발키리','비프로스트발키리','임페리얼발키리','디바인발키리','로얄발키리','시큐리티발키리'])
        self.assertEqual(load('characters')[0]['artifacts'],['칼날 피뢰침','우아한 호흡','바람 걸음'])
        d=load('debuffs')[0]
        self.assertEqual(d['name'],'단속')
        self.assertEqual(d['duration'],2)
        self.assertEqual(d['tags'],['노출'])

    def test_weapon(self):
        w=load('weapons')[0]
        self.assertEqual([v['maxHp'] for v in w['baseStats']],[141,142,143,145,146,147])
        self.assertEqual([v['attack'] for v in w['baseStats']],[316,319,323,327,330,334])
        self.assertEqual([v['physPen'] for v in w['baseStats']],[10,11,12,13,14,15])
        self.assertEqual([v['critRate'] for v in w['baseStats']],[10,11,12,13,14,15])
        for i,v in enumerate(w['effects'][0]['levels']):
            self.assertIn(f'[{50+i*5}%]',v['effect'])
            self.assertIn(f'[{15+i}%]',v['effect'])
            self.assertIn(f'쿨타임: [{3 if i<4 else 2}]',v['effect'])
        self.assertEqual(w['effects'][1]['type'],'일반')

if __name__ == '__main__':
    unittest.main()
