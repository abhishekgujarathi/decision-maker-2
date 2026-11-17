"""Shared, smooth front-elevation paths used by the builder and validators."""
import math
from .config import TRACK_Z, TURN_R, BALL_Z

def path_line(a, b, count=12):
    return [(a[0]+(b[0]-a[0])*i/(count-1),
             a[1]+(b[1]-a[1])*i/(count-1),
             a[2]+(b[2]-a[2])*i/(count-1)) for i in range(count)]

def arc(center, radius, start, end, count=24):
    return [(center[0]+radius*math.cos(start+(end-start)*i/(count-1)),
             center[1]+radius*math.sin(start+(end-start)*i/(count-1)), center[2]) for i in range(count)]


def cubic_bezier(a, b, c, d, count=24):
    """Sample a cubic Bezier in the local front-elevation plane."""
    points=[]
    for i in range(count):
        t=i/(count-1)
        u=1.0-t
        points.append(tuple(
            u**3*a[index] + 3*u*u*t*b[index] + 3*u*t*t*c[index] + t**3*d[index]
            for index in range(3)
        ))
    return points

def track_centerline():
    """Return the reference-style continuous centerline with three U-turns."""
    p=[]
    # The launch cradle hands off at (-130, 590), leaving the vertical drop
    # clear of Run 01 instead of burying its first 15 mm inside the channel.
    p += path_line((-130,590,TRACK_Z),(145,560,TRACK_Z),28)
    p += arc((145,530,TRACK_Z),TURN_R,math.pi/2,-math.pi/2,24)[1:]
    p += path_line((145,500,TRACK_Z),(-145,470,TRACK_Z),28)[1:]
    p += arc((-145,440,TRACK_Z),TURN_R,math.pi/2,3*math.pi/2,24)[1:]
    p += path_line((-145,410,TRACK_Z),(145,380,TRACK_Z),28)[1:]
    # The lower reference route turns back right-to-left through a third
    # 30 mm U-turn before entering the selector. This keeps the exit guide
    # clear of the preceding run instead of folding diagonally underneath it.
    p += arc((145,350,TRACK_Z),TURN_R,math.pi/2,-math.pi/2,24)[1:]
    p += path_line((145,320,TRACK_Z),(20,330,TRACK_Z),18)[1:]
    return p


def selector_branch_paths(plane='track'):
    """Return the two non-crossing centreline branches into the output pockets.

    plane='track' gives the floor mid-plane (used to build channels);
    plane='ball' gives the ball-centre plane (used for the ball path).
    """
    z = BALL_Z if plane == 'ball' else TRACK_Z
    # The exit guide ends above the selector. A short drop reaches the pivot
    # datum, then the two routes split below the apex with a real clearance
    # gap instead of overlapping the guide and each other.
    return {
        'YES': path_line((20, 315, z), (2, 310, z), 4) + path_line((2, 310, z), (-78, 245, z), 18)[1:],
        'NO': path_line((20, 315, z), (38, 310, z), 4) + path_line((38, 310, z), (78, 245, z), 18)[1:],
    }


def selector_drop_path(plane='track'):
    """Shared vertical drop from the exit guide to the selector pivot datum."""
    z = BALL_Z if plane == 'ball' else TRACK_Z
    return path_line((20, 330, z), (20, 315, z), 5)


def to_ball_plane(points):
    """Re-seat a track-plane polyline onto the ball-centre plane."""
    return [(p[0], p[1], BALL_Z) for p in points]


def full_ball_path():
    """Return the input-to-selector path, including both selector branches."""
    input_lead = path_line((-145, 638, BALL_Z), (-145, 602, BALL_Z), 8)
    input_lead += path_line((-145, 602, BALL_Z), (-130, 590, BALL_Z), 5)[1:]
    return {
        'INPUT_TO_SELECTOR': input_lead + to_ball_plane(track_centerline()[1:]),
        'YES': selector_drop_path('ball') + selector_branch_paths('ball')['YES'][1:],
        'NO': selector_drop_path('ball') + selector_branch_paths('ball')['NO'][1:],
    }
