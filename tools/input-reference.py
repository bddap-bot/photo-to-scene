import argparse
import json
import shutil
from pathlib import Path


FIELDS = {'image', 'source_image', 'reference_image'}


def prepare(root, source):
    manifest = root / 'input.json'
    if manifest.exists():
        reference = json.loads(manifest.read_text())['image']
        bundled = resolve(root, reference)
        if source.read_bytes() != bundled.read_bytes():
            raise ValueError('input differs from the photograph already bound to this run')
    else:
        reference = 'input/reference' + source.suffix.lower()
        bundled = root / reference
        bundled.parent.mkdir(parents=True, exist_ok=True)
        if source != bundled.resolve():
            shutil.copyfile(source, bundled)
        manifest.write_text(json.dumps({'image': reference}) + '\n')
    return reference


def resolve(root, reference):
    path = Path(reference)
    if path.is_absolute() or '..' in path.parts:
        raise ValueError(f'image reference is not run-relative: {reference}')
    resolved = (root / path).resolve()
    if not resolved.is_relative_to(root.resolve()) or not resolved.is_file():
        raise ValueError(f'image reference is absent or outside the run: {reference}')
    return resolved


def normalize(root, source):
    reference = json.loads((root / 'input.json').read_text())['image']
    bundled = resolve(root, reference)

    def visit(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key in FIELDS and isinstance(item, str):
                    value[key] = reference if (root / item).resolve() in {source, bundled} else item
                    resolve(root, value[key])
                else:
                    visit(item)
        elif isinstance(value, list):
            for item in value:
                visit(item)

    paths = [root / 'state/floorplan.json', root / 'state/objects.json']
    paths.extend((root / 'state').glob('entry_*.json'))
    updates = []
    for path in paths:
        if path.exists():
            value = json.loads(path.read_text())
            visit(value)
            updates.append((path, json.dumps(value, indent=2) + '\n'))
    for path, content in updates:
        if path.read_text() != content:
            path.write_text(content)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['prepare', 'normalize'])
    parser.add_argument('root', type=Path)
    parser.add_argument('source', type=Path)
    args = parser.parse_args()
    try:
        if args.action == 'prepare':
            print(prepare(args.root.resolve(), args.source.resolve(strict=True)))
        else:
            normalize(args.root.resolve(), args.source.resolve(strict=True))
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f'input reference: {error}\n')


if __name__ == '__main__':
    main()
