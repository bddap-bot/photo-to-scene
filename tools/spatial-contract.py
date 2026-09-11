import argparse
import hashlib
import json
import math
from pathlib import Path


def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def point_segment(p, a, b):
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    den = dx * dx + dy * dy
    t = 0 if den == 0 else max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / den))
    return distance(p, [a[0] + t * dx, a[1] + t * dy])


def segments(poly):
    return list(zip(poly, poly[1:] + poly[:1]))


def orient(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def intersects(a, b, c, d):
    values = [orient(a, b, c), orient(a, b, d), orient(c, d, a), orient(c, d, b)]
    if values[0] * values[1] < 0 and values[2] * values[3] < 0:
        return True
    def on_segment(p, q, r):
        return abs(orient(p, q, r)) <= 1e-9 and min(p[0], q[0]) - 1e-9 <= r[0] <= max(p[0], q[0]) + 1e-9 and min(p[1], q[1]) - 1e-9 <= r[1] <= max(p[1], q[1]) + 1e-9
    return on_segment(a, b, c) or on_segment(a, b, d) or on_segment(c, d, a) or on_segment(c, d, b)


def contains(poly, point):
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        if (poly[i][1] > point[1]) != (poly[j][1] > point[1]):
            x = (poly[j][0] - poly[i][0]) * (point[1] - poly[i][1]) / (poly[j][1] - poly[i][1]) + poly[i][0]
            if point[0] < x:
                inside = not inside
        j = i
    return inside


def polygon_distance(a, b):
    if contains(a, b[0]) or contains(b, a[0]) or any(intersects(p, q, r, s) for p, q in segments(a) for r, s in segments(b)):
        return 0
    return min([point_segment(p, r, s) for p in a for r, s in segments(b)] + [point_segment(p, r, s) for p in b for r, s in segments(a)])


def polygon_error(a, b):
    if len(a) < 3 or len(b) < 3:
        return math.inf
    return max([min(point_segment(p, r, s) for r, s in segments(b)) for p in a] + [min(point_segment(p, r, s) for r, s in segments(a)) for p in b])


def bbox_error(a, b):
    return max(abs(a[k][i] - b[k][i]) for k in ('min', 'max') for i in range(3))


def check_contract(entry, entries, errors):
    ident = entry['id']
    contract = entry.get('spatial_contract')
    if not contract:
        errors.append(f'{ident}: missing spatial_contract')
        return
    for field in ('source_evidence', 'frame', 'footprint_xy', 'front_xy', 'regions', 'relationships', 'ownership'):
        if field not in contract:
            errors.append(f'{ident}: missing spatial_contract.{field}')
    footprint = contract.get('footprint_xy', [])
    if len(footprint) < 3:
        errors.append(f'{ident}: footprint_xy needs at least three points')
    lo = entry['bbox']['min']
    hi = entry['bbox']['max']
    for point in footprint:
        if len(point) != 2 or not lo[0] - 1e-6 <= point[0] <= hi[0] + 1e-6 or not lo[1] - 1e-6 <= point[1] <= hi[1] + 1e-6:
            errors.append(f'{ident}: footprint point outside bbox')
    front = contract.get('front_xy', [])
    if len(front) != 2 or abs(math.hypot(*front) - 1) > .01:
        errors.append(f'{ident}: front_xy must be a unit vector')
    frame = contract.get('frame', {})
    axes = [frame.get(name, []) for name in ('x_axis_xy', 'y_axis_xy')]
    if len(frame.get('origin_xyz', [])) != 3 or len(frame.get('size_xyz', [])) != 3 or any(value <= 0 for value in frame.get('size_xyz', [0])):
        errors.append(f'{ident}: frame needs positive size_xyz and origin_xyz')
    elif any(len(axis) != 2 or abs(math.hypot(*axis) - 1) > .01 for axis in axes) or abs(sum(a * b for a, b in zip(*axes))) > .01:
        errors.append(f'{ident}: frame axes must be orthonormal')
    elif sum(a * b for a, b in zip(frame['y_axis_xy'], front)) < .999:
        errors.append(f'{ident}: frame y axis must equal front_xy')
    region_ids = [r.get('id') for r in contract.get('regions', [])]
    if not region_ids or len(region_ids) != len(set(region_ids)):
        errors.append(f'{ident}: regions must be nonempty and unique')
    for region in contract.get('regions', []):
        box = region.get('bbox', {})
        if set(box) != {'min', 'max'} or any(box['min'][i] < lo[i] - 1e-6 or box['max'][i] > hi[i] + 1e-6 or box['min'][i] >= box['max'][i] for i in range(3)):
            errors.append(f'{ident}: invalid region {region.get("id")}')
    for relation in contract.get('relationships', []):
        other = entries.get(relation.get('with'))
        if not other:
            errors.append(f'{ident}: unknown relationship target {relation.get("with")}')
            continue
        if relation.get('type') == 'minimum_xy_clearance':
            other_contract = other.get('spatial_contract')
            if not other_contract:
                errors.append(f'{ident}: clearance target lacks spatial_contract')
            elif polygon_distance(footprint, other_contract['footprint_xy']) + 1e-6 < relation.get('metres', 0):
                errors.append(f'{ident}: minimum_xy_clearance violated with {other["id"]}')


def check_observed(entries, observed, ids, tolerance, errors):
    seen = {}
    for ident in ids:
        expected = entries[ident]['spatial_contract']
        actual = observed.get(ident)
        if not actual:
            errors.append(f'{ident}: missing observed invariant record')
            continue
        if polygon_error(expected['footprint_xy'], actual.get('footprint_xy', [])) > tolerance:
            errors.append(f'{ident}: footprint did not round-trip')
        front = actual.get('front_xy', [0, 0])
        dot = sum(a * b for a, b in zip(expected['front_xy'], front))
        if dot < .98:
            errors.append(f'{ident}: facing did not round-trip')
        actual_regions = {r['id']: r['bbox'] for r in actual.get('regions', [])}
        for region in expected['regions']:
            if region['id'] not in actual_regions:
                errors.append(f'{ident}: missing region {region["id"]}')
            elif bbox_error(region['bbox'], actual_regions[region['id']]) > tolerance:
                errors.append(f'{ident}: region {region["id"]} did not round-trip')
        for owned in actual.get('owned_ids', [ident]):
            if owned in seen:
                errors.append(f'{ident}: geometry ownership duplicates {owned} from {seen[owned]}')
            seen[owned] = ident
        if expected.get('ownership', {}).get('children') == 'external' and set(actual.get('owned_ids', [ident])) != {ident}:
            errors.append(f'{ident}: external child geometry was duplicated')
        appearance = expected.get('appearance', {})
        if appearance.get('aperture_background') == 'source_visible' and actual.get('aperture_luminance', 0) < appearance.get('minimum_luminance', 0):
            errors.append(f'{ident}: source-visible aperture is black')
    for ident in ids:
        if ident not in observed or ident not in entries:
            continue
        for relation in entries[ident]['spatial_contract'].get('relationships', []):
            other_id = relation.get('with')
            if other_id not in observed:
                errors.append(f'{ident}: relationship target {other_id} was not observed')
                continue
            if relation.get('type') == 'minimum_xy_clearance':
                gap = polygon_distance(observed[ident]['footprint_xy'], observed[other_id]['footprint_xy'])
                if gap + 1e-6 < relation.get('metres', 0):
                    errors.append(f'{ident}: observed minimum_xy_clearance violated with {other_id}')
            if relation.get('type') == 'supported_by':
                region_id = relation.get('region')
                support_id = relation.get('support_region')
                own = next((r['bbox'] for r in observed[ident].get('regions', []) if r['id'] == region_id), None)
                support = next((r['bbox'] for r in observed[other_id].get('regions', []) if r['id'] == support_id), None)
                if not own or not support:
                    errors.append(f'{ident}: support regions were not observed')
                elif abs(own['min'][2] - support['max'][2]) > tolerance or polygon_distance(observed[ident]['footprint_xy'], observed[other_id]['footprint_xy']) > tolerance:
                    errors.append(f'{ident}: observed support relationship failed with {other_id}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('objects')
    parser.add_argument('--ids', required=True)
    parser.add_argument('--observed')
    parser.add_argument('--tolerance', type=float, default=.03)
    parser.add_argument('--output')
    args = parser.parse_args()
    data = json.loads(Path(args.objects).read_text())
    entries = {entry['id']: entry for entry in data}
    ids = args.ids.split(',')
    errors = []
    for ident in ids:
        if ident not in entries:
            errors.append(f'{ident}: missing object entry')
        else:
            check_contract(entries[ident], entries, errors)
    if args.observed:
        check_observed(entries, json.loads(Path(args.observed).read_text()), ids, args.tolerance, errors)
    digest = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
    result = {'valid': not errors, 'ids': ids, 'errors': errors, 'observed': bool(args.observed), 'objects_sha256': digest(args.objects)}
    if args.observed:
        result['observed_sha256'] = digest(args.observed)
    rendered = json.dumps(result, indent=2)
    if args.output:
        Path(args.output).write_text(rendered + '\n')
    print(rendered)
    raise SystemExit(0 if not errors else 1)


if __name__ == '__main__':
    main()
