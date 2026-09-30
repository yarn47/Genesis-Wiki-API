import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
def read(path):
    return json.loads((ROOT/'data'/path).read_text())

class KoonTests(unittest.TestCase):
    def test_profile_and_shared_references(self):
        c=read('characters/koon.json')[0]
        self.assertEqual((c['name'],c['birthYear'],c['height'],c['cv']),('쿤 그리어','에스겔력 1185년','162cm','이다은'))
        self.assertEqual((c['faction'],c['element']),('게이시르','자유의불꽃'))
        self.assertNotIn('ultimate',c)
        self.assertNotIn('stats',c)
        self.assertEqual(c['classTree'],['메이지','매지션','위자드','아크메이지','프로스트메이지','다크위자드'])
        self.assertEqual(c['artifacts'],['치밀한 준비','간이 보호 부적','주문 가속'])
        for key in ['releaseDate','appearedIn']:
            self.assertEqual(c[key],read('characters/beradin.json')[0][key])

    def test_passive_levels_and_distinct_extra_actions(self):
        ls=read('characters/koon.json')[0]['passive']['levels']
        self.assertEqual([(l['type'],l['step']) for l in ls],[('각성',n) for n in [3,4,5,6]]+[('발현',n) for n in [2,4,6]])
        for i,l in enumerate(ls):
            for element in ['화염','빙한','전격']:
                self.assertIn(f'[{element} 강화 {i+1}]',l['effect'])
            self.assertIn(f'[{3 if i<2 else 4}]{{yellow}}턴',l['effect'])
        for l,n,action in zip(ls[4:],[10,20,30],['추가 이동','추가 공격이나 스킬 사용','추가 행동']):
            self.assertIn(f'[{n}%]',l['effect'])
            self.assertIn(action,l['effect'])

    def test_enhancement_values(self):
        b={x['name']:x for x in read('buffs/koon.json')}
        for name,values in [('화염 강화',[15,15,20,20,25,30,40]),('전격 강화',[5,10,10,15,20,30,40])]:
            for l,n in zip(b[name]['levels'],values):
                self.assertIn(f'주문력 [+{n}%]',l['effect'])
        for l,n in zip(b['빙한 강화']['levels'],[25,30,35,40,60,80,100]):
            self.assertIn(f'주문력의 [{n}%]',l['effect'])
        for l,n in zip(b['빙한 강화']['levels'][4:],[10,20,30]):
            self.assertIn(f'받는 피해 [-{n}%]',l['effect'])
            self.assertIn('TP 소모량 [-1]',l['effect'])

    def test_archmage(self):
        c=read('classes/archmage.json')[0]
        self.assertEqual(c['parent'],'매지션')
        for i,n in enumerate([25,30]):
            self.assertIn(f'주문력이 [{n}%]',c['passive'][f'lv{i+1}'])
            self.assertIn('죽지 않았다면 [1 TP]',c['passive'][f'lv{i+1}'])
        s=c['skills'][0]
        self.assertEqual((s['name'],s['tpCost'],s['range'],s['cooldown']),('썬더볼트',3,[1,1],2))
        self.assertIn('저항력을 무시',s['effect'])
        self.assertIn('[70%]',s['effect'])

    def test_weapon_confirmed_assumptions_and_rotation(self):
        w=read('weapons/koon.json')[0]
        self.assertEqual(w['extraStats'],'주문력 +10/11/12/13/14/15% (각성 1~6단)')
        old=read('weapons/beradin.json')[0]['baseStats']
        for actual,expected in zip(w['baseStats'],old):
            self.assertEqual(actual,{k:expected[k] for k in ['step','maxHp','spellAttack']})
            self.assertNotIn('magicPen',actual)
        self.assertTrue(all(len(e['levels'])==6 for e in w['effects']))
        self.assertTrue(all(len({l['effect'] for l in e['levels']})==1 for e in w['effects']))
        b={x['name']:x for x in read('buffs/koon.json')}
        for kind,percent in [('지배',20),('나선',15)]:
            for src,dst in [('화염','빙한'),('빙한','전격'),('전격','화염')]:
                effect=b[f'{src} {kind}']
                self.assertEqual(effect['duration'],1)
                self.assertIn(f'[{dst} {kind}]',effect['description'])
                self.assertIn(f'[{percent}%]',effect['description'])
                self.assertEqual('[집중]' in effect['description'],kind=='지배')

    def test_spell_acceleration(self):
        a=read('artifacts/koon.json')
        self.assertEqual(len(a),1)
        self.assertEqual([l['step'] for l in a[0]['levels']],[3,4,5,6])
        b=next(x for x in read('buffs/koon.json') if x['name']=='주문 가속')
        self.assertEqual(b['maxStack'],3)
        self.assertEqual(b['tags'],['해제 불가'])
        for l,n in zip(b['levels'],[3,7,11,15]):
            self.assertIn(f'[+{n}%]',l['effect'])
            self.assertIn(f'[-{n}%]',l['effect'])
            self.assertIn('모든 일반 스킬의 쿨타임 [1]',l['effect'])

if __name__=='__main__':
    unittest.main()
