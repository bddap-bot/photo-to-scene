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


def region_ids(geometry):
    return [region.get('id') for region in geometry.get('regions', [])]


def region_bbox(geometry, region_id):
    box = next((region.get('bbox') for region in geometry.get('regions', []) if region.get('id') == region_id), None)
    return box if isinstance(box, dict) and all(len(box.get(k, [])) == 3 for k in ('min', 'max')) else None


def relationship_error(relation, own, other, tolerance):
    kind = relation.get('type')
    if kind not in ('minimum_xy_clearance', 'supported_by'):
        return None
    if kind == 'supported_by':
        region, support = relation.get('region'), relation.get('support_region')
        own_box, support_box = region_bbox(own, region), region_bbox(other, support)
        if not own_box or not support_box:
            return f'region must name one of {region_ids(own)} and support_region one of {region_ids(other)}; got region={region!r}, support_region={support!r}'
    footprints = own.get('footprint_xy', []), other.get('footprint_xy', [])
    if any(len(footprint) < 3 or any(len(point) != 2 for point in footprint) for footprint in footprints):
        return 'both objects need footprint_xy with at least three [x, y] points'
    gap = polygon_distance(*footprints)
    if kind == 'minimum_xy_clearance':
        if gap + 1e-6 < relation.get('metres', 0):
            return f'footprints are {gap:.3f} m apart, less than {relation["metres"]} m'
        return None
    rise = own_box['min'][2] - support_box['max'][2]
    if abs(rise) > tolerance or gap > tolerance:
        return f'region {region} bottom z={own_box["min"][2]:.3f} m sits {rise:+.3f} m from support_region {support} top z={support_box["max"][2]:.3f} m and footprints are {gap:.3f} m apart; both must be within {tolerance} m'
    return None


def check_contract(entry, entries, tolerance, errors):
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
    ids = region_ids(contract)
    if not ids or len(ids) != len(set(ids)):
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
        error = relationship_error(relation, contract, other.get('spatial_contract') or {}, tolerance)
        if error:
            errors.append(f'{ident}: declared {relation["type"]} {other["id"]}: {error}')


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
            elif bbox_error(region['bbox'], actual_regions[region['id']]) > tolerance / max(region.get('confidence', 1), .25):
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
            error = relationship_error(relation, observed[ident], observed[other_id], tolerance)
            if error:
                errors.append(f'{ident}: observed {relation["type"]} {other_id}: {error}')


def load_inventory(path):
    try:
        data = json.loads(Path(path).read_text())
    except json.JSONDecodeError as error:
        return {}, [f'objects.json: not valid JSON: {error}']
    if not isinstance(data, list) or not data:
        return {}, [f'objects.json: top level must be a nonempty array of object entries, got {json.dumps(data) if data == [] else type(data).__name__}']
    errors = [f'objects.json[{index}]: entry must be an object with a string id' for index, entry in enumerate(data) if not isinstance(entry, dict) or not isinstance(entry.get('id'), str)]
    ids = [entry['id'] for entry in data if isinstance(entry, dict) and isinstance(entry.get('id'), str)]
    errors += [f'objects.json: duplicate id {ident}' for ident in sorted({ident for ident in ids if ids.count(ident) > 1})]
    return ({}, errors) if errors else ({entry['id']: entry for entry in data}, [])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('objects')
    parser.add_argument('--observed')
    parser.add_argument('--tolerance', type=float, default=.03)
    parser.add_argument('--output')
    args = parser.parse_args()
    entries, errors = load_inventory(args.objects)
    ids = list(entries)
    for ident in ids:
        check_contract(entries[ident], entries, args.tolerance, errors)
    if args.observed and not errors:
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
