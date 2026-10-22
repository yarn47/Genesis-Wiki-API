import json
import re
import unittest
from pathlib import Path
DATA = Path(__file__).resolve().parents[2] / 'data'
def read(kind):
    return json.loads((DATA / kind / 'chris.json').read_text())
class ChrisTests(unittest.TestCase):
    def test_profile_and_links(self):
        c=read('characters')[0]
        self.assertEqual((c['releaseDate'],c['appearedIn']),('2024-07-23','서풍의 광시곡'))
        self.assertEqual((c['faction'],c['subFaction'],c['element']),('게이시르','제피르팰컨','활력의나무'))
        self.assertNotIn('stats',c)
        for kind,names in [('classes',c['classTree']),('weapons',[c['exclusiveWeapon']]),('artifacts',c['artifacts'])]:
            available=[x['name'] for p in (DATA/kind).glob('*.json') for x in json.loads(p.read_text())]
            for name in names: self.assertEqual(available.count(name),1)
        available=set()
        for kind in ['buffs','debuffs']:
            for p in (DATA/kind).glob('*.json'):
                for b in json.loads(p.read_text()):
                    available.add(b['name'])
                    available.update(l.get('name',f'{b["name"]} {l["level"]}') for l in b.get('levels',[]))
        for kind in ['characters','classes','buffs','debuffs','weapons','artifacts']:
            for name in re.findall(r'\[([^\[\]]+)\]\{(?:green|orange)\}',json.dumps(read(kind),ensure_ascii=False)):
                self.assertIn(name,available)
    def test_passive(self):
        p=read('characters')[0]['passive']['levels']
        self.assertEqual([(l['type'],l['step']) for l in p],[('각성',s) for s in [3,4,5,6]]+[('발현',s) for s in [2,4,6]])
        for i,l in enumerate(p):
            self.assertIn(f'[+{[20,20,25,25,30,35,40][i]}%]',l['effect'])
            self.assertIn(f'[운명의 속삭임 {i+1}]',l['effect'])
            self.assertEqual('최대 체력' in l['effect'],i>=4)
            self.assertEqual('예리한 일격' in l['effect'],i>=2)
            self.assertEqual('약점 방어' in l['effect'],i>=4)
    def test_buff_conditions(self):
        b={x['name']:x for x in read('buffs')}
        for i,l in enumerate(b['운명의 속삭임']['levels']):
            self.assertEqual(l['duration'],1)
            self.assertIn('탄환이 있어야',l['effect'])
            self.assertIn(f'[{[40,45,50,55,60,70,80][i]}%]',l['effect'])
            self.assertEqual('사거리 [+1]' in l['effect'],i>=4)
        for i,l in enumerate(b['약점 방어']['levels']):
            self.assertIn('[30~80%]',l['effect'])
            self.assertIn(f'[{[20,25,30][i]}%]',l['effect'])
            self.assertEqual('징표' in l['effect'],i==2)
        self.assertEqual(b['운명의 활기']['duration'],'영구')
        for i,l in enumerate(b['강화 코어']['levels']):
            self.assertEqual((l['duration'],l['maxStack']),(2,5))
            self.assertIn(f'[+{i+5}%]',l['effect'])
            self.assertIn('적에게 보이지 않음',l['effect'])
        self.assertIn('마법 피해',b['마탄']['description'])
        self.assertNotIn('고정',b['마탄']['description'])
        self.assertIn('물리 고정',b['철갑탄']['description'])
        self.assertIn('방어 무시 물리',b['정밀탄']['description'])
    def test_classes(self):
        c={x['name']:x for x in read('classes')}
        self.assertEqual(len(c),6)
        self.assertEqual(c['스핏파이어']['parent'],'건슬링어')
        self.assertEqual(c['레퀴엠']['parent'],'건블레이더')
        self.assertEqual(sum(len(x['skills']) for x in c.values()),8)
        for x in c.values():
            self.assertEqual((x['weaponType'],x['defenseType'],x['attackRange'],x['moveRange']),('권총','미디엄',4,3))
        self.assertIn('최대 탄환 수 : [4]',c['스핏파이어']['passive']['lv2'])
        self.assertIn('이번 턴',c['스핏파이어']['passive']['lv2'])
        self.assertIn('클래스 패시브 봉쇄 불가',c['레퀴엠']['passive']['lv2'])
        self.assertIn('[50%]',c['레퀴엠']['passive']['lv2'])
        self.assertIn('최대 [15%]',c['레퀴엠']['passive']['lv2'])
        self.assertEqual(c['건블레이더']['skills'][0]['attackType'],'참격')
        self.assertIn('소모된 모든 탄환',c['에이스']['skills'][0]['effect'])
        for name in ['스핏파이어','레퀴엠']:
            self.assertIn('탄환 전부 소모',c[name]['skills'][0]['effect'])
            self.assertIn('탄환 수로 제한',c[name]['skills'][0]['effect'])
    def test_artifacts(self):
        a=read('artifacts')
        self.assertEqual(len(a),4)
        for x in a: self.assertEqual([l['step'] for l in x['levels']],[3,4,5,6])
        self.assertIn('[+60%]',a[0]['levels'][-1]['effect'])
        self.assertIn('[+20%]',a[1]['levels'][-1]['effect'])
        self.assertIn('[60%]',a[2]['levels'][-1]['effect'])
        self.assertIn('[예비탄창 2]',a[3]['levels'][-1]['effect'])
    def test_weapon(self):
        w=read('weapons')[0]
        self.assertEqual([s['maxHp'] for s in w['baseStats']],[116,117,118,120,121,122])
        self.assertEqual([s['attack'] for s in w['baseStats']],[364,367,371,375,378,382])
        for e in w['effects']: self.assertEqual([l['step'] for l in e['levels']],list(range(1,7)))
        for i,l in enumerate(w['effects'][0]['levels']):
            self.assertIn('[+1]' if i<3 else '[+2]',l['effect'])
            self.assertIn(f'[강화 코어 {i+1}]',l['effect'])
            self.assertIn(f'[짜릿한 한발 {[1,1,2,2,2,3][i]}]',l['effect'])
        for i,l in enumerate(w['effects'][1]['levels']):
            self.assertIn(f'[{10+i}%]',l['effect'])
            self.assertIn('쿨타임 [3]',l['effect'])
        for i,l in enumerate(read('debuffs')[1]['levels']):
            self.assertEqual((l['duration'],l['maxStack']),(2,2))
            self.assertIn(f'[{[20,30,40][i]}%]',l['effect'])
            self.assertEqual('TP +1' in l['effect'],i>=1)
    def test_ultimate(self):
        u=read('characters')[0]['ultimate']
        self.assertEqual((u['tpCost'],u['range'],u['cooldown']),(5,[1,3],5))
        self.assertEqual([l['step'] for l in u['levels']],[0,1,3,5])
        for i,l in enumerate(u['levels']):
            self.assertIn(f'[{170+i*10}%]',l['effect'])
            self.assertIn('탄환을 소모하지 않습니다',l['effect'])
        self.assertIn('[TP 2]',u['levels'][-1]['effect'])
        self.assertIn('각각 [35%]',u['levels'][-1]['effect'])
