import importlib.util
import json
import os
import sys
import traceback
from pathlib import Path

import bpy

IMAGE_SUFFIXES = {".bmp", ".exr", ".hdr", ".jpeg", ".jpg", ".png", ".tga", ".tif", ".tiff", ".webp"}
IMAGE_SOURCES = {"FILE", "MOVIE", "SEQUENCE", "TILED"}

asset, entry, own_arg, report = map(Path, sys.argv[sys.argv.index("--") + 1:])
own = own_arg.parent.resolve() / own_arg.name
opened: list[str] = []


def audit(event: str, args: tuple[object, ...]) -> None:
    if event == "open" and isinstance(args[0], (str, bytes, os.PathLike)):
        opened.append(os.fsdecode(args[0]))


sys.path.insert(0, str(asset.parent))
spec = importlib.util.spec_from_file_location(f"asset_{asset.stem}", asset)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.addaudithook(audit)
try:
    spec.loader.exec_module(module)
    module.build(json.loads(entry.read_text()))
except BaseException as error:
    report.write_text(json.dumps({"error": traceback.format_exception_only(error)[-1].strip(), "outside": []}) + "\n")
    sys.exit()
loaded = [image.filepath for image in bpy.data.images if image.source in IMAGE_SOURCES and image.filepath]
loaded += [path for path in opened if Path(path).suffix.lower() in IMAGE_SUFFIXES]
outside = sorted({path for path in loaded if not (os.path.isabs(path) and Path(path).resolve().is_relative_to(own))})
report.write_text(json.dumps({"error": None, "outside": outside}) + "\n")
