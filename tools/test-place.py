import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).parent


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, TOOLS / file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


observe = load('observe', 'observe.py')
spatial_contract = load('spatial_contract', 'spatial-contract.py')

BOX_ASSET = '''import bpy
EXTRA = {extra}
def build(entry, collection=None):
    frame = entry['spatial_contract']['frame']
    boxes = {{region['id']: region['bbox'] for region in entry['spatial_contract']['regions']}}
    boxes.update(EXTRA)
    for name, box in boxes.items():
        lo, hi = ([(box[k][i] - frame['origin_xyz'][i]) / frame['size_xyz'][i] for i in range(3)] for k in ('min', 'max'))
        corners = [(x, y, z) for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]
        faces = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata(corners, [], faces)
        part = bpy.data.objects.new(name, mesh)
        if name in {{region['id'] for region in entry['spatial_contract']['regions']}}:
            part['spatial_region'] = name
        bpy.context.collection.objects.link(part)
'''

FLOOR_FOOTPRINT = [[0, 0], [6.47119043, 0], [6.47119043, 7.65596894], [-0.52, 7.65596894], [-0.52, 4.95], [0, 4.95]]


def box(lo, hi):
    return {'min': list(lo), 'max': list(hi)}


def floor_entry(ident):
    lo, hi = [-0.52, 0, -0.12], [6.47119043, 7.65596894, 0]
    return {
        'id': ident, 'crop_bbox': [0, 0, 10, 10], 'bbox': box(lo, hi),
        'spatial_contract': {
            'source_evidence': {'synthetic': True},
            'frame': {'origin_xyz': [(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, lo[2]], 'x_axis_xy': [1, 0], 'y_axis_xy': [0, 1], 'size_xyz': [hi[i] - lo[i] for i in range(3)]},
            'footprint_xy': FLOOR_FOOTPRINT,
            'front_xy': [0, 1],
            'regions': [{'id': 'main', 'bbox': box([0, 0, -0.12], [6.47119043, 7.65596894, 0])}, {'id': 'rear_recess', 'bbox': box([-0.52, 4.95, -0.12], [0, 7.65596894, 0])}],
            'relationships': [], 'ownership': {'children': 'external'},
        },
    }


def chair_entry():
    size, origin, x_axis, y_axis = [0.82, 0.85, 1.12], [2, 3, 0], [0.6, 0.8], [-0.8, 0.6]
    corners = [[origin[0] + x_axis[0] * sx * size[0] + y_axis[0] * sy * size[1], origin[1] + x_axis[1] * sx * size[0] + y_axis[1] * sy * size[1]] for sx, sy in ((-.5, -.5), (.5, -.5), (.5, .5), (-.5, .5))]
    lo = [min(c[0] for c in corners), min(c[1] for c in corners), 0]
    hi = [max(c[0] for c in corners), max(c[1] for c in corners), size[2]]
    return {
        'id': 'chair', 'crop_bbox': [0, 0, 10, 10], 'bbox': box(lo, hi),
        'spatial_contract': {
            'source_evidence': {'synthetic': True},
            'frame': {'origin_xyz': origin, 'x_axis_xy': x_axis, 'y_axis_xy': y_axis, 'size_xyz': size},
            'footprint_xy': corners, 'front_xy': y_axis,
            'regions': [{'id': 'body', 'bbox': box(lo, hi)}],
            'relationships': [], 'ownership': {'children': 'external'},
        },
    }


def square_entry(ident):
    lo, hi = [4, 1, 0], [5, 2, .5]
    return {
        'id': ident, 'crop_bbox': [0, 0, 10, 10], 'bbox': box(lo, hi),
        'spatial_contract': {
            'source_evidence': {'synthetic': True},
            'frame': {'origin_xyz': [4.5, 1.5, 0], 'x_axis_xy': [1, 0], 'y_axis_xy': [0, 1], 'size_xyz': [1, 1, .5]},
            'footprint_xy': [[4, 1], [5, 1], [5, 2], [4, 2]], 'front_xy': [0, 1],
            'regions': [{'id': 'body', 'bbox': box(lo, hi)}],
            'relationships': [], 'ownership': {'children': 'external'},
        },
    }


PARTS_ASSET = """import bpy
def part(name, lo, hi, collection):
    corners = [(x, y, z) for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(corners, [], [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)])
    obj = bpy.data.objects.new(name, mesh)
    obj['spatial_region'] = 'body'
    collection.objects.link(obj)
    return obj
def build(entry, collection=None):
%s
"""

INSTANCED_HALF = PARTS_ASSET % """    part('left', (-.5, -.5, 0), (0, .5, 1), bpy.context.collection).hide_viewport = True
    part('unrendered', (-3, -3, 0), (-2, -2, 1), bpy.context.collection).hide_render = True
    source = bpy.data.collections.new('right half')
    part('right', (0, -.5, 0), (.5, .5, 1), source)
    instancer = bpy.data.objects.new('right instance', None)
    instancer.instance_type = 'COLLECTION'
    instancer.instance_collection = source
    bpy.context.collection.objects.link(instancer)"""

RING = PARTS_ASSET % """    for lo, hi in (((-.5, -.5, 0), (.5, -.3, 1)), ((-.5, .3, 0), (.5, .5, 1)), ((-.5, -.5, 0), (-.3, .5, 1)), ((.3, -.5, 0), (.5, .5, 1))):
        bpy.context.scene.collection.objects.link(part(str(lo), lo, hi, bpy.context.collection))"""


UNIT_CUBE = '''import bpy
def build(entry, collection=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, .5))
    bpy.context.object['spatial_region'] = 'body'
'''


def blender(*args):
    result = subprocess.run(['blender', '-b', '--factory-startup', '--python-exit-code', '1', '--python', str(TOOLS / 'place.py'), '--', *map(str, args)], capture_output=True, text=True, timeout=900)
    if result.returncode:
        raise AssertionError(result.stdout[-3000:] + result.stderr[-3000:])


def contract_errors(entries, observed):
    errors = []
    for entry in entries.values():
        spatial_contract.check_contract(entry, entries, .03, errors)
    assert not errors, errors
    spatial_contract.check_observed(entries, observed, list(entries), .03, errors)
    return errors


class PlacementTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        root = cls.root = Path(cls.directory.name)
        (root / 'state').mkdir()
        (root / 'assets').mkdir()
        cls.entries = {entry['id']: entry for entry in (floor_entry('floor'), floor_entry('filled'), floor_entry('split'), chair_entry(), square_entry('stand'), square_entry('ring'))}
        (root / 'state' / 'objects.json').write_text(json.dumps(list(cls.entries.values())))
        (root / 'assets' / 'floor.py').write_text(BOX_ASSET.format(extra={}))
        (root / 'assets' / 'filled.py').write_text(BOX_ASSET.format(extra={'strip': box([-0.52, 0, -0.12], [0, 4.95, 0])}))
        (root / 'assets' / 'split.py').write_text(BOX_ASSET.format(extra={}).replace("boxes.update(EXTRA)", "boxes['main'] = {'min': [0.5, 0, -0.12], 'max': [6.47119043, 7.65596894, 0]}"))
        (root / 'assets' / 'chair.py').write_text(UNIT_CUBE)
        (root / 'assets' / 'stand.py').write_text(INSTANCED_HALF)
        (root / 'assets' / 'ring.py').write_text(RING)
        blender('place', root, root / 'state' / 'placed.blend')
        blender('measure', root / 'state' / 'placed.blend', root / 'state' / 'measured.json')
        cls.placed = json.loads((root / 'state' / 'measured.json').read_text())
        cls.observed = observe.observe(cls.placed, {})

    @classmethod
    def tearDownClass(cls):
        cls.directory.cleanup()

    def errors_for(self, ident):
        return contract_errors({ident: self.entries[ident]}, {ident: self.observed[ident]})

    def test_two_rectangle_l_floor_round_trips(self):
        self.assertEqual(self.errors_for('floor'), [])

    def test_geometry_filling_the_recess_strip_fails(self):
        self.assertEqual(self.errors_for('filled'), ['filled: footprint did not round-trip'])

    def test_disjoint_parts_are_rejected_explicitly(self):
        errors = self.errors_for('split')
        self.assertEqual(len(errors), 1)
        self.assertIn('split: placed geometry projects to 2 disjoint parts', errors[0])

    def test_instanced_parts_are_placed_and_measured_once(self):
        self.assertEqual(self.errors_for('stand'), [])

    def test_enclosed_hole_keeps_the_outer_outline(self):
        self.assertEqual(self.errors_for('ring'), [])

    def test_anisotropic_frame_is_applied_once_in_integration(self):
        self.assertEqual(self.errors_for('chair'), [])

    def test_preview_places_with_integration_proportions_and_renders(self):
        measured = self.root / 'state' / 'preview.json'
        script = self.root / 'measure_preview.py'
        script.write_text(f'''import bpy, json, sys
sys.path.insert(0, {str(TOOLS)!r})
import place
anchor = place.place_alone({str(self.root)!r}, 'chair')
open({str(measured)!r}, 'w').write(json.dumps(place.measure(anchor, bpy.context.evaluated_depsgraph_get())))
''')
        result = subprocess.run(['blender', '-b', '--factory-startup', '--python-exit-code', '1', '--python', str(script)], capture_output=True, text=True, timeout=300)
        self.assertEqual(result.returncode, 0, result.stdout[-3000:] + result.stderr[-3000:])
        preview = json.loads(measured.read_text())
        self.assertEqual(contract_errors({'chair': self.entries['chair']}, {'chair': observe.observe({'chair': preview}, {})['chair']}), [])
        self.assertEqual(preview['regions'], self.placed['chair']['regions'])
        render = self.root / 'state' / 'detail_chair.png'
        blender('preview', self.root, 'chair', render)
        self.assertEqual(render.read_bytes()[:8], b'\x89PNG\r\n\x1a\n')


if __name__ == '__main__':
    unittest.main()
