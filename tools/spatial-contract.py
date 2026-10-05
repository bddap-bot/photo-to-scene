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


CONTRACT_FIELDS = ('source_evidence', 'frame', 'footprint_xy', 'regions', 'relationships', 'ownership')
APPEARANCE_FIELDS = ('aperture_background', 'minimum_luminance')
OPTIONAL_FIELDS = ('appearance', 'inferred')
VECTOR3 = '[x, y, z] numbers'
BOX = '{"min": [x, y, z], "max": [x, y, z]}'


RELATIONSHIP_FIELDS = {'supported_by': {'type', 'with', 'region', 'support_region'}, 'minimum_xy_clearance': {'type', 'with', 'metres'}}


def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def is_vector(value, size):
    return isinstance(value, list) and len(value) == size and all(is_number(v) for v in value)


def is_box(value):
    return isinstance(value, dict) and set(value) == {'min', 'max'} and is_vector(value['min'], 3) and is_vector(value['max'], 3)


def is_footprint(value):
    return isinstance(value, list) and len(value) >= 3 and all(is_vector(point, 2) for point in value)


def is_fraction(value):
    return is_number(value) and 0 <= value <= 1


def is_relationship(relation):
    fields = isinstance(relation, dict) and isinstance(relation.get('type'), str) and RELATIONSHIP_FIELDS.get(relation['type'])
    return bool(fields) and set(relation) <= fields and all(isinstance(relation.get(key, ''), str) for key in ('with', 'region', 'support_region')) and 'with' in relation and (relation['type'] != 'minimum_xy_clearance' or (is_number(relation.get('metres')) and relation['metres'] >= 0))


def contract_shape_errors(entry):
    ident = entry['id']
    contract = entry.get('spatial_contract')
    if not contract:
        return [f'{ident}: missing spatial_contract']
    if not isinstance(contract, dict):
        return [f'{ident}: spatial_contract must be an object with fields {list(CONTRACT_FIELDS)} and optional {list(OPTIONAL_FIELDS)}']
    errors = [f'{ident}: missing spatial_contract.{field}' for field in CONTRACT_FIELDS if field not in contract]
    errors += [f'{ident}: spatial_contract.{field} is not a contract field; allowed: {list(CONTRACT_FIELDS) + list(OPTIONAL_FIELDS)}' for field in contract if field not in CONTRACT_FIELDS + OPTIONAL_FIELDS]
    if 'inferred' in contract:
        if contract['inferred'] is not True:
            errors.append(f'{ident}: spatial_contract.inferred must be true when present; omit it for an observed entry')
        elif 'crop_bbox' in entry:
            errors.append(f'{ident}: spatial_contract.inferred marks structure the photograph does not show, so the entry has no crop_bbox; remove crop_bbox, or remove inferred when the crop shows this object')
    elif not (is_vector(entry.get('crop_bbox'), 4) and entry['crop_bbox'][2] > 0 and entry['crop_bbox'][3] > 0):
        errors.append(f'{ident}: crop_bbox must be source pixels [x, y, width, height] with positive size; an entry the photograph does not show sets spatial_contract.inferred to true instead')
    if not is_box(entry.get('bbox')):
        errors.append(f'{ident}: bbox must be {BOX}')
    if 'source_evidence' in contract and not (isinstance(contract['source_evidence'], dict) and contract['source_evidence']):
        errors.append(f'{ident}: spatial_contract.source_evidence must be a nonempty object')
    frame = contract.get('frame')
    if 'frame' in contract and not (isinstance(frame, dict) and set(frame) == {'origin_xyz', 'x_axis_xy', 'y_axis_xy', 'size_xyz'} and is_vector(frame['origin_xyz'], 3) and is_vector(frame['size_xyz'], 3) and is_vector(frame['x_axis_xy'], 2) and is_vector(frame['y_axis_xy'], 2)):
        errors.append(f'{ident}: spatial_contract.frame must be {{"origin_xyz": {VECTOR3}, "size_xyz": {VECTOR3}, "x_axis_xy": [x, y], "y_axis_xy": [x, y]}}')
    if 'footprint_xy' in contract and not is_footprint(contract['footprint_xy']):
        errors.append(f'{ident}: spatial_contract.footprint_xy must be at least three [x, y] number points')
    regions = contract.get('regions', [])
    if not isinstance(regions, list) or not all(isinstance(region, dict) and set(region) <= {'id', 'bbox', 'confidence'} and isinstance(region.get('id'), str) and region['id'] and is_box(region.get('bbox')) and is_fraction(region.get('confidence', 1)) for region in regions):
        errors.append(f'{ident}: spatial_contract.regions must be a list of {{"id": nonempty string, "bbox": {BOX}, "confidence": optional 0..1}}')
    relationships = contract.get('relationships', [])
    if not isinstance(relationships, list) or not all(is_relationship(relation) for relation in relationships):
        errors.append(f'{ident}: spatial_contract.relationships must be a list of checked relationships, {{"type": "supported_by", "with": id, "region": own region, "support_region": target region}} or {{"type": "minimum_xy_clearance", "with": id, "metres": number >= 0}}; evidence belongs in source_evidence')
    if 'ownership' in contract and contract['ownership'] not in ({'children': 'external'}, {'children': 'included'}):
        errors.append(f'{ident}: spatial_contract.ownership must be {{"children": "external"}} or {{"children": "included"}}')
    if 'appearance' not in contract:
        return errors
    appearance = contract['appearance']
    if not isinstance(appearance, dict):
        errors.append(f'{ident}: spatial_contract.appearance must be an object')
        return errors
    errors += [f'{ident}: spatial_contract.appearance.{field} is not a machine-checked appearance field; allowed: {list(APPEARANCE_FIELDS)}. Dimensions belong in regions, material in the entry material_note, corrections in feedback' for field in appearance if field not in APPEARANCE_FIELDS]
    if set(appearance) <= set(APPEARANCE_FIELDS) and (appearance.get('aperture_background') != 'source_visible' or not is_fraction(appearance.get('minimum_luminance'))):
        errors.append(f'{ident}: spatial_contract.appearance must be {{"aperture_background": "source_visible", "minimum_luminance": 0..1}} when the source shows an exterior through an opening, otherwise absent')
    return errors


