import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('gen', ROOT / 'scripts/gen_sql.py')
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

def read(path):
    return json.loads((ROOT / 'data' / path).read_text())

class GishneAlcionTests(unittest.TestCase):
    def test_profiles_and_reuse(self):
        g, a = [read(f'characters/{n}.json')[0] for n in ['gishne', 'alcion']]
        self.assertEqual((g['name'], g['faction'], g['element']), ('기쉬네 드리포드', '게이시르', '지성의결정체'))
        self.assertEqual((a['name'], a['faction'], a['element']), ('알시온 블랙소드', '카슈미르', '자유의불꽃'))
        self.assertNotIn('ultimate', g)
        for c in [g, a]:
            for unknown in ['stats', 'releaseDate', 'appearedIn']:
                self.assertNotIn(unknown, c)
            self.assertEqual(len(c['classTree']), 6)
            self.assertEqual([(l['type'], l['step']) for l in c['passive']['levels']],
                             [('각성', n) for n in [3, 4, 5, 6]] + [('발현', n) for n in [2, 4, 6]])
        fighter_names = {c['name'] for c in read('classes/fighter_line.json')}
        self.assertTrue(set(a['classTree']) <= fighter_names)
        self.assertEqual(a['artifacts'], ['협공 연계', '속성 과부하', '전사의 정수'])
        self.assertEqual(g['artifacts'], ['간이 보호 부적', '깜빡이는 보주', '주문 가속'])

    def test_shared_skills_use_original_ids(self):
        classes = gen.load_classes({t['name'] for t in read('tags.json')})
        warlock = next(c for c in classes if c['name'] == '워록')
        self.assertEqual(warlock['skillsFrom'], '위치')
        self.assertNotIn('skills', warlock)
        sql = gen.shared_class_skills_sql(warlock)
        self.assertIn('SELECT @target_class, skill_id, unlock_order FROM class_skills', sql)
        self.assertNotIn('INSERT INTO skills ', sql)
        self.assertIn("name = '위치'", sql)
        self.assertNotIn('INSERT INTO skills ', gen.class_sql(warlock))
        self.assertEqual(next(c for c in classes if c['name'] == '다크메이지')['parent'], '위치')

    def test_invalid_skill_references_rejected(self):
        for source in ['없는 클래스', '워록']:
            with self.subTest(source=source), patch.object(gen, 'load_folder', return_value=[('test.json', dict(name='워록', tier=1, skillsFrom=source))]):
                with self.assertRaises(gen.DataError): gen.load_classes(set())
        original = dict(name='위치', tier=1, skills=[dict(name='스킬')])
        alias = dict(name='워록', tier=1, skillsFrom='위치', skills=[dict(name='복제')])
        with patch.object(gen, 'load_folder', return_value=[('t.json', original), ('t.json', alias)]):
            with self.assertRaises(gen.DataError): gen.load_classes(set())

    def test_gishne_passive_and_time_control(self):
        levels = read('characters/gishne.json')[0]['passive']['levels']
        for l, spell, tp in zip(levels[:4], [15,20,20,30], [1,1,2,2]):
            self.assertIn(f'[{spell}%]', l['effect'])
            self.assertIn(f'TP를 [{tp}]', l['effect'])
        for l, spell, hp, shield in zip(levels[4:], [30,35,40], [10,15,20], [40,50,60]):
            for value in [spell,hp,shield]: self.assertIn(f'[{value}%]', l['effect'])
            self.assertNotIn('범위 스킬로 적 공격 시', l['effect'])
        self.assertNotIn('추가 행동', levels[4]['effect'])
        self.assertIn('쿨타임: [3]', levels[5]['effect'])
        self.assertIn('쿨타임: [2]', levels[6]['effect'])
        buffs = {b['name']: b for b in read('buffs/gishne.json')}
        self.assertEqual([l['maxStack'] for l in buffs['시간 조작']['levels']], [20,19,18,17,16,15])
        for l in buffs['시간 조작']['levels']:
            self.assertIn('액티브 스킬 하나씩', l['effect'])
            self.assertIn('쿨타임을 [1]', l['effect'])
        self.assertEqual(read('debuffs/gishne.json')[0]['duration'], 2)

    def test_alcion_passive_ultimate_and_artifact(self):
        c = read('characters/alcion.json')[0]
        for l, damage, chance in zip(c['passive']['levels'][:4], [25,35,40,50], [50,70,80,100]):
            self.assertIn(f'공격력의 [{damage}%]', l['effect'])
            self.assertEqual('확률로' in l['effect'], chance != 100)
            self.assertEqual('TP 소모량' in l['effect'], damage >= 40)
        u = c['ultimate']
        self.assertEqual((u['name'],u['tpCost'],u['range'],u['cooldown']), ('부동명왕검',5,[1,1],5))
        self.assertEqual([l['step'] for l in u['levels']], [0,1,3,5])
        for l, damage in zip(u['levels'], [230,240,250,260]):
            self.assertIn(f'[{damage}%]', l['effect'])
            self.assertIn('[99%]', l['effect'])
            self.assertIn('반격당하지 않고 호위할 수 없습니다', l['effect'])
        for l, damage in zip(read('artifacts/alcion.json')[0]['levels'], [40,60,80,100]):
            self.assertEqual(l['effect'], f'협공 피해량 [+{damage}%]{{red}}.')
        b = {b['name']: b for b in read('buffs/alcion.json')}
        self.assertEqual((b['부동명왕검']['duration'],b['부동명왕검']['maxStack']), ('영구',4))
        self.assertEqual((b['난투의 제왕']['duration'],b['난투의 제왕']['maxStack']), (1,3))

    def test_weapons_six_steps(self):
        for name, hp, stat, values in [('gishne',[116,117,118,120,121,122],'spellAttack',[381,384,388,392,395,399]),
                                      ('alcion',[122,123,124,126,127,128],'attack',[364,367,371,375,378,382])]:
            w = read(f'weapons/{name}.json')[0]
            self.assertEqual([s['maxHp'] for s in w['baseStats']],hp)
            self.assertEqual([s[stat] for s in w['baseStats']],values)
            for e in w['effects']: self.assertEqual([l['step'] for l in e['levels']],list(range(1,7)))
        w = read('weapons/alcion.json')[0]
        for l, damage, cd in zip(w['effects'][0]['levels'], [15,17,19,21,23,25], [1,1,2,2,3,3]):
            self.assertIn(f'[{damage}%]',l['effect'])
            self.assertIn(f'쿨타임이 [{cd}]',l['effect'])

if __name__ == '__main__':
    unittest.main()
