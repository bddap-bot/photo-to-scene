import importlib.util
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('input_reference', REPO / 'tools/input-reference.py')
REFERENCE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REFERENCE)


class InputReferenceTest(unittest.TestCase):
    def test_absolute_input_contracts_survive_move_and_driver_consumption(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            source = base / 'external photo.ppm'
            source.write_bytes(b'P6\n1 1\n255\n\x80\x80\x80')
            root = base / 'original run'
            binaries = base / 'bin'
            binaries.mkdir()
            nix = binaries / 'nix-shell'
            nix.write_text('#!/usr/bin/env bash\nexec bash -c "$4"\n')
            nix.chmod(0o755)
            codex = binaries / 'codex'
            codex.write_text('''#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
args = sys.argv
root = Path(args[args.index('-C') + 1])
photo = Path(args[args.index('-i') + 1])
prompt = sys.stdin.read()
assert 'input/reference.ppm' in prompt
assert photo.read_bytes() == b'P6\\n1 1\\n255\\n\\x80\\x80\\x80'
if os.environ['PHASE'] == 'produce':
    (root / 'state/floorplan.json').write_text(json.dumps({'reference_image': str(photo)}))
    entry = {'id': 'neutral', 'image': str(photo), 'spatial_contract': {
        'source_evidence': [{'source_image': str(photo), 'points': [{'image': str(photo)}]}]},
        'crop': {'image': 'state/crops/neutral.ppm'}}
    (root / 'state/crops/neutral.ppm').write_bytes(photo.read_bytes())
    (root / 'state/objects.json').write_text(json.dumps([entry]))
    (root / 'state/entry_neutral.json').write_text(json.dumps(entry))
else:
    def consume(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key in {'image', 'source_image', 'reference_image'}:
                    assert not Path(item).is_absolute()
                    assert (root / item).read_bytes() == photo.read_bytes()
                else:
                    consume(item)
        elif isinstance(value, list):
            for item in value:
                consume(item)
    for path in (root / 'state').glob('*.json'):
        consume(json.loads(path.read_text()))
    (root / 'consumed').touch()
''')
            codex.chmod(0o755)
            driver = base / 'driver.sh'
            prefix = (REPO / 'pipeline.sh').read_text().split('\nfeedback=\ncurrent=', 1)[0]
            prefix = prefix.replace('PIPELINE_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)',
                                    f'PIPELINE_DIR={shlex.quote(str(REPO))}')
            export = (REPO / 'pipeline.sh').read_text().split('\ncp "$STATE/best_render.png"', 1)[1]
            driver.write_text(prefix + '\nbuilder floorplan_builder.md "" -i "$INPUT"\n'
                              + 'touch "$STATE/best_render.png" "$STATE/side_by_side.png" '
                              + '"$STATE/objects_sheet.png" "$STATE/scores.md"\n'
                              + 'cp "$STATE/best_render.png"' + export)
            env = {**os.environ, 'PATH': f'{binaries}:{os.environ["PATH"]}',
                   'PHOTO_TO_SCENE_ROOT': str(root), 'BOTQ_ARTIFACTS_DIR': str(root / 'artifacts'),
                   'PHASE': 'produce'}

            def run(photo):
                return subprocess.run(['bash', str(driver), str(photo)], env=env,
                                      text=True, capture_output=True, timeout=30)

            result = run(source)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            contracts = {p.name: p.read_bytes() for p in (root / 'state').glob('*.json')}
            self.assertEqual(json.loads(contracts['floorplan.json'])['reference_image'], 'input/reference.ppm')
            for content in contracts.values():
                self.assertNotIn(str(base).encode(), content)
            published = base / 'published'
            shutil.move(root / 'artifacts', published)
            ref = json.loads((published / 'floorplan.json').read_text())['reference_image']
            self.assertEqual((published / ref).read_bytes(), source.read_bytes())
            self.assertEqual(json.loads((published / 'input.json').read_text())['image'], ref)
            self.assertEqual((published / 'objects.json').read_bytes(), contracts['objects.json'])
            moved = base / 'moved run'
            shutil.move(root, moved)
            source.unlink()
            env.update(PHASE='consume', PHOTO_TO_SCENE_ROOT=str(moved),
                       BOTQ_ARTIFACTS_DIR=str(moved / 'artifacts'))
            result = run(moved / 'input/reference.ppm')
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((moved / 'consumed').exists())
            self.assertEqual(contracts, {p.name: p.read_bytes() for p in (moved / 'state').glob('*.json')})
            replacement = base / 'different.ppm'
            replacement.write_bytes(b'different')
            result = run(replacement)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('input differs', result.stderr)

    def test_same_basename_derived_image_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            source = base / 'photo.ppm'
            source.write_bytes(b'input')
            root = base / 'run'
            REFERENCE.prepare(root, source)
            (root / 'photo.ppm').write_bytes(b'derived')
            (root / 'state').mkdir()
            objects = root / 'state/objects.json'
            objects.write_text(json.dumps([{'image': 'photo.ppm', 'source_image': str(source)}]))
            REFERENCE.normalize(root, source)
            self.assertEqual(json.loads(objects.read_text()),
                             [{'image': 'photo.ppm', 'source_image': 'input/reference.ppm'}])

    def test_references_cannot_escape_or_name_missing_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for reference in ('/outside.ppm', '../outside.ppm', 'missing.ppm'):
                with self.subTest(reference=reference), self.assertRaises(ValueError):
                    REFERENCE.resolve(root, reference)
            (root / 'inside').mkdir()
            (root / 'outside.ppm').write_bytes(b'outside')
            (root / 'inside/escape').symlink_to(root)
            with self.assertRaises(ValueError):
                REFERENCE.resolve(root / 'inside', 'escape/outside.ppm')

    def test_unknown_absolute_reference_is_rejected_without_partial_rewrite(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'photo.ppm'
            source.write_bytes(b'neutral')
            REFERENCE.prepare(root, source)
            (root / 'state').mkdir()
            floorplan = root / 'state/floorplan.json'
            floorplan.write_text(json.dumps({'reference_image': str(source)}))
            objects = root / 'state/objects.json'
            objects.write_text(json.dumps([{'source_image': '/unavailable.ppm'}]))
            before = floorplan.read_bytes()
            with self.assertRaises(ValueError):
                REFERENCE.normalize(root, source)
            self.assertEqual(before, floorplan.read_bytes())


if __name__ == '__main__':
    unittest.main()