def check_contract(entry, entries, tolerance, errors):
    ident = entry['id']
    shape = contract_shape_errors(entry)
    if shape:
        errors += shape
        return
    contract = entry['spatial_contract']
    lo = entry['bbox']['min']
    hi = entry['bbox']['max']
    for point in contract['footprint_xy']:
        if not lo[0] - 1e-6 <= point[0] <= hi[0] + 1e-6 or not lo[1] - 1e-6 <= point[1] <= hi[1] + 1e-6:
            errors.append(f'{ident}: footprint point outside bbox')
    frame = contract['frame']
    axes = [frame['x_axis_xy'], frame['y_axis_xy']]
    if any(value <= 0 for value in frame['size_xyz']):
        errors.append(f'{ident}: frame needs positive size_xyz')
    elif any(abs(math.hypot(*axis) - 1) > .01 for axis in axes) or abs(sum(a * b for a, b in zip(*axes))) > .01:
        errors.append(f'{ident}: frame axes must be orthonormal')
    ids = region_ids(contract)
    if not ids or len(ids) != len(set(ids)):
        errors.append(f'{ident}: regions must be nonempty and unique')
    for region in contract['regions']:
        box = region['bbox']
        if any(box['min'][i] < lo[i] - 1e-6 or box['max'][i] > hi[i] + 1e-6 or box['min'][i] >= box['max'][i] for i in range(3)):
            errors.append(f'{ident}: invalid region {region["id"]}')
    for relation in contract['relationships']:
        other = entries.get(relation['with'])
        if not other:
            errors.append(f'{ident}: unknown relationship target {relation["with"]}')
            continue
        target = contract_shape_errors(other)
        if target:
            errors.append(f'{ident}: relationship target {other["id"]} has an invalid contract: {"; ".join(target)}')
            continue
        error = relationship_error(relation, contract, other['spatial_contract'], tolerance)
        if error:
            errors.append(f'{ident}: declared {relation["type"]} {other["id"]}: {error}')


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def room_walls(polygon):
    area = sum(a[0] * b[1] - b[0] * a[1] for a, b in segments(polygon))
    walls = []
    for a, b in segments(polygon):
        length = distance(a, b)
        if length:
            side = 1 if area > 0 else -1
            walls.append((a, b, [side * (a[1] - b[1]) / length, side * (b[0] - a[0]) / length], [-math.inf, math.inf], f'floorplan wall {a}->{b}'))
    return walls


