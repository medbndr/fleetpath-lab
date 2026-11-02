import unittest
from fleetpath.core import Grid, plan, svg

def mission(name, start, goal):
    return dict(id=name, start=start, goal=goal)

class Routes(unittest.TestCase):
    def test_shortest_single(self):
        path = plan(Grid(4,4), [mission('a',(0,0),(3,3))])['a']
        self.assertEqual(len(path), 7)

    def test_conflicts_and_steps(self):
        grid = Grid(5,3)
        paths = list(plan(grid, [mission('a',(0,1),(4,1)), mission('b',(4,1),(0,1))]).values())
        length = max(map(len, paths))
        a,b = [p + [p[-1]] * (length-len(p)) for p in paths]
        for t in range(length):
            self.assertNotEqual(a[t], b[t])
            if t:
                self.assertFalse(a[t-1] == b[t] and b[t-1] == a[t])
                for route in (a,b):
                    self.assertLessEqual(sum(abs(x-y) for x,y in zip(route[t-1],route[t])),1)

    def test_obstacles(self):
        g = Grid(3,3,frozenset({(1,0),(1,1)}))
        p = plan(g,[mission('a',(0,0),(2,0))])['a']
        self.assertEqual(len(p),7)
        self.assertTrue(all(g.valid(c) for c in p))

    def test_impossible_swap(self):
        with self.assertRaises(ValueError):
            plan(Grid(2,1),[mission('a',(0,0),(1,0)),mission('b',(1,0),(0,0))],4)

    def test_goal_held(self):
        with self.assertRaises(ValueError):
            plan(Grid(3,1),[mission('a',(1,0),(1,0)),mission('b',(0,0),(2,0))],4)

    def test_duplicate_start(self):
        with self.assertRaises(ValueError):
            plan(Grid(2,2),[mission('a',(0,0),(1,0)),mission('b',(0,0),(0,1))])

    def test_horizon(self):
        with self.assertRaises(ValueError):
            plan(Grid(3,3),[mission('a',(0,0),(2,2))],3)

    def test_zero_and_svg_escape(self):
        self.assertEqual(plan(Grid(1,1),[mission('<x>',(0,0),(0,0))],0), {'<x>':[(0,0)]})
        self.assertIn('&lt;x&gt;',svg(Grid(1,1),{'<x>':[(0,0)]}))
