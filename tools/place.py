import importlib.util
import json
import math
import sys
import traceback
from pathlib import Path

import bpy
import numpy
from mathutils import Matrix, Vector

GEOMETRY_TYPES = {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT'}
CELL = .005
CHUNK = 1 << 20
SHIFT = 1 << 32


def frame_matrix(frame):
    (ox, oy, oz), (sx, sy, sz) = frame['origin_xyz'], frame['size_xyz']
    (xx, xy), (yx, yy) = frame['x_axis_xy'], frame['y_axis_xy']
    return Matrix(((xx * sx, yx * sy, 0, ox), (xy * sx, yy * sy, 0, oy), (0, 0, sz, oz), (0, 0, 0, 1)))


def place(root, entry):
    ident = entry['id']
    scene = bpy.context.scene
    collection = bpy.data.collections.new(ident)
    scene.collection.children.link(collection)
    layers = bpy.context.view_layer.layer_collection
    bpy.context.view_layer.active_layer_collection = layers.children[collection.name]
    objects, collections = set(bpy.data.objects), set(bpy.data.collections)
    try:
        spec = importlib.util.spec_from_file_location(f'asset_{ident}', Path(root, 'assets', f'{ident}.py'))
        asset = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(asset)
        asset.build(entry, collection)
        bpy.context.view_layer.active_layer_collection = layers
        made = set(bpy.data.collections) - collections
        for child in made & set(scene.collection.children):
            scene.collection.children.unlink(child)
            if child.name not in collection.children:
                collection.children.link(child)
        for obj in set(scene.collection.objects) - objects:
            scene.collection.objects.unlink(obj)
            if obj.name not in collection.objects:
                collection.objects.link(obj)
        scene.collection.children.unlink(collection)
        anchor = bpy.data.objects.new(f'placed {ident}', None)
        anchor['placed_id'] = ident
        anchor.instance_type = 'COLLECTION'
        anchor.instance_collection = collection
        scene.collection.objects.link(anchor)
        anchor.matrix_world = frame_matrix(entry['spatial_contract']['frame'])
    except BaseException:
        bpy.context.view_layer.active_layer_collection = layers
        for obj in set(bpy.data.objects) - objects:
            bpy.data.objects.remove(obj)
        for made in set(bpy.data.collections) - collections | {collection}:
            bpy.data.collections.remove(made)
        raise
    bpy.context.view_layer.update()
    return anchor


def place_all(root):
    errors = {}
    for entry in json.loads(Path(root, 'state', 'objects.json').read_text()):
        try:
            place(root, entry)
        except BaseException:
            errors[entry['id']] = 'asset build failed during placement: ' + traceback.format_exc(limit=-3)[-1500:]
    bpy.context.scene['placement_errors'] = json.dumps(errors)


def region_of(obj):
    while obj is not None:
        if 'spatial_region' in obj:
            return str(obj['spatial_region'])
        obj = obj.parent
    return None


def geometry(anchor, depsgraph):
    for instance in depsgraph.object_instances:
        owner = instance.object.original
        if not instance.is_instance or instance.parent.original != anchor or instance.object.type not in GEOMETRY_TYPES:
            continue
        matrix = numpy.array(instance.matrix_world)
        mesh = instance.object.to_mesh()
        try:
            local = numpy.empty(len(mesh.vertices) * 3)
            mesh.vertices.foreach_get('co', local)
            mesh.calc_loop_triangles()
            corners = numpy.empty(len(mesh.loop_triangles) * 3, dtype=numpy.int64)
            mesh.loop_triangles.foreach_get('vertices', corners)
        finally:
            instance.object.to_mesh_clear()
        if len(local):
            yield owner, local.reshape(-1, 3) @ matrix[:3, :3].T + matrix[:3, 3], corners.reshape(-1, 3)


def merge(runs):
    key = runs[:, 0] * SHIFT + SHIFT // 2
    start, end = key + runs[:, 1], key + runs[:, 2]
    order = numpy.argsort(start, kind='stable')
    start, end = start[order], end[order]
    reach = numpy.maximum.accumulate(end)
    first = numpy.flatnonzero(numpy.concatenate([[True], start[1:] > reach[:-1] + 1]))
    start, end = start[first], numpy.maximum.reduceat(end, first)
    row = start // SHIFT
    return numpy.stack([row, start - row * SHIFT - SHIFT // 2, end - row * SHIFT - SHIFT // 2], axis=1)


def cover(triangles):
    rows = numpy.floor(triangles[:, :, 1] / CELL).astype(numpy.int64)
    low, counts = rows.min(axis=1), rows.max(axis=1) - rows.min(axis=1) + 1
    runs = numpy.empty((0, 3), dtype=numpy.int64)
    ends = numpy.cumsum(counts)
    begin = 0
    while begin < len(triangles):
        stop = max(begin + 1, int(numpy.searchsorted(ends, (ends[begin - 1] if begin else 0) + CHUNK, side='right')))
        part, count = triangles[begin:stop], counts[begin:stop]
        which = numpy.repeat(numpy.arange(len(part)), count)
        row = low[begin:stop][which] + numpy.arange(len(which)) - numpy.repeat(numpy.cumsum(count) - count, count)
        bottom, top = row * CELL, (row + 1) * CELL
        xmin, xmax = numpy.full(len(row), numpy.inf), numpy.full(len(row), -numpy.inf)
        for a, b in ((0, 1), (1, 2), (2, 0)):
            p, q = part[which, a], part[which, b]
            p, q = numpy.where(p[:, 1:] <= q[:, 1:], p, q), numpy.where(p[:, 1:] <= q[:, 1:], q, p)
            lo, hi = numpy.maximum(bottom, p[:, 1]), numpy.minimum(top, q[:, 1])
            rise = q[:, 1] - p[:, 1]
            flat = rise <= 0
            safe = numpy.where(flat, 1, rise)
            for y, default in ((lo, 0), (hi, 1)):
                x = p[:, 0] + numpy.where(flat, default, numpy.clip((y - p[:, 1]) / safe, 0, 1)) * (q[:, 0] - p[:, 0])
                x = numpy.where(lo <= hi, x, numpy.nan)
                xmin, xmax = numpy.fmin(xmin, x), numpy.fmax(xmax, x)
        found = numpy.stack([row, numpy.floor(xmin / CELL).astype(numpy.int64), numpy.floor(xmax / CELL).astype(numpy.int64)], axis=1)
        runs = merge(numpy.concatenate([runs, found]))
        begin = stop
    return runs


def measure(anchor, depsgraph):
    runs = numpy.empty((0, 3), dtype=numpy.int64)
    boxes = {}
    for owner, world, corners in geometry(anchor, depsgraph):
        if len(corners):
            runs = merge(numpy.concatenate([runs, cover(world[corners][:, :, :2])]))
        region = region_of(owner)
        if region is not None:
            lo, hi = world.min(axis=0), world.max(axis=0)
            if region in boxes:
                lo, hi = numpy.minimum(lo, boxes[region][0]), numpy.maximum(hi, boxes[region][1])
            boxes[region] = lo, hi
    front = anchor.matrix_world.col[1].xy.normalized()
    return {
        'front_xy': [round(front.x, 6), round(front.y, 6)],
        'regions': [{'id': region, 'bbox': {'min': lo.round(6).tolist(), 'max': hi.round(6).tolist()}} for region, (lo, hi) in boxes.items()],
        'coverage': {'cell': CELL, 'runs': runs.tolist()},
    }


def rendered_depsgraph():
    for item in [*bpy.data.objects, *bpy.data.collections]:
        item.hide_viewport = item.hide_render
    return bpy.context.evaluated_depsgraph_get()


def measure_scene(blend, output):
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    depsgraph = rendered_depsgraph()
    measured = {ident: {'error': error} for ident, error in json.loads(bpy.context.scene.get('placement_errors', '{}')).items()}
    for anchor in bpy.context.scene.objects:
        ident = anchor.get('placed_id')
        if ident is None:
            continue
        measured[ident] = {'error': 'was placed more than once'} if ident in measured else measure(anchor, depsgraph)
    Path(output).write_text(json.dumps(measured))


def place_alone(root, ident):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    return place(root, next(entry for entry in json.loads(Path(root, 'state', 'objects.json').read_text()) if entry['id'] == ident))


def measure_alone(root, ident, output):
    anchor = place_alone(root, ident)
    Path(output).write_text(json.dumps({ident: measure(anchor, rendered_depsgraph())}))


def preview(root, ident, output):
    anchor = place_alone(root, ident)
    worlds = [world for _, world, _ in geometry(anchor, bpy.context.evaluated_depsgraph_get())]
    if not worlds:
        raise SystemExit(f'{ident}: build created no geometry')
    lo = Vector([min(world.min(axis=0)[i] for world in worlds) for i in range(3)])
    hi = Vector([max(world.max(axis=0)[i] for world in worlds) for i in range(3)])
    centre, radius = (lo + hi) / 2, max((hi - lo).length / 2, 1e-3)
    front = anchor.matrix_world.col[1].xy.normalized()
    side = anchor.matrix_world.col[0].xy.normalized()
    direction = (front.to_3d() * math.cos(math.radians(35)) + side.to_3d() * math.sin(math.radians(35))).normalized()
    direction = (direction * math.cos(math.radians(20)) + Vector((0, 0, math.sin(math.radians(20))))).normalized()
    scene = bpy.context.scene
    camera = bpy.data.objects.new('preview camera', bpy.data.cameras.new('preview camera'))
    scene.collection.objects.link(camera)
    camera.location = centre + direction * radius * 1.15 / math.sin(camera.data.angle / 2)
    camera.rotation_euler = (centre - camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera.data.clip_end = max(100, radius * 10)
    scene.camera = camera
    sun = bpy.data.objects.new('preview sun', bpy.data.lights.new('preview sun', 'SUN'))
    sun.data.energy = 3
    key = direction.copy()
    key.rotate(Matrix.Rotation(math.radians(-50), 3, 'Z'))
    key.z += .8
    sun.rotation_euler = key.to_track_quat('Z', 'Y').to_euler()
    scene.collection.objects.link(sun)
    scene.world = bpy.data.worlds.new('preview world')
    scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.3, .3, .3, 1)
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 32
    scene.render.resolution_x = scene.render.resolution_y = 768
    scene.render.filepath = str(output)
    bpy.ops.render.render(write_still=True)


def main():
    mode, *args = sys.argv[sys.argv.index('--') + 1:]
    if mode == 'preview':
        preview(*args)
    elif mode == 'place':
        bpy.ops.wm.read_factory_settings(use_empty=True)
        place_all(args[0])
        bpy.ops.wm.save_as_mainfile(filepath=str(Path(args[1]).resolve()))
    elif mode == 'measure':
        measure_scene(*args)
    elif mode == 'measure-alone':
        measure_alone(*args)
    else:
        raise SystemExit(f'unknown mode {mode}; use preview ROOT ID PNG, place ROOT BLEND, measure BLEND JSON, or measure-alone ROOT ID JSON')


if __name__ == '__main__':
    main()
