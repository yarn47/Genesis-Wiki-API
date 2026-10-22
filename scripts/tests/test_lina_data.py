import json
import re
import unittest
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / 'data'


def read(kind):
    return json.loads((DATA / kind / 'lina.json').read_text())


class LinaTests(unittest.TestCase):
    def test_profile_and_references(self):
        c = read('characters')[0]
        self.assertEqual(c['releaseDate'], '2024-05-28')
        self.assertEqual(c['appearedIn'], '템페스트')
        self.assertEqual((c['faction'], c['element']), ('다갈', '신념의빛'))
        self.assertEqual((c['birthYear'], c['height'], c['cv']), ('에스겔력 1255년', '162cm', '이새아'))
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
            self.assertIn(f'중재하는 손 {i+1}', effect)
            self.assertIn(f"디버프를 [{[1,2,2,3,3,3,3][i]}]", effect)
            self.assertIn(f"치유량이 [{[5,7,8,10,10,10,10][i]}%]", effect)
            self.assertIn(f"[{3 if i < 2 else 4}]{{yellow}}턴 동안", effect)
            self.assertIn('필요한 [TP]{yellow}가 [1]{yellow}만큼 감소', effect)
            self.assertEqual('회복의 서약' in effect, i >= 4)
            self.assertIn('효과를 가진 아군이 없다면', effect)
        hand = read('buffs')[0]['levels']
        for i, l in enumerate(hand):
            self.assertEqual(l['duration'], 3 if i < 2 else 4)
            self.assertIn(f"[{[20,30,40,50,55,60,65][i]}%]", l['effect'])
            self.assertIn('캐릭터 턴 종료 시', l['effect'])
            self.assertIn('디버프를 [1]', l['effect'])
        for i, l in enumerate(read('buffs')[1]['levels']):
            self.assertEqual(l['duration'], 2)
            self.assertIn(f'[{20+5*i}%]', l['effect'])

    def test_ultimate_and_inferred_base(self):
        u = read('characters')[0]['ultimate']
        self.assertEqual((u['tpCost'], u['cooldown'], u['range'], u['element']), (5,5,'자신','광휘'))
        self.assertEqual([l['step'] for l in u['levels']], [0,1,3,5])
        for i, l in enumerate(u['levels']):
            self.assertIn(f'[{100+5*i}%]', l['effect'])
            self.assertIn(f'[{50+5*i}%]', l['effect'])
            self.assertIn('체력이 [50%]{red} 이하', l['effect'])
            self.assertIn('디버프를 [1]', l['effect'])
        base = next(b for b in read('buffs') if b['name'] == '축복의 진언 (기본)')
        self.assertIn('[+7.5%]', base['description'])
        self.assertIn('[-7.5%]', base['description'])
        blessing = next(b for b in read('buffs') if b['name'] == '축복의 진언')
        for i, l in enumerate(blessing['levels']):
            value = [10,12.5,15][i]
            self.assertEqual(l['duration'], 2)
            self.assertIn(f'[+{value}%]', l['effect'])
            self.assertIn(f'[-{value}%]', l['effect'])

    def test_classes(self):
        r, o = read('classes')
        self.assertEqual((r['parent'], o['parent']), ('프리스트', '클레릭'))
        for i, key in enumerate(['lv1', 'lv2']):
            self.assertIn(f'[{30+i*10}%]', r['passive'][key])
            self.assertIn(f'[{70+i*10}%]', r['passive'][key])
            self.assertIn('광휘 계열 스킬을 사용했다면', r['passive'][key])
            self.assertIn(f'[{30+i*10}%]', o['passive'][key])
            self.assertIn('적과 인접해 있는 모든 아군', o['passive'][key])
        self.assertEqual((r['skills'][0]['tpCost'], r['skills'][0]['range'], r['skills'][0]['cooldown']), (2,[1,4],2))
        self.assertEqual((o['skills'][0]['tpCost'], o['skills'][0]['range'], o['skills'][0]['cooldown']), (1,'자신',4))
        trance = next(b for b in read('buffs') if b['name'] == '트랜스')
        self.assertEqual(trance['duration'], 2)
        self.assertIn('해제 불가', trance['tags'])

    def test_weapon(self):
        w = read('weapons')[0]
        self.assertEqual(w['weaponType'], '로드')
        self.assertEqual([s['maxHp'] for s in w['baseStats']], [130,131,132,134,135,136])
        self.assertEqual([s['spellAttack'] for s in w['baseStats']], [342,346,350,354,358,362])
        for e in w['effects']:
            self.assertEqual([l['step'] for l in e['levels']], [1,2,3,4,5,6])
            for l in e['levels']:
                self.assertIn('다른 아군', l['effect'])
                self.assertEqual('자신에게' in l['effect'], e['type'] == '전용')
                self.assertEqual('치유 스킬 사거리' in l['effect'], e['type'] == '전용')
        for name, base in [('신성한 목도',15), ('인도',10)]:
            b = next(b for b in read('buffs') if b['name'] == name)
            for i, l in enumerate(b['levels']):
                self.assertEqual(l['duration'], 2)
                self.assertIn(f'[+{base+i}%]', l['effect'])
                self.assertEqual('공격력/주문력' in l['effect'], name == '신성한 목도' and i >= 4)

    def test_artifact(self):
        a = read('artifacts')[0]
        for i, l in enumerate(a['levels']):
            self.assertEqual(l['step'], i+3)
            self.assertIn(f'[-{8+4*i}%]', l['effect'])
            self.assertIn('[1]{yellow}턴', l['effect'])
            self.assertIn('[2]{red}칸', l['effect'])
            self.assertIn('[집중]{green}', l['effect'])


if __name__ == '__main__':
    unittest.main()
