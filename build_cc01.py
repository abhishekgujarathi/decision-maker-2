"""Compatibility entrypoint for the modular CC-01 builder."""
import os
import sys

_candidates = []
if '__file__' in globals():
    _candidates.append(os.path.dirname(os.path.abspath(__file__)))
_candidates.extend([os.getcwd(), r'L:\coding\YOUTUBE\blenderr\code-python'])
ROOT = next((path for path in _candidates if os.path.isdir(os.path.join(path, 'src'))), _candidates[-1])
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import importlib
_build_module = importlib.import_module('src.build')
_build_module = importlib.reload(_build_module)
build = _build_module.build

if __name__ == '__main__':
    build()
