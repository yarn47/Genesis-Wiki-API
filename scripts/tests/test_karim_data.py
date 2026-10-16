import json
import re
from pathlib import Path
import unittest

DATA = Path(__file__).resolve().parents[2] / 'data'
def read(kind):
    return json.loads((DATA / kind / 'karim_nidia.json').read_text())

class KarimTests(unittest.TestCase):
    def test_profile_and_references(self):
        c = read('characters')[0]
        self.assertEqual((c['releaseDate'], c['appearedIn']), ('2024-04-16', '창세기전2'))
        self.assertEqual((c['faction'], c['element']), ('사이럽스', '활력의나무'))
        self.assertNotIn('stats', c)
        for kind, names in [('classes', c['classTree']), ('artifacts', c['artifacts']), ('weapons', [c['exclusiveWeapon']])]:
            existing = [x['name'] for p in (DATA / kind).glob('*.json') for x in json.loads(p.read_text())]
            for name in names:
                self.assertEqual(existing.count(name), 1)

    def test_passive_progression(self):
        levels = read('characters')[0]['passive']['levels']
        self.assertEqual([(x['type'],x['step']) for x in levels], [('각성',s) for s in [3,4,5,6]] + [('발현',s) for s in [2,4,6]])
        for i,l in enumerate(levels):
            text = l['effect']
            self.assertIn('[3]{red}배' if i < 2 else '[4]{red}배', text)
            self.assertEqual('더블캐스트' in text, i >= 2)
            self.assertIn('코인이 [10]', text)
            self.assertIn('모든 코인을 소모', text)
            if i >= 4: self.assertIn(f'[{[10,15,20][i-4]}%]', text)
        buffs = {x['name']:x for x in read('buffs')}
        self.assertEqual(buffs['코인 버스트']['maxStack'],50)
        self.assertEqual(buffs['에테르 배리어']['duration'],2)
        self.assertNotIn('아케인',buffs)  # Preserve Vishnu's existing shared effect.

    def test_ultimate_and_classes(self):
        c = read('characters')[0]
        u = c['ultimate']
        self.assertEqual((u['tpCost'],u['range'],u['cooldown']),(5,'자신',5))
        for l in u['levels']:
            self.assertEqual('추가로 공격하거나 스킬' in l['effect'], l['step'] > 0)
        b = next(x for x in read('buffs') if x['name']=='엘드 엠파이어')
        for l,n in zip(b['levels'],[100,110,120,140]): self.assertIn(f'[{n}%]',l['effect'])
        spark,storm = read('classes')
        self.assertEqual((spark['parent'],storm['parent']),('메이지','스파크메이지'))
        self.assertEqual(storm['skills'][0]['tpCost'],3)
        slow = next(x for x in read('debuffs') if x['name'].startswith('느려짐'))
        self.assertEqual(slow['duration'],2)

    def test_artifacts_and_weapon(self):
        heart,wall = read('artifacts')
        self.assertEqual([x['step'] for x in heart['levels']],[3,4,5,6])
        for l,n in zip(wall['levels'],[15,20,25,30]): self.assertIn(f'[{n}%]',l['effect'])
        w = read('weapons')[0]
        self.assertEqual([x['maxHp'] for x in w['baseStats']],[116,117,118,120,121,122])
        self.assertEqual([x['spellAttack'] for x in w['baseStats']],[381,384,388,392,395,399])
        for i,l in enumerate(w['effects'][0]['levels']):
            self.assertIn(f'코인을 [{1 if i<4 else 2}]',l['effect'])
            if i<5: self.assertIn(f'[{75+5*i}%]',l['effect'])
            else: self.assertNotIn('확률',l['effect'])

    def test_all_effect_links_resolve(self):
        names = set()
        for kind in ['buffs','debuffs']:
            for p in (DATA / kind).glob('*.json'):
                for b in json.loads(p.read_text()):
                    names.add(b['name'])
                    for l in b.get('levels',[]): names.add(l.get('name',f"{b['name']} {l['level']}"))
        for kind in ['characters','classes','buffs','debuffs','weapons','artifacts']:
            for name in re.findall(r'\[([^\[\]]+)\]\{(?:green|orange)\}',json.dumps(read(kind),ensure_ascii=False)):
                self.assertIn(name,names)

if __name__=='__main__': unittest.main()
