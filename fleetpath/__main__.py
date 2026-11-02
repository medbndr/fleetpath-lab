import argparse
import json
from pathlib import Path
from .core import Grid, plan, svg

def main():
    p = argparse.ArgumentParser(description='Plan synchronous grid robot routes')
    p.add_argument('scenario', type=Path)
    p.add_argument('--horizon', type=int, default=100)
    p.add_argument('--output', type=Path)
    p.add_argument('--svg', type=Path)
    args = p.parse_args()
    try:
        data = json.loads(args.scenario.read_text(encoding='utf-8'))
        grid = Grid(data['width'], data['height'], frozenset(map(tuple, data.get('walls', []))))
        paths = plan(grid, data['robots'], args.horizon)
        result = {'paths': paths, 'makespan': max((len(x)-1 for x in paths.values()), default=0),
                  'total_steps': sum(len(x)-1 for x in paths.values())}
        output = json.dumps(result, indent=2)
        if args.output:
            args.output.write_text(output + '\n', encoding='utf-8')
        if args.svg:
            args.svg.write_text(svg(grid, paths), encoding='utf-8')
        print(output)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        p.exit(2, f'error: {exc}\n')

if __name__ == '__main__':
    main()
