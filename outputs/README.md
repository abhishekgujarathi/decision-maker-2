# Render Output Organization

- `full/` contains complete-product review renders from `render_cc01.py`.
- `isolate/<group>/` contains focused assembly renders from `isolate_cc01.py`.
- Each folder uses independent incrementing filenames such as `001.png`, `002.png`.
- Each isolated render also stores a matching JSON file with the group and camera framing metadata.

The first isolated `001.png` files were generated before the camera-unit calibration. The corrected focused renders are the `002.png` files.
