import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2] / 'data'

def read(kind):
    return json.loads((ROOT / kind / 'landam.json').read_text())

class LandamTests(unittest.TestCase):
    def test_ultimate_has_base_and_three_manifest_levels(self):
        u = read('characters')[0]['ultimate']
        self.assertEqual(u['name'], '교아참')
        self.assertEqual((u['tpCost'], u['range'], u['cooldown']), (5, [1, 1], 5))
        self.assertEqual([l['step'] for l in u['levels']], [0, 1, 3, 5])
        for l, damage in zip(u['levels'], [200, 210, 220, 230]):
            self.assertIn(f'[{damage}%]', l['effect'])
            self.assertIn('[20%]', l['effect'])
            self.assertIn('[5]{red}칸', l['effect'])
            self.assertIn('반격당하지 않고 호위할 수 없습니다', l['effect'])

    def test_passive_and_manifest_values(self):
        c = read('characters')[0]
        self.assertEqual(c['releaseDate'], '2024-01-09')
        self.assertEqual(c['appearedIn'], '창세기전2')
        self.assertEqual((c['birthYear'], c['height'], c['cv']), ('에스겔력 1162년', '190cm', '최낙윤'))
        ls = c['passive']['levels']
        self.assertEqual([(l['type'], l['step']) for l in ls], [('각성', n) for n in [3,4,5,6]] + [('발현', n) for n in [2,4,6]])
        self.assertNotIn('회복', ls[0]['effect'])
        for l, heal in zip(ls[1:], [3,4,5,6,7,8]):
            self.assertIn(f'[{heal}%]', l['effect'])
            self.assertIn('[30%]', l['effect'])
        for i, l in enumerate(ls[4:], 1):
            for name in ['하울랜서','호위병','돌격병']:
                self.assertIn(f'[{name} {i}]', l['effect'])
            self.assertIn('클래스 보유중', l['effect'])

    def test_shared_data_and_assets(self):
        c = read('characters')[0]
        self.assertEqual(c['classTree'], ['파이크','가드','제너럴','어스퀘이커','마샬','로얄랜서'])
        self.assertEqual(c['artifacts'], ['가시 군주의 반지','팔랑크스 전술서','섬광연격 비전서'])
        for kind, refs in [('classes', c['classTree']), ('artifacts', c['artifacts']), ('buffs', []), ('debuffs', [])]:
            names = [v['name'] for p in (ROOT/kind).glob('*.json') for v in json.loads(p.read_text())]
            self.assertEqual(len(names), len(set(names)))
            self.assertTrue(set(refs) <= set(names))
        self.assertEqual(len(read('artifacts')), 1)
        self.assertFalse((ROOT/'classes/landam.json').exists())

    def test_manifest_related_effects(self):
        bs = {b['name']: b for b in read('buffs')}
        for name, stacks in [('호위 방어술', 3), ('돌격 방어술', 10)]:
            for i, l in enumerate(bs[name]['levels'], 1):
                self.assertEqual((l['duration'], l['maxStack']), (1, stacks))
                self.assertIn(f'[-{i+2}%]', l['effect'])
        for i, l in enumerate(bs['랜서쉴드']['levels'], 1):
            self.assertIn(f'[{20+i*10}%]', l['effect'])
            self.assertEqual(l['duration'], 2)
        self.assertNotIn('이동력', bs['선봉대의 진격']['levels'][1]['effect'])
        self.assertIn('이동력 [+1]', bs['선봉대의 진격']['levels'][2]['effect'])
        for l in bs['호위병']['levels']:
            self.assertIn('쿨타임 [+1]', l['effect'])
        for l, value in zip(read('debuffs')[0]['levels'], [5,7.5,10]):
            self.assertIn(f'[+{value}%]', l['effect'])
            self.assertEqual(l['duration'], 2)

    def test_weapon_and_ring(self):
        w = read('weapons')[0]
        self.assertEqual(w['description'], '아스타니아 법국의 국보이자 주신이 만든 무기라 전해지는 성스러운 창. 마장기 가리우스를 기동시키는 열쇠이기도 하다.\n랜담이 장착하면 무기의 잠재력을 끌어낼 수 있다.')
        self.assertEqual([s['maxHp'] for s in w['baseStats']], [127,128,129,131,132,133])
        self.assertEqual([s['attack'] for s in w['baseStats']], [347,350,354,358,361,365])
        for e, start in zip(w['effects'], [30,20]):
            self.assertEqual([l['step'] for l in e['levels']], [1,2,3,4,5,6])
            for i, l in enumerate(e['levels']):
                self.assertIn(f'[{start+i*2}%]', l['effect'])
                self.assertIn('치명타를 발동했을 경우', l['effect'])
        self.assertEqual([l['step'] for l in read('artifacts')[0]['levels']], [3,4,5,6])

if __name__ == '__main__':
    unittest.main()
