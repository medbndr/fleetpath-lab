"""Prioritized, time-expanded breadth-first search with goal reservations."""
from collections import deque
from dataclasses import dataclass
from html import escape

Cell = tuple[int, int]

@dataclass(frozen=True)
class Grid:
    width: int
    height: int
    walls: frozenset[Cell] = frozenset()

    def valid(self, p):
        return 0 <= p[0] < self.width and 0 <= p[1] < self.height and p not in self.walls

def plan(grid, missions, horizon=100):
    if grid.width < 1 or grid.height < 1 or horizon < 0:
        raise ValueError('positive grid dimensions and nonnegative horizon required')
    if any(not (0 <= x < grid.width and 0 <= y < grid.height) for x, y in grid.walls):
        raise ValueError('wall outside grid')
    starts = [tuple(m['start']) for m in missions]
    names = [m['id'] for m in missions]
    if len(set(starts)) != len(starts) or len(set(names)) != len(names):
        raise ValueError('robot IDs and initial cells must be unique')
    for m in missions:
        if not grid.valid(tuple(m['start'])) or not grid.valid(tuple(m['goal'])):
            raise ValueError('start and goal must be traversable')
    vertices, edges, paths = set(), set(), {}
    for m in missions:
        start, goal = tuple(m['start']), tuple(m['goal'])
        initial = (start, 0)
        queue, parent = deque([initial]), {initial: None}
        found = None
        while queue:
            cell, t = queue.popleft()
            if cell == goal and all((goal, k) not in vertices for k in range(t, horizon + 1)):
                found = (cell, t)
                break
            if t == horizon:
                continue
            x, y = cell
            for nxt in ((x+1,y), (x,y+1), (x-1,y), (x,y-1), cell):
                state = (nxt, t+1)
                if (grid.valid(nxt) and state not in parent and state not in vertices
                        and (nxt, cell, t+1) not in edges):
                    parent[state] = (cell, t)
                    queue.append(state)
        if found is None:
            raise ValueError(f"no route for {m['id']} within horizon/priority constraints")
        path = []
        while found is not None:
            path.append(found[0])
            found = parent[found]
        path.reverse()
        paths[m['id']] = path
        padded = path + [goal] * (horizon + 1 - len(path))
        vertices.update((p, t) for t, p in enumerate(padded))
        edges.update((padded[t-1], padded[t], t) for t in range(1, len(padded)))
    return paths

def svg(grid, paths):
    size, pad = 36, 28
    width, height = grid.width*size+pad*2, grid.height*size+pad*2+60
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
           '<rect width="100%" height="100%" fill="#101827"/>',
           '<text x="28" y="30" fill="white" font-family="sans-serif" font-size="17">FLEETPATH / ROUTE REPORT</text>']
    for y in range(grid.height):
        for x in range(grid.width):
            fill = '#475569' if (x,y) in grid.walls else '#1e293b'
            out.append(f'<rect x="{pad+x*size}" y="{60+y*size}" width="34" height="34" rx="5" fill="{fill}"/>')
    colors = ['#38bdf8', '#a78bfa', '#4ade80', '#fb923c']
    for i, (name, path) in enumerate(paths.items()):
        color = colors[i % len(colors)]
        points = ' '.join(f'{pad+x*size+17},{60+y*size+17}' for x,y in path)
        out.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="4" opacity="0.8"/>')
        x,y = path[-1]
        out.append(f'<circle cx="{pad+x*size+17}" cy="{60+y*size+17}" r="10" fill="{color}"/>')
        x,y = path[0]
        out.append(f'<text x="{pad+x*size+4}" y="{60+y*size+15}" fill="white" font-size="11">{escape(str(name))}</text>')
    return ''.join(out) + '</svg>'
