import argparse
import hashlib
import json
import pathlib
import urllib.request


def nested(data, selector):
    for part in selector.split("."):
        data = data[part]
    return data


parser = argparse.ArgumentParser()
parser.add_argument("asset")
parser.add_argument("selectors", nargs="+")
parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path("."))
args = parser.parse_args()
manifest_url = f"https://api.polyhaven.com/files/{args.asset}"
with urllib.request.urlopen(manifest_url) as response:
    manifest = json.load(response)
manifest_dir = args.root / "manifests"
texture_dir = args.root / "textures"
manifest_dir.mkdir(parents=True, exist_ok=True)
texture_dir.mkdir(parents=True, exist_ok=True)
manifest_path = manifest_dir / f"{args.asset}.files.json"
manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
for selector in args.selectors:
    record = nested(manifest, selector)
    url = record["url"]
    target = texture_dir / pathlib.PurePosixPath(url).name
    with urllib.request.urlopen(url) as response, target.open("wb") as output:
        while chunk := response.read(1024 * 1024):
            output.write(chunk)
    expected = record.get("md5")
    if expected and hashlib.md5(target.read_bytes()).hexdigest() != expected:
        target.unlink()
        raise SystemExit(f"checksum mismatch: {target}")
    print(target)
