"""Compatibility entrypoint: rebuild and render CC-01 to outputs/001.png."""
import importlib
import os
import sys

_candidates = []
if '__file__' in globals():
    _candidates.append(os.path.dirname(os.path.abspath(__file__)))
_candidates.extend([os.getcwd(), r'L:\coding\YOUTUBE\blenderr\code-python'])
ROOT = next((path for path in _candidates if os.path.isdir(os.path.join(path, 'src'))), _candidates[-1])
if ROOT not in sys.path:
    sys.path.insert(0,ROOT)

build_module=importlib.import_module('src.build')
build_module=importlib.reload(build_module)
render_module=importlib.import_module('src.render')
render_module=importlib.reload(render_module)

build_module.build()
render_module.render_review(os.path.join(ROOT,'outputs','full'))
