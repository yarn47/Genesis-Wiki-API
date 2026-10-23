import json
import re
import unittest
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / 'data'

def read(kind):
    return json.loads((DATA / kind / 'roberto.json').read_text())

def all_items(kind):
    return [x for p in (DATA / kind).glob('*.json') for x in json.loads(p.read_text())]

class RobertoTests(unittest.TestCase):
    def test_profile_and_links(self):
        c = read('characters')[0]
        self.assertEqual((c['releaseDate'], c['appearedIn']), ('2024-08-06', '서풍의 광시곡'))
        self.assertEqual((c['faction'], c['subFaction'], c['element']), ('게이시르', '제피르팰컨', '지성의결정체'))
        self.assertNotIn('stats', c)
        for kind, names in [('classes',c['classTree']), ('weapons',[c['exclusiveWeapon']]), ('artifacts',c['artifacts'])]:
            available = [x['name'] for x in all_items(kind)]
            for name in names: self.assertEqual(available.count(name), 1)
        available = set()
        for b in all_items('buffs') + all_items('debuffs'):
            available.add(b['name'])
            available.update(l.get('name', f'{b["name"]} {l["level"]}') for l in b.get('levels', []))
        for kind in ['characters', 'classes', 'buffs', 'weapons', 'artifacts']:
            for name in re.findall(r'\[([^\[\]]+)\]\{(?:green|orange)\}', json.dumps(read(kind), ensure_ascii=False)):
                self.assertIn(name, available)

    def test_passive(self):
        p = read('characters')[0]['passive']['levels']
        self.assertEqual([(x['type'], x['step']) for x in p], [('각성',s) for s in [3,4,5,6]] + [('발현',s) for s in [2,4,6]])
        for i, l in enumerate(p):
            self.assertIn(f'[혁명의 전주곡 {i+1}]', l['effect'])
            self.assertIn(f'쿨타임 : [{3 if i<2 else 2}]', l['effect'])
            self.assertIn('남은 TP가 [0]', l['effect'])
            self.assertEqual('비상하는 매' in l['effect'], i>=4)
        b = {x['name']:x for x in read('buffs')}
        for i, l in enumerate(b['혁명의 전주곡']['levels']):
            self.assertEqual((l['duration'], l['maxStack']), (2,6))
            self.assertIn(f'[+{[2,3,4,5,6,8,10][i]}%]', l['effect'])
        self.assertEqual((b['저항군의 심장']['duration'], b['저항군의 심장']['maxStack']), ('영구',4))
        self.assertNotIn('levels', b['저항군의 심장'])
        for i,l in enumerate(b['비상하는 매']['levels']):
            self.assertEqual(l['duration'], '영구')
            self.assertEqual('기본 공격 사거리' in l['effect'], i>0)

    def test_classes(self):
        c = {x['name']:x for x in read('classes')}
        self.assertEqual(len(c), 3)
        self.assertEqual(c['레지스탕스']['parent'], '파이터')
        self.assertEqual(c['스톰나이트']['parent'], '나이트')
        self.assertEqual(c['레지스트커맨더']['parent'], '레지스탕스')
        self.assertEqual(c['레지스탕스']['moveRange'], 4)
        self.assertIn('항상 [1%]', c['레지스탕스']['skills'][0]['effect'])
        self.assertIn('[1]{yellow}턴 동안 [감전]', c['스톰나이트']['skills'][0]['effect'])
        self.assertEqual(c['스톰나이트']['skills'][0]['element'], '전격')
        for key in ['lv1','lv2']:
            self.assertIn('턴 당 한번', c['레지스트커맨더']['passive'][key])
            self.assertIn('턴 시작 시', c['레지스트커맨더']['passive'][key])
            self.assertIn('최대 [15%]', c['스톰나이트']['passive'][key])

    def test_artifacts(self):
        a = read('artifacts')
        for x in a: self.assertEqual([l['step'] for l in x['levels']], [3,4,5,6])
        for i,l in enumerate(a[0]['levels']):
            self.assertIn(f'쿨타임이 [{1 if i<2 else 2}]', l['effect'])
            self.assertIn('잔여 TP가 [2]', l['effect'])
        for l in a[1]['levels']: self.assertIn('인도받는 검 효과와 중복 적용 불가', l['effect'])
        b = {x['name']:x for x in read('buffs')}
        for i,l in enumerate(b['폭풍의 전조']['levels']):
            self.assertEqual(l['duration'], 1)
            self.assertEqual('폭풍의 수호' in l['effect'], i>=2)
            self.assertIn(f'[+{[12,18,24,30][i]}%]', l['effect'])
        for i,l in enumerate(b['전사의 용맹']['levels']):
            self.assertEqual(l['duration'], 2)
            self.assertIn(f'[+{[15,16,18,20][i]}%]', l['effect'])

    def test_weapon(self):
        w = read('weapons')[0]
        self.assertEqual([x['maxHp'] for x in w['baseStats']], [126,127,128,130,131,132])
        self.assertEqual([x['attack'] for x in w['baseStats']], [353,356,360,364,367,371])
        for e in w['effects']:
            self.assertEqual([l['step'] for l in e['levels']], [1,2,3,4,5,6])
            for i,l in enumerate(e['levels']): self.assertIn(f'쿨타임 [{[4,4,3,3,2,2][i]}]', l['effect'])
        for i,l in enumerate(w['effects'][0]['levels']):
            self.assertIn(f'[{50+i*10}%]', l['effect'])
            self.assertIn(f'[선두 진격 {i+1}]', l['effect'])
        buff = next(b for b in read('buffs') if b['name']=='선두 진격')
        for i,l in enumerate(buff['levels']):
            self.assertEqual('이동력' in l['effect'], i>=4)
            self.assertEqual(l['duration'], 2)

    def test_ultimate(self):
        u = read('characters')[0]['ultimate']
        self.assertEqual((u['tpCost'],u['range'],u['cooldown'],u['element']), (5,'자신',5,'화염'))
        self.assertEqual([x['step'] for x in u['levels']], [0,1,3,5])
        for i,l in enumerate(u['levels']):
            self.assertIn(f'[{145+i*5}%]', l['effect'])
            self.assertIn(f'[{55+i*5}%]', l['effect'])
            self.assertIn('방어력을 무시', l['effect'])
        self.assertIn('145%/55%', (DATA/'notes/roberto.md').read_text())
