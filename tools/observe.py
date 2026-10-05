import argparse
import json
from pathlib import Path

import numpy
import shapely

GAP = .01


def outline(coverage):
    cell, runs = coverage['cell'], numpy.asarray(coverage['runs'], dtype=float).reshape(-1, 3)
    if not len(runs):
        return None, 'has no geometry'
    parts = shapely.union_all(shapely.box(runs[:, 1] * cell, runs[:, 0] * cell, (runs[:, 2] + 1) * cell, (runs[:, 0] + 1) * cell))
    union = parts.union(parts.buffer(GAP).buffer(-GAP))
    if union.geom_type != 'Polygon':
        return None, f'projects to {len(union.geoms)} disjoint parts, but footprint_xy is one outline; join the parts or split the entry in blockout'
    return [[round(x, 6), round(y, 6)] for x, y in union.simplify(cell).exterior.coords[:-1]], None


def observe(placed, apertures):
    observed = {}
    for ident, record in placed.items():
        footprint, error = (None, record['error']) if 'error' in record else outline(record['coverage'])
        observed[ident] = {'error': f'placed geometry {error}'} if error else {'footprint_xy': footprint, 'front_xy': record['front_xy'], 'regions': record['regions']}
        if ident in apertures:
            observed[ident]['aperture_luminance'] = apertures[ident]
    return observed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('placed')
    parser.add_argument('--apertures')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    apertures = json.loads(Path(args.apertures).read_text()) if args.apertures and Path(args.apertures).is_file() else {}
    if not isinstance(apertures, dict):
        raise SystemExit(f'{args.apertures}: must be an object keyed by object id')
    Path(args.output).write_text(json.dumps(observe(json.loads(Path(args.placed).read_text()), apertures), indent=2) + '\n')


if __name__ == '__main__':
    main()
