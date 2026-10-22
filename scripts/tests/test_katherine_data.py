import json
import re
import unittest
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / 'data'

def read(kind):
    return json.loads((DATA / kind / 'katherine.json').read_text())

class KatherineTests(unittest.TestCase):
    def test_profile_and_references(self):
        c = read('characters')[0]
        self.assertEqual((c['releaseDate'], c['appearedIn']), ('2024-07-09', '템페스트'))
        self.assertEqual((c['faction'], c['element'], c['cv']), ('팬드래건', '지성의결정체', '김율'))
        self.assertEqual(c['height'], '182cm')
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

    def test_passive_progression(self):
        levels = read('characters')[0]['passive']['levels']
        self.assertEqual([(l['type'], l['step']) for l in levels], [('각성', s) for s in [3,4,5,6]] + [('발현', s) for s in [2,4,6]])
        for i, l in enumerate(levels):
            effect = l['effect']
            self.assertIn('[50%]', effect)
            self.assertIn(f'[{[5,7,8,10,15,20,25][i]}%]', effect)
            self.assertIn(f'[극기 투혼 {i+1}]', effect)
            self.assertIn('최대 중첩 상태라면 턴 당 한번', effect)
            self.assertEqual('주변 [1]{red}바퀴' in effect, i >= 4)
            self.assertEqual('쿨타임' in effect, i >= 2)
            self.assertEqual('디버프' in effect, i >= 5)
            self.assertEqual('턴 시작 시' in effect, i == 6)

    def test_buff_progression(self):
        b = read('buffs')[0]
        self.assertEqual((b['maxStack'], b['tags']), (3, ['해제 불가']))
        self.assertEqual([l['duration'] for l in b['levels']], [2,3,3,4,'영구','영구','영구'])
        for i, l in enumerate(b['levels']):
            self.assertIn(f'[+{[2,3,4,5,6,8,10][i]}%]', l['effect'])
            self.assertEqual('방어력' in l['effect'], i >= 4)
            self.assertIn('[2]{yellow}턴 동안 [약점 노출]', l['effect'])

    def test_ultimate(self):
        u = read('characters')[0]['ultimate']
        self.assertEqual((u['tpCost'], u['range'], u['cooldown'], u['attackType']), (5,[1,1],5,'참격'))
        self.assertEqual([l['step'] for l in u['levels']], [0,1,3,5])
        for i, l in enumerate(u['levels']):
            self.assertIn(f'[{80+i*10}%]', l['effect'])
            self.assertIn(f'남은 체력의 [{[50,50,55,60][i]}%]', l['effect'])
            self.assertIn('전방 [5]{red}칸', l['effect'])
            self.assertIn('속성: 화염, 빙한.', l['effect'])
            self.assertIn('[냉기 둔화]', l['effect'])
            self.assertIn('[화상]', l['effect'])

    def test_classes(self):
        a, d = read('classes')
        self.assertEqual((a['parent'], d['parent']), ('파이터', '아이언메이든'))
        for c in [a,d]:
            self.assertEqual((c['weaponType'],c['defenseType'],c['moveRange']), ('대검','헤비',3))
            for key in ['lv1','lv2']:
                self.assertIn('[엄폐]', c['passive'][key])
                self.assertIn('[통제 영역]', c['passive'][key])
        for key, v in [('lv1',10),('lv2',15)]:
            self.assertIn(f'적 수 * [{v}%]', a['passive'][key])
            self.assertIn('방어력의 [15%]', a['passive'][key])
        for key,v in [('lv1',20),('lv2',30)]:
            self.assertIn(f'방어력/저항력 [{v}%]', d['passive'][key])
            self.assertIn(f'받는 피해 [{v-10}%]', d['passive'][key])
        self.assertIn('추가 행동', a['skills'][0]['effect'])
        self.assertNotIn('tpCost', a['skills'][0])
        self.assertEqual(d['skills'][0]['tpCost'], 3)
        self.assertIn('지정한 빈 타일', d['skills'][0]['effect'])
        self.assertIn('방어력의 [50%]', read('buffs')[1]['description'])

    def test_weapon(self):
        w = read('weapons')[0]
        self.assertEqual([s['maxHp'] for s in w['baseStats']], [122,123,124,126,127,128])
        self.assertEqual([s['attack'] for s in w['baseStats']], [364,367,371,375,378,382])
        for e in w['effects']:
            self.assertEqual([l['step'] for l in e['levels']], list(range(1,7)))
            for i,l in enumerate(e['levels']):
                self.assertIn('반격 후', l['effect'])
                self.assertIn(f'공격력의 [{10+i*(2 if e["type"]=="전용" else 1)}%]', l['effect'])
                if e['type'] == '전용':
                    self.assertIn(f'방어력의 [{20+2*i}%]', l['effect'])
                    self.assertIn(f'쿨타임 [{4 if i<4 else 3}]', l['effect'])
                    self.assertIn('[2]{yellow}턴 동안', l['effect'])
                    self.assertNotIn('이하', l['effect'])

    def test_artifact(self):
        a = read('artifacts')[0]
        b = read('buffs')[2]
        self.assertEqual((b['duration'], b['maxStack']), (2,4))
        self.assertEqual([l['step'] for l in a['levels']], [3,4,5,6])
        for i,l in enumerate(a['levels']):
            self.assertIn('근접 스킬 사용 후', l['effect'])
            self.assertIn(f'[{3 if i<2 else 2}]{{yellow}}턴에 한번', l['effect'])
            self.assertIn(f'[투지 {i+1}]', l['effect'])
            self.assertIn(f'[+{[5,6,8,10][i]}%]', b['levels'][i]['effect'])

if __name__ == '__main__':
    unittest.main()
