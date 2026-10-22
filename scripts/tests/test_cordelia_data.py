import json
import re
import unittest
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / 'data'

def read(kind):
    return json.loads((DATA / kind / 'cordelia.json').read_text())

def named(kind, name):
    return next(x for x in read(kind) if x['name'] == name)

class CordeliaTests(unittest.TestCase):
    def test_profile_references(self):
        c = read('characters')[0]
        self.assertEqual((c['releaseDate'], c['appearedIn']), ('2024-06-18', '템페스트'))
        self.assertEqual((c['faction'], c['element'], c['cv']), ('커티스', '지성의결정체', '오로아'))
        self.assertEqual((c['birthYear'], c['height']), ('에스겔력 1259년', '141cm'))
        self.assertNotIn('stats', c)
        for kind, names in [('classes', c['classTree']), ('artifacts', c['artifacts']), ('weapons', [c['exclusiveWeapon']])]:
            available = [x['name'] for p in (DATA / kind).glob('*.json') for x in json.loads(p.read_text())]
            for name in names:
                self.assertEqual(available.count(name), 1)
        available = set()
        for kind in ['buffs', 'debuffs']:
            for p in (DATA / kind).glob('*.json'):
                for b in json.loads(p.read_text()):
                    available.add(b['name'])
                    available.update(l.get('name', f'{b["name"]} {l["level"]}') for l in b.get('levels', []))
        for kind in ['characters', 'classes', 'buffs', 'weapons', 'artifacts']:
            for name in re.findall(r'\[([^\[\]]+)\]\{(?:green|orange)\}', json.dumps(read(kind), ensure_ascii=False)):
                self.assertIn(name, available)

    def test_passive_and_bombs(self):
        levels = read('characters')[0]['passive']['levels']
        self.assertEqual([(l['type'],l['step']) for l in levels], [('각성',s) for s in [3,4,5,6]] + [('발현',s) for s in [2,4,6]])
        for i,l in enumerate(levels):
            self.assertIn(f'퓨즈 폭탄 {min(i+1,4)}',l['effect'])
            self.assertIn(f'테슈브의 낙진 {min(i+1,4)}',l['effect'])
            self.assertIn('이번 턴에 적을 공격하지 않았다면',l['effect'])
            self.assertIn('중 하나를 선택',l['effect'])
            self.assertEqual('추가 행동' in l['effect'],i>=4)
            if i>=4:
                self.assertEqual(l['effect'].count(f'[{(i-3)*10}%]'),2)
        for i,l in enumerate(named('buffs','퓨즈 폭탄')['levels']):
            self.assertIn(f'[{[110,115,125,130][i]}%]',l['effect'])
            self.assertIn('전격',l['effect'])
            self.assertIn('[감전]{orange}',l['effect'])
            self.assertIn('사용 시 해제',l['effect'])
        for i,l in enumerate(named('buffs','테슈브의 낙진')['levels']):
            self.assertIn(f'[{[35,45,50,60][i]}%]',l['effect'])
            self.assertIn(f'[{[65,65,70,70][i]}%]',l['effect'])

    def test_ultimate(self):
        u=read('characters')[0]['ultimate']
        self.assertEqual((u['tpCost'],u['range'],u['cooldown'],u['element']),(5,[2,4],5,'화염'))
        self.assertEqual([l['step'] for l in u['levels']],[0,1,3,5])
        for i,l in enumerate(u['levels']):
            self.assertIn(f'[{[90,100,110,130][i]}%]',l['effect'])
            self.assertIn('[끈끈이 불꽃]{orange}',l['effect'])
        b=named('debuffs','끈끈이 불꽃')
        self.assertEqual(b['duration'],2)
        self.assertEqual(b['tags'],['해제 불가','지속 피해'])
        self.assertIn('[25%]',b['description'])

    def test_classes_and_installations(self):
        classes=read('classes')
        self.assertEqual([c['parent'] for c in classes],['아처','막스맨','메이드새퍼'])
        for c in classes:
            self.assertEqual((c['attackRange'],c['moveRange']),(4,3))
        for c,values in [(classes[0],[3,4]),(classes[2],[6,8])]:
            b=named('buffs',c['passive']['name'])
            self.assertEqual((b['duration'],b['maxStack']),('영구',4))
            for i,l in enumerate(b['levels']):
                self.assertIn(f'[+{values[i]}%]',l['effect'])
                self.assertIn('다른 아군 [1]',c['passive'][f'lv{i+1}'])
        for i,key in enumerate(['lv1','lv2']):
            self.assertIn(f'[{50+i*10}%]',classes[1]['passive'][key])
            self.assertIn(f'[{30+i*10}%]',classes[1]['passive'][key])
            self.assertIn('치명타가 터지지 않습니다',classes[1]['passive'][key])
        for c,cost,ran in zip(classes,[1,3,1],[[1,2],[2,5],[1,4]]):
            s=c['skills'][0]
            self.assertEqual((s['tpCost'],s['range'],s['cooldown']),(cost,ran,3))
        self.assertIn('[2]{yellow}턴',classes[0]['skills'][0]['effect'])
        self.assertEqual(named('buffs','취급 주의 상자')['duration'],'영구')
        self.assertIn('한번 더',classes[2]['skills'][0]['effect'])
        self.assertIn('주변 [1]{red}바퀴',named('buffs','깜짝 깜찍 함정')['description'])
        self.assertIn('남은 스킬 쿨타임이 가장 긴 스킬 하나',named('buffs','잔해')['description'])

    def test_weapon_stats_and_triggers(self):
        w=read('weapons')[0]
        self.assertEqual(w['extraStats'], '공격력 +10/11/12/13/14/15% (각성 1~6단)')
        self.assertEqual([s['maxHp'] for s in w['baseStats']],[120,121,122,124,125,126])
        self.assertEqual([s['attack'] for s in w['baseStats']],[370,373,377,381,384,388])
        for e in w['effects']:
            self.assertEqual([l['step'] for l in e['levels']],[1,2,3,4,5,6])
            for i,l in enumerate(e['levels']):
                self.assertEqual('설치물' in l['effect'],e['type']=='전용')
                self.assertEqual('설치 스킬 시전' in l['effect'],e['type']=='전용')
                if e['type']=='일반':
                    self.assertIn(f'화력 강화 {[1,2,2,3,3,4][i]}',l['effect'])
        for name,durations,stacks in [('폭발적 발상',[2,2,2,2,3,3],[5,6,7,8,9,10]),('화력 강화',[2,2,2,2],[3,4,5,6])]:
            levels=named('buffs',name)['levels']
            self.assertEqual([l['duration'] for l in levels],durations)
            self.assertEqual([l['maxStack'] for l in levels],stacks)
            for l in levels:
                self.assertIn('[+2%]',l['effect'])

    def test_artifact(self):
        a=read('artifacts')[0]
        b=named('debuffs','잿빛 그을림')
        self.assertEqual((b['duration'],b['maxStack']),(2,3))
        for i,l in enumerate(a['levels']):
            self.assertEqual(l['step'],i+3)
            self.assertIn(f'[+{12+i*6}%]',l['effect'])
            self.assertIn(f'[잿빛 그을림 {i+1}]',l['effect'])
            self.assertIn(f'[-{4+i*2}%]',b['levels'][i]['effect'])

if __name__ == '__main__':
    unittest.main()
