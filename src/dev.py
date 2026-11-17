"""Developer helper: reload every CC-01 module, rebuild, and run checks.

    import src.dev as dev; dev.rebuild()
"""
import importlib
import sys

MODULES = ['src.config', 'src.core', 'src.paths', 'src.materials', 'src.scene', 'src.build', 'src.refine_check']


def reload_all():
    for name in MODULES:
        if name in sys.modules:
            importlib.reload(sys.modules[name])
        else:
            importlib.import_module(name)


def rebuild(check=True, skip=()):
    reload_all()
    sys.modules['src.build'].build()
    if check:
        return summary(sys.modules['src.refine_check'].run(skip=skip))


def summary(res):
    v2 = res.get('V02_intersections', {})
    fl = res.get('V05_floating', {})
    return {
        'glass': res.get('V06_glass'),
        'ball': {k: v for k, v in res.get('V01_ball_sweep', {}).items() if k != 'worst'},
        'ball_worst': res.get('V01_ball_sweep', {}).get('worst', [])[:6],
        'unintended': len(v2.get('unintended', [])),
        'floating_components': len(fl.get('floating', [])),
    }
