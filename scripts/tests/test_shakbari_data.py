import json
import unittest
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / 'data'

def read(kind):
    return json.loads((DATA / kind / 'shakbari.json').read_text())

class ShakbariDataTest(unittest.TestCase):
    def test_identity(self):
        c = read('characters')[0]
        self.assertEqual((c['name'], c['releaseDate'], c['appearedIn']), ('전쟁의 샤크바리', '2025-05-13', '창세기전2'))
        self.assertEqual((c['grade'], c['faction'], c['element']), ('전설', '주신', '자유의불꽃'))
        self.assertNotIn('stats', c)

    def test_passive(self):
        ls = read('characters')[0]['passive']['levels']
        self.assertEqual([(x['type'], x['step']) for x in ls], [('각성',3),('각성',4),('각성',5),('각성',6),('발현',2),('발현',4),('발현',6)])
        for i, x in enumerate(ls):
            self.assertIn(f'[전투열기 {i+1}]{{green}}', x['effect'])
            self.assertIn('스킬 사용 전/공격 전/공격 받기 전/버프 획득 후', x['effect'])
            self.assertIn(f'[{[3,3,2,1,1,1,1][i]}]{{yellow}}턴 마다', x['effect'])
            self.assertEqual('[집중]{green}' in x['effect'], i >= 4)
        self.assertIn('[3]{yellow}중첩', ls[-1]['effect'])

    def test_ultimate(self):
        u=read('characters')[0]['ultimate']
        self.assertEqual((u['tpCost'],u['range'],u['cooldown'],u['attackType'],u['element']), (5,'자신',5,'마법','전격'))
        for x, step, damage in zip(u['levels'],[0,1,3,5],[120,130,140,150]):
            self.assertEqual(x['step'],step)
            self.assertIn(f'[{damage}%]{{red}}',x['effect'])
            self.assertIn('[감전]{orange}',x['effect'])

    def test_buffs(self):
        b={x['name']:x for x in read('buffs')}
        self.assertEqual(b['전투열기']['maxStack'],8)
        self.assertNotIn('전쟁의 권능',b['전투열기']['levels'][1]['effect'])
        self.assertIn('전쟁의 권능',b['전투열기']['levels'][2]['effect'])
        self.assertEqual(b['아머드 슈트']['levels'][-1]['maxStack'],3)
        self.assertNotIn('이동력',b['볼텍스 러쉬']['levels'][1]['effect'])
        self.assertIn('이동력',b['볼텍스 러쉬']['levels'][2]['effect'])

    def test_classes(self):
        classes={x['name']:x for x in read('classes')}
        self.assertEqual({n:x['parent'] for n,x in classes.items()}, {'워본':'파이터','슬래셔':'글라디에이터','도미네이터':'글라디에이터','언브로큰':'워본'})
        self.assertIn('네번 공격',classes['슬래셔']['skills'][0]['effect'])
        self.assertEqual(classes['언브로큰']['skills'][0]['cooldown'],2)
        self.assertIn('[30/50/80%]{red}',classes['도미네이터']['passive']['lv2'])

    def test_weapon(self):
        w=read('weapons')[0]
        e,n=w['effects']
        self.assertEqual(w['baseStats'][-1],{'step':6,'maxHp':128,'attack':382})
        for i in range(6):
            self.assertIn(f'[{[30,30,35,35,40,50][i]}%]{{red}}',e['levels'][i]['effect'])
            self.assertIn(f'[{50+i*10}%]{{red}} 확률',n['levels'][i]['effect'])
            self.assertIn(f'[{[30,30,35,35,35,40][i]}%]{{red}}만큼',n['levels'][i]['effect'])

if __name__ == '__main__': unittest.main()