def wall_contact(footprint, a, b, normal, tolerance):
    length = distance(a, b)
    along = [(b[0] - a[0]) / length, (b[1] - a[1]) / length]
    total = 0
    for p, q in segments(footprint):
        if all(abs(dot([r[0] - a[0], r[1] - a[1]], normal)) <= tolerance for r in (p, q)):
            s, t = sorted(dot([r[0] - a[0], r[1] - a[1]], along) for r in (p, q))
            total += max(0, min(t, length) - max(s, 0))
    return total


def front_face(contract):
    frame = contract['frame']
    o, x, y, size = frame['origin_xyz'], frame['x_axis_xy'], frame['y_axis_xy'], frame['size_xyz']
    a = [o[0] + y[0] * size[1], o[1] + y[1] * size[1]]
    return a, [a[0] + x[0] * size[0], a[1] + x[1] * size[0]]


ALONG_WALL, ON_SUPPORT = .99, .5


def faces(front, normals, threshold):
    return any(dot(front, normal) >= threshold for normal in normals)


def required_facing(entries, walls, tolerance):
    required = {}
    while True:
        surfaces = list(walls)
        for ident, (normals, threshold, _) in required.items():
            front = entries[ident]['spatial_contract']['frame']['y_axis_xy']
            if threshold == ALONG_WALL and faces(front, normals, threshold):
                box = entries[ident]['bbox']
                surfaces.append((*front_face(entries[ident]['spatial_contract']), front, [box['min'][2], box['max'][2]], f'front of {ident}'))
        found = {}
        for ident, entry in entries.items():
            if ident in required:
                continue
            low, high = entry['bbox']['min'][2], entry['bbox']['max'][2]
            footprint = entry['spatial_contract']['footprint_xy']
            contacts = [(length, normal, label) for a, b, normal, (bottom, top), label in surfaces if min(high, top) - max(low, bottom) > tolerance and (length := wall_contact(footprint, a, b, normal, tolerance)) > tolerance]
            if not contacts:
                continue
            best = max(contacts, key=lambda c: c[0])
            touching = [c for c in contacts if c[0] >= best[0] - tolerance]
            if any(dot(m[1], n[1]) < -.5 for m in touching for n in contacts):
                continue
            found[ident] = ([c[1] for c in touching], ALONG_WALL, f'its footprint lies {best[0]:.3f} m along {best[2]}, whose interior normal is {best[1]}')
        if not found:
            for ident, entry in entries.items():
                support = next((r['with'] for r in entry['spatial_contract']['relationships'] if r['type'] == 'supported_by' and r['with'] in required), None)
                if ident not in required and support:
                    found[ident] = (required[support][0], ON_SUPPORT, f'it is supported_by {support}, which faces {required[support][0][0]}, and must face within 60 degrees of it')
        if not found:
            return required
        required.update(found)


def check_facing(entries, room, tolerance, errors):
    for ident, (normals, threshold, reason) in required_facing(entries, room_walls(room), tolerance).items():
        front = entries[ident]['spatial_contract']['frame']['y_axis_xy']
        if not faces(front, normals, threshold):
            errors.append(f'{ident}: frame.y_axis_xy {front} does not face into the room: {reason}; set frame.y_axis_xy to {normals[0]} with x_axis_xy perpendicular to it, or GOTO floorplan if that wall is wrong')


def load_room(path):
    data, error = load_json(path)
    if error:
        return None, error
    room = data.get('room') if isinstance(data, dict) else None
    polygon = room.get('polygon_xy_m') if isinstance(room, dict) else None
    if not is_footprint(polygon) or not any(a[0] * b[1] - b[0] * a[1] for a, b in segments(polygon)):
        return None, 'floorplan.json: room.polygon_xy_m must be the interior room outline as at least three [x, y] metre points enclosing an area; GOTO floorplan to record it'
    return polygon, None


