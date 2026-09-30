import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('gen_sql', ROOT/'scripts/gen_sql.py')
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

def read(path):
    return json.loads((ROOT/'data'/path).read_text())

class DurantTests(unittest.TestCase):
    """Expectations from supplied screenshots 6385–6483, including 6477 correction."""
    def test_profile_and_no_ultimate(self):
        c = read('characters/durant.json')[0]
        self.assertEqual((c['name'],c['birthYear'],c['height'],c['cv']), ('듀란 렘브란트','에스겔력 1165년','187cm','김영찬'))
        self.assertEqual((c['grade'],c['faction'],c['element']), ('전설','팬드래건','신념의빛'))
        self.assertNotIn('ultimate',c)
        self.assertNotIn('stats',c)
        self.assertTrue(c['hasManifestation'])
        self.assertNotIn('INSERT INTO ultimate_skills',gen.character_sql(c))
        self.assertIn('INSERT INTO character_manifestation',gen.character_sql(c))
        previous = read('characters/beradin.json')[0]
        for key in ['releaseDate','appearedIn']:
            self.assertEqual(c[key],previous[key])

    def test_passive_awaken_thresholds_and_recovery(self):
        levels = read('characters/durant.json')[0]['passive']['levels']
        self.assertEqual([(l['type'],l['step']) for l in levels], [('각성',n) for n in [3,4,5,6]]+[('발현',n) for n in [2,4,6]])
        for l,threshold,buff,heal in zip(levels[:4],[50,60,60,70],[10,15,20,25],[10,10,15,15]):
            self.assertIn(f'체력이 [{threshold}%]{{red}} 이하',l['effect'])
            self.assertIn(f'저항력을 [{buff}%]{{red}} 증가',l['effect'])
            self.assertIn(f'최대 체력의 [{heal}%]{{red}}',l['effect'])
            self.assertIn('인접한 아군들을 [호위]{green}',l['effect'])

    def test_manifest_four_complete_and_six_range(self):
        levels = read('characters/durant.json')[0]['passive']['levels'][4:]
        for l,heal,reduction in zip(levels,[20,20,25],[5,10,10]):
            self.assertIn('방어력/저항력이 [30%]{red}',l['effect'])
            self.assertIn('체력이 [80%]{red} 이하',l['effect'])
            self.assertIn(f'최대 체력의 [{heal}%]{{red}}',l['effect'])
            self.assertIn(f'받는 피해가 [{reduction}%]{{red}} 감소',l['effect'])
        self.assertIn('[2]{red}칸 이내 아군들을 [호위]{green}',levels[2]['effect'])
        self.assertIn('인접한 아군들을 [호위]{green}',levels[1]['effect'])

    def test_durant_tree_not_donor_character_tree(self):
        classes = read('classes/defender_line.json')
        self.assertEqual(read('characters/durant.json')[0]['classTree'],[c['name'] for c in classes])
        self.assertEqual({c['name']:c.get('parent') for c in classes}, {'디펜더':None,'아머나이트':'디펜더','팔라딘':'디펜더','포트리스':'아머나이트','센츄리온':'아머나이트','크루세이더':'팔라딘'})
        self.assertEqual(sum(len(c['skills']) for c in classes),8)
        self.assertTrue(all((c['attackRange'],c['moveRange'],c['defenseType'])==(1,3,'헤비') for c in classes))

    def test_skill_edge_conditions(self):
        skills={s['name']:s for c in read('classes/defender_line.json') for s in c['skills']}
        self.assertEqual(skills['이충공파']['range'],[3,3])
        self.assertEqual(skills['공파진섬']['cooldown'],1)
        self.assertIn('추가 피해를 가하지 않았다면 TP를 [1]{yellow}',skills['진격섬']['effect'])
        self.assertIn('설치물에게는 [3]{red}의 피해',skills['허공열파']['effect'])
        self.assertIn('공격력 또는 주문력 중 높은 수치',skills['썬 라이트']['effect'])
        self.assertEqual(skills['썬 라이트']['element'],'광휘')

    def test_second_wind_and_shared_artifacts(self):
        c=read('characters/durant.json')[0]
        self.assertEqual(c['artifacts'],['섬광연격 비전서','재기의 바람','최상의 상태'])
        a=read('artifacts/durant.json')
        self.assertEqual(len(a),1)
        self.assertEqual([l['step'] for l in a[0]['levels']],[3,4,5,6])
        for l,n in zip(a[0]['levels'],[10,15,20,25]):
            self.assertIn(f'[+{n}%]{{red}}',l['effect'])
        buff=next(b for b in read('buffs/defender_line.json') if b['name']=='재기의 바람')
        for l,reduction,heal in zip(buff['levels'],[8,12,16,20],[35,40,45,50]):
            self.assertEqual((l['duration'],l['maxStack']),(2,2))
            self.assertIn(f'[-{reduction}%]{{red}}',l['effect'])
            self.assertIn(f'[{heal}%]{{red}}',l['effect'])
            self.assertIn('방어력 또는 공격력 중 높은 수치',l['effect'])

    def test_last_bastion_stats_and_counter_limits(self):
        w=read('weapons/durant.json')[0]
        self.assertEqual([s['maxHp'] for s in w['baseStats']],[139,140,141,143,144,145])
        self.assertEqual([s['attack'] for s in w['baseStats']],[321,324,328,332,335,339])
        self.assertEqual([s['defense'] for s in w['baseStats']],[28,28,28,28,29,29])
        for e,values,chance,heal in zip(w['effects'],[[50,60,65,70,75,80],[25,30,35,40,45,50]],[20,10],[50,30]):
            for l,limit,bonus in zip(e['levels'],[1,1,2,2,3,3],values):
                self.assertIn(f'턴 당 [{limit}]{{yellow}}번 반격',l['effect'])
                self.assertIn(f'방어력의 [{bonus}%]{{red}}만큼 공격력',l['effect'])
                self.assertIn(f'반격 후 [{chance}%]{{red}}의 확률',l['effect'])
                self.assertIn(f'방어력의 [{heal}%]{{red}}만큼 체력',l['effect'])
                self.assertIn('호위에도 적용',l['effect'])

if __name__=='__main__':
    unittest.main()
