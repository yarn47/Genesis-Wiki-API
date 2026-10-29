import copy
import importlib.util
import json
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('black_prince_gen_sql', ROOT / 'scripts/gen_sql.py')
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

def load(kind, file='black_prince'):
    return json.loads((ROOT / 'data' / kind / (file + '.json')).read_text())

class BlackPrinceDataTests(unittest.TestCase):
    def test_identity(self):
        c = load('characters')[0]
        self.assertEqual((c['releaseDate'], c['appearedIn'], c['grade']), ('2025-01-14', '창세기전2', '아우터원'))
        self.assertNotIn('stats', c)
        self.assertEqual(len(c['classTree']), 6)

    def test_independent_skills_and_outer_unlock_at_manifest_one(self):
        c = load('characters')[0]
        self.assertEqual([x['step'] for x in c['ultimate']['levels']], [0,1,3,5])
        self.assertEqual([x['step'] for x in c['outerSkill']['levels']], [1,3,5])
        for x, n in zip(c['ultimate']['levels'], [185,190,195,200]):
            self.assertIn(f'[{n}%]', x['effect'])
        self.assertIn('역산', c['ultimate']['levels'][0]['effect'])
        self.assertEqual(c['outerSkill']['cooldown'], 3)
        self.assertNotIn('tpCost', c['outerSkill'])

    def test_passive_and_weapon_breakpoints(self):
        self.assertEqual(len(load('characters')[0]['passive']['levels']), 7)
        buffs = {x['name']:x for x in load('buffs')}
        for i, lvl in enumerate(buffs['극한의 무']['levels']):
            self.assertEqual('선제 공격' in lvl['effect'], i >= 2)
            self.assertEqual('반격 사거리' in lvl['effect'], i >= 3)
            self.assertEqual('이중 방어' in lvl['effect'], i >= 5)
        self.assertEqual(buffs['영자 축적']['maxStack'], 4)
        self.assertIn('[50%]', buffs['검은 불꽃']['levels'][4]['effect'])
        self.assertNotIn('[50%]', buffs['검은 불꽃']['levels'][5]['effect'])
        w=load('weapons','asura')[0]
        self.assertEqual([x['critRate'] for x in w['baseStats']], [10,12,14,16,18,20])
        self.assertEqual([x['attack'] for x in w['baseStats']], [364,367,371,375,378,382])

    def test_dawn_exists_only_at_four_stars(self):
        self.assertEqual([x['step'] for x in load('artifacts')[0]['levels']], [6])

    def test_ammyung_summon_kill_refund(self):
        cls = next(x for x in load('classes') if x['name'] == '검황')
        skill = next(x for x in cls['skills'] if x['name'] == '암명연살검')
        self.assertEqual((skill['tpCost'], skill['cooldown']), (2, 3))
        self.assertIn('[한계확장]{green} 효과를 획득합니다.', skill['effect'])
        self.assertIn('이 스킬로 처치한 적이 소환수라면 TP를 [2]{yellow}만큼 회복하고 쿨타임이 [3]{yellow}만큼 감소합니다.', skill['effect'])

    def test_atomic_blast_mixed_attack_type_overrides_class(self):
        cls=next(x for x in load('classes') if x['name']=='데스로드')
        skill=cls['skills'][0]
        self.assertEqual(cls['attackType'], '참격')
        self.assertEqual(skill['attackType'], '물리/마법')
        self.assertIn(skill['attackType'], gen.ATTACK_TYPES)
        self.assertIn('물리 고정 피해', skill['effect'])
        self.assertIn("attack_type = '물리/마법'", gen.skill_sql(skill, 1))

    def test_sql_owns_separate_rows_and_is_repeatable(self):
        c=load('characters')[0]
        sql=gen.character_sql(c)
        self.assertIn('SELECT outer_skill_id FROM characters WHERE character_id = @id', sql)
        self.assertIn('SET @outer = COALESCE(@outer, LAST_INSERT_ID())', sql)
        self.assertIn('DELETE FROM ultimate_skill_levels WHERE ultimate_id = @outer', sql)
        self.assertIn('UPDATE characters SET outer_skill_id = @outer', sql)
        self.assertIn('(@ult, 0, 5, 0, 0, 5,', sql)
        self.assertIn('(@outer, 1, NULL, 1, 3, 3,', sql)
        self.assertNotIn('(@outer, 0,', sql)
        self.assertIn('(@id, 3, @ult, NULL,', sql)

    def test_outer_validation(self):
        c=copy.deepcopy(load('characters')[0])
        c['grade']='전설'
        with patch.object(gen, 'load_folder', return_value=[('test.json',c)]):
            with self.assertRaisesRegex(gen.DataError, '아우터원'):
                gen.load_characters(set(c['classTree']), {c['exclusiveWeapon']}, set(c['artifacts']), set(gen.load_tags()[1]))

    def test_all_new_image_links_exist(self):
        frontend=ROOT.parent/'The-War-Of-Genesis-Mobile-Wiki/public'
        def scan(value):
            if isinstance(value,dict):
                for k,v in value.items():
                    if k.endswith('Url') and v:
                        self.assertTrue((frontend/v.lstrip('/')).is_file(),v)
                    else: scan(v)
            elif isinstance(value,list):
                for v in value: scan(v)
        for kind,file in [('characters','black_prince'),('classes','black_prince'),('artifacts','black_prince'),('weapons','asura')]:
            scan(load(kind,file))
