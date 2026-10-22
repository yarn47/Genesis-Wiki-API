import json
import re
import unittest
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / 'data'

def read(kind):
    return json.loads((DATA / kind / 'sharn.json').read_text())

def buff(name):
    return next(x for x in read('buffs') if x['name'] == name)

class SharnTests(unittest.TestCase):
    def test_profile_and_references(self):
        c = read('characters')[0]
        self.assertEqual((c['releaseDate'], c['appearedIn']), ('2024-06-25', '템페스트'))
        self.assertEqual((c['faction'],c['element'],c['cv']),('무소속','욕망의그림자','김혜성'))
        self.assertEqual((c['birthYear'],c['height']),('불명','187cm'))
        self.assertNotIn('stats',c)
        for kind,names in [('classes',c['classTree']),('artifacts',c['artifacts']),('weapons',[c['exclusiveWeapon']])]:
            available=[x['name'] for p in (DATA/kind).glob('*.json') for x in json.loads(p.read_text())]
            for name in names:
                self.assertEqual(available.count(name),1)
        self.assertEqual(c['artifacts'],['바람 걸음','필살의 의지','전사의 정수'])
        available=set()
        for kind in ['buffs','debuffs']:
            for p in (DATA/kind).glob('*.json'):
                for b in json.loads(p.read_text()):
                    available.add(b['name'])
                    available.update(l.get('name',f'{b["name"]} {l["level"]}') for l in b.get('levels',[]))
        for kind in ['characters','classes','buffs','weapons']:
            for name in re.findall(r'\[([^\[\]]+)\]\{(?:green|orange)\}',json.dumps(read(kind),ensure_ascii=False)):
                self.assertIn(name,available)

    def test_passive_thresholds(self):
        levels=read('characters')[0]['passive']['levels']
        self.assertEqual([(l['type'],l['step']) for l in levels],[('각성',s) for s in [3,4,5,6]]+[('발현',s) for s in [2,4,6]])
        for i,l in enumerate(levels):
            self.assertIn(f'[{[45,55,60,70,75,80,85][i]}%]',l['effect'])
            self.assertIn(f'[왕자의 이중 생활 {i+1}]',l['effect'])
            self.assertIn('다른 아군이 없다면',l['effect'])
            self.assertIn('추가 행동',l['effect'])
            self.assertIn('추가 이동',l['effect'])
            self.assertEqual('여성 캐릭터' in l['effect'],i>=4)
            if i>=4:
                self.assertIn(f'[{(i-3)*10}%]',l['effect'])

    def test_passive_buff_progression(self):
        b=buff('왕자의 이중 생활')
        self.assertEqual((b['duration'],b['tags']),(2,['해제 불가']))
        for i,l in enumerate(b['levels']):
            self.assertEqual(l['level'],i+1)
            self.assertIn(f'[+{[10,15,25,30,30,40,50][i]}%]',l['effect'])
            self.assertEqual('TP 제거 면역' in l['effect'],i>=2)
            self.assertEqual('치유 불가' in l['effect'],i>=5)
            self.assertIn(f'[{2 if i==6 else 1}]{{yellow}} [TP]',l['effect'])

    def test_ultimate(self):
        u=read('characters')[0]['ultimate']
        self.assertEqual((u['tpCost'],u['range'],u['cooldown'],u['attackType']),(5,'자신',5,'타격'))
        self.assertEqual(u['tags'],['원거리','추방상태공격'])
        self.assertEqual([l['step'] for l in u['levels']],[0,1,3,5])
        for i,l in enumerate(u['levels']):
            self.assertIn('남은 체력의 [50%]',l['effect'])
            self.assertIn(f'[{[40,43,46,50][i]}%]',l['effect'])
            self.assertIn(f'[{140+i*10}%]',l['effect'])
            self.assertIn('주변 [3]{red}바퀴',l['effect'])

    def test_classes(self):
        cs=read('classes')
        self.assertEqual([c['parent'] for c in cs],['파이터','소드맨','나이트워커'])
        self.assertEqual([c['moveRange'] for c in cs],[4,3,4])
        for c,values in [(cs[0],[20,25]),(cs[2],[40,50])]:
            for key,value in zip(['lv1','lv2'],values):
                self.assertEqual(c['passive'][key].count(f'[{value}%]'),3)
                self.assertIn('턴 당 한번',c['passive'][key])
        for key,value in zip(['lv1','lv2'],[30,40]):
            self.assertIn(f'[{value}%]',cs[1]['passive'][key])
            self.assertIn('[25%]',cs[1]['passive'][key])
        self.assertEqual(buff('어둠 장막 (다크프린스)')['maxStack'],3)
        shared=json.loads((DATA/'buffs/rogue_line.json').read_text())
        self.assertEqual(next(b for b in shared if b['name']=='어둠 장막')['maxStack'],5)
        self.assertEqual(cs[0]['skills'][0]['tpCost'],3)
        self.assertIn('치명타 피해',cs[0]['skills'][0]['effect'])
        self.assertIn('모두 소모',cs[1]['skills'][0]['effect'])
        self.assertIn('체력이 [1]{red} 미만',cs[1]['skills'][0]['effect'])
        for c in cs[1:]:
            self.assertNotIn('tpCost',c['skills'][0])
        self.assertEqual(cs[2]['skills'][0]['cooldown'],1)
        self.assertIn('사용한 스킬의 쿨타임',cs[2]['skills'][0]['effect'])

    def test_weapon(self):
        w=read('weapons')[0]
        self.assertEqual([s['maxHp'] for s in w['baseStats']],[130,131,132,134,135,136])
        self.assertEqual([s['attack'] for s in w['baseStats']],[342,345,349,353,356,360])
        for e in w['effects']:
            self.assertEqual([l['step'] for l in e['levels']],list(range(1,7)))
            for i,l in enumerate(e['levels']):
                self.assertIn('적이 살아있을 경우',l['effect'])
                if e['type']=='전용':
                    self.assertIn(f'[{[30,35,45,50,55,60][i]}%]',l['effect'])
                    self.assertIn(f'쿨타임 [{4 if i<4 else 3}]',l['effect'])
                    self.assertIn('[2]{yellow}턴 동안',l['effect'])
        for name,base in [('뇌신의 부름',25),('썬더 스톰',15)]:
            for i,l in enumerate(buff(name)['levels']):
                self.assertIn(f'[{base+i*5}%]',l['effect'])
                self.assertIn('[1]{yellow}턴 간 [감전]',l['effect'])

if __name__ == '__main__':
    unittest.main()
