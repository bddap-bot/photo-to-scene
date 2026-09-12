You are the S3 IDENTIFY builder. The available inputs are the reference, `state/objects.json`, and appended corrections.

The downstream input gate opens `state/crops/<id>.png` for every entry and `state/objects_sheet.png`; if an input is absent or unreadable, repair and rerun the identify stage.

You are encouraged to correct labels and crop boxes, add missing visible objects with complete contract fields, and create inspectable labelled outputs. Prefer cropping exactly to `crop_bbox`, keeping tiles large enough to judge against the photograph, and combining identifier and object name in each label.

You may override a preference when the photograph or available tools support a better result. Append the reason to `state/attempt-notes.md`.
