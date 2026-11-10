import json
import unittest
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / 'data'

def read(kind):
    return json.loads((DATA / kind / 'albatini.json').read_text())

class AlbatiniDataTest(unittest.TestCase):
    def test_identity(self):
        c = read('characters')[0]
        self.assertEqual((c['name'], c['releaseDate'], c['appearedIn']), ('알바티니 데 메디치', '2025-04-29', '창세기전3'))
        self.assertNotIn('stats', c)

    def test_passive_conditions(self):
        levels = read('characters')[0]['passive']['levels']
        self.assertEqual([(x['type'], x['step']) for x in levels], [('각성',3),('각성',4),('각성',5),('각성',6),('발현',2),('발현',4),('발현',6)])
        for i, x in enumerate(levels):
            self.assertIn('남은 TP가 [0]{yellow}', x['effect'])
            self.assertIn('크리스티나 여제와 무작위 아군 [1]{red}', x['effect'])
            self.assertIn(f'[{40+10*i}%]{{red}}의 체력으로 부활', x['effect'])
            self.assertEqual('모든 디버프를 해제' in x['effect'], i >= 4)
            self.assertIn(f'쿨타임 : [{[4,4,4,3,3,2,2][i]}]{{yellow}}', x['effect'])
        self.assertNotIn('가장 긴 스킬', levels[-2]['effect'])
        self.assertIn('가장 긴 스킬 하나', levels[-1]['effect'])

    def test_ultimate_gap(self):
        u = read('characters')[0]['ultimate']
        self.assertEqual((u['tpCost'],u['range'],u['cooldown']), (5,[1,1],5))
        for x, step, damage in zip(u['levels'],[0,1,3,5],[130,140,150,160]):
            self.assertEqual(x['step'], step)
            self.assertIn(f'[{damage}%]{{red}}만큼 피해', x['effect'])
            self.assertIn('무작위 방향으로 [1]{red}칸', x['effect'])
            self.assertIn('[2]{yellow}턴 동안 적에게 [통제 영역]{orange}', x['effect'])

    def test_buffs(self):
        buffs = {x['name']:x for x in read('buffs')}
        self.assertEqual(buffs['기사의 서약']['maxStack'],5)
        self.assertEqual(buffs['비밀 경호']['duration'],2)
        self.assertIn('[3]{red}칸 이상', buffs['비밀 경호']['description'])
        self.assertEqual(buffs['강력한 권위']['maxStack'],3)
        self.assertIn('체력 [+4%]{red}', buffs['기사의 서약']['levels'][-1]['effect'])

    def test_classes(self):
        j,e = read('classes')
        self.assertEqual((j['parent'], e['parent']), ('파이터','저스티카'))
        skill=j['skills'][0]
        self.assertNotIn('tpCost',skill)
        self.assertIn('항상 [1%]{red}',skill['effect'])
        self.assertIn('TP를 모두 소모',skill['effect'])
        self.assertEqual(e['skills'][0]['range'],'자신')
        self.assertIn('스톰나이트',read('characters')[0]['classTree'])

    def test_artifact_penalty(self):
        a=read('artifacts')[0]
        self.assertEqual([x['step'] for x in a['levels']],[3,4,5,6])
        for x in a['levels']:
            self.assertIn('받는 피해가 [15%]{red} 증가',x['effect'])
            self.assertIn('두배의 피해',x['effect'])
        self.assertNotIn('체력',a['levels'][0]['effect'])
        self.assertIn('[+30%]{red}',a['levels'][-1]['effect'])

    def test_weapon_noncrit_trigger(self):
        w=read('weapons')[0]
        exclusive,normal=w['effects']
        for i,(e,n) in enumerate(zip(exclusive['levels'],normal['levels'])):
            self.assertIn('치명타가 발생하지 않았다면',e['effect'])
            self.assertIn(f'[{15+i*5}%]{{red}}',e['effect'])
            self.assertNotIn('비정한 학살',n['effect'])
            self.assertNotIn('치명타',n['effect'])
            if i<5: self.assertIn(f'[{25+i*15}%]{{red}} 확률로',e['effect'])
            else: self.assertNotIn('확률로',e['effect'])
        self.assertEqual(w['baseStats'][-1],{'step':6,'maxHp':128,'attack':382})

if __name__ == '__main__': unittest.main()
