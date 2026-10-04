import argparse
import json
from pathlib import Path

import numpy
import shapely

SEAM = .001
GAP = .01


def outline(triangles):
    corners = numpy.asarray(triangles, dtype=float).reshape(-1, 3, 2)
    if not len(corners):
        return None, 'has no geometry'
    edges = corners[:, 1:] - corners[:, :1]
    flat = numpy.abs(edges[:, 0, 0] * edges[:, 1, 1] - edges[:, 0, 1] * edges[:, 1, 0]) <= 1e-12
    parts = shapely.union_all(numpy.concatenate([shapely.polygons(corners[~flat]), shapely.linestrings(corners[flat])]))
    union = parts.buffer(SEAM, join_style='mitre').union(parts.buffer(GAP).buffer(-GAP))
    if union.geom_type != 'Polygon':
        return None, f'projects to {len(union.geoms)} disjoint parts, but footprint_xy is one outline; join the parts or split the entry in blockout'
    return [[round(x, 6), round(y, 6)] for x, y in union.simplify(SEAM / 2).exterior.coords[:-1]], None


def observe(placed, apertures):
    observed = {}
    for ident, record in placed.items():
        footprint, error = (None, record['error']) if 'error' in record else outline(record['triangles'])
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