def observed_shape_error(ident, actual):
    if not isinstance(actual, dict):
        return f'{ident}: observed record must be an object'
    if isinstance(actual.get('error'), str):
        return f'{ident}: {actual["error"]}'
    if not is_footprint(actual.get('footprint_xy')) or not is_vector(actual.get('front_xy'), 2):
        return f'{ident}: observed record needs footprint_xy (at least three [x, y] points) and front_xy [x, y]'
    regions = actual.get('regions', [])
    if not isinstance(regions, list) or not all(isinstance(region, dict) and isinstance(region.get('id'), str) and is_box(region.get('bbox')) for region in regions):
        return f'{ident}: observed regions must be a list of {{"id": string, "bbox": {BOX}}}'
    if not is_number(actual.get('aperture_luminance', 0.0)):
        return f'{ident}: observed aperture_luminance must be a number'
    return None


def check_observed(entries, observed, ids, tolerance, errors):
    valid = set()
    for ident in ids:
        expected = entries[ident]['spatial_contract']
        actual = observed.get(ident)
        if not actual:
            errors.append(f'{ident}: missing observed invariant record')
            continue
        shape = observed_shape_error(ident, actual)
        if shape:
            errors.append(shape)
            continue
        valid.add(ident)
        if polygon_error(expected['footprint_xy'], actual['footprint_xy']) > tolerance:
            errors.append(f'{ident}: footprint did not round-trip')
        dot = sum(a * b for a, b in zip(expected['frame']['y_axis_xy'], actual['front_xy']))
        if dot < .98:
            errors.append(f'{ident}: facing did not round-trip')
        actual_regions = {r['id']: r['bbox'] for r in actual.get('regions', [])}
        for region in expected['regions']:
            if region['id'] not in actual_regions:
                errors.append(f'{ident}: missing region {region["id"]}')
            elif bbox_error(region['bbox'], actual_regions[region['id']]) > tolerance / max(region.get('confidence', 1), .25):
                errors.append(f'{ident}: region {region["id"]} did not round-trip')
        appearance = expected.get('appearance')
        if appearance and actual.get('aperture_luminance', 0) < appearance['minimum_luminance']:
            errors.append(f'{ident}: source-visible aperture is black')
    for ident in ids:
        if ident not in valid:
            continue
        for relation in entries[ident]['spatial_contract']['relationships']:
            other_id = relation['with']
            if other_id not in observed:
                errors.append(f'{ident}: relationship target {other_id} was not observed')
                continue
            if other_id not in valid:
                continue
            error = relationship_error(relation, observed[ident], observed[other_id], tolerance)
            if error:
                errors.append(f'{ident}: observed {relation["type"]} {other_id}: {error}')


def load_json(path):
    try:
        return json.loads(Path(path).read_text(), parse_int=float), None
    except (OSError, ValueError, RecursionError) as error:
        return None, f'{Path(path).name}: not valid JSON: {error}'


def load_inventory(path):
    data, error = load_json(path)
    if error:
        return {}, [error]
    if not isinstance(data, list) or not data:
        return {}, [f'objects.json: top level must be a nonempty array of object entries, got {json.dumps(data) if data == [] else type(data).__name__}']
    errors = [f'objects.json[{index}]: entry must be an object with a string id' for index, entry in enumerate(data) if not isinstance(entry, dict) or not isinstance(entry.get('id'), str)]
    ids = [entry['id'] for entry in data if isinstance(entry, dict) and isinstance(entry.get('id'), str)]
    errors += [f'objects.json: duplicate id {ident}' for ident in sorted({ident for ident in ids if ids.count(ident) > 1})]
    return ({}, errors) if errors else ({entry['id']: entry for entry in data}, [])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('objects')
    parser.add_argument('--floorplan', required=True)
    parser.add_argument('--observed')
    parser.add_argument('--tolerance', type=float, default=.03)
    parser.add_argument('--output')
    args = parser.parse_args()
    entries, errors = load_inventory(args.objects)
    ids = list(entries)
    for ident in ids:
        check_contract(entries[ident], entries, args.tolerance, errors)
    if not errors:
        room, error = load_room(args.floorplan)
        if error:
            errors.append(error)
        else:
            check_facing(entries, room, args.tolerance, errors)
    if args.observed and not errors:
        observed, error = load_json(args.observed)
        if error or not isinstance(observed, dict):
            errors.append(error or f'{Path(args.observed).name}: top level must be an object keyed by object id, got {type(observed).__name__}')
        else:
            check_observed(entries, observed, ids, args.tolerance, errors)
    digest = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest() if Path(path).is_file() else None
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
