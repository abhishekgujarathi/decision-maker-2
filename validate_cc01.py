"""Compatibility entrypoint: rebuild CC-01 and run the P0 validator."""
import importlib
import os
import sys

_candidates = []
if '__file__' in globals():
    _candidates.append(os.path.dirname(os.path.abspath(__file__)))
_candidates.extend([os.getcwd(), r'L:\coding\YOUTUBE\blenderr\code-python'])
ROOT = next((path for path in _candidates if os.path.isdir(os.path.join(path, 'src'))), _candidates[-1])
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

build_module = importlib.import_module('src.build')
build_module = importlib.reload(build_module)
build_module.build()
validate_module = importlib.import_module('src.validate')
validate_module = importlib.reload(validate_module)
result = validate_module.validate_scene()
if not result['passed']:
    raise SystemExit(1)
