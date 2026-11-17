"""Compatibility entrypoint for isolated CC-01 assembly builds/renders."""
import importlib
import os
import sys

_candidates = []
if '__file__' in globals():
    _candidates.append(os.path.dirname(os.path.abspath(__file__)))
_candidates.extend([os.getcwd(), r'L:\coding\YOUTUBE\blenderr\code-python'])
ROOT = next((path for path in _candidates if os.path.isdir(os.path.join(path, 'src'))), _candidates[-1])
if ROOT not in sys.path: sys.path.insert(0,ROOT)

module=importlib.import_module('src.isolate')
module=importlib.reload(module)
module.main()
