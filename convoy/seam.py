"""
seam.py -- turn the CLOSED DP/BP loops into OPEN rails convoy.py can pair.

THE PROBLEM
-----------
convoy.build_convoy wants OPEN rails and pairs their endpoints: dtw_map anchors
g[0]=0 and g[-1]=m-1 (convoy.py:208-214). DP and BP are closed loops. Cut them at
an ARBITRARY pair of indices and that endpoint anchoring is not merely vestigial,
it is actively WRONG -- it force-pairs two points that have no reason to
correspond, and drags the whole warp map to reach them.

THE FIX (judgement call J2)
---------------------------
Cut both rails at the MUTUALLY-NEAREST DP/BP point pair -- the pinch where the
band is narrowest. Two properties make this the right cut and not just a cut:

  * It is DERIVED FROM THE GEOMETRY, not hand-frozen. HARP_PLAN.md warns DP/BP are
    OUTPUTS of paraguayan/harp.py, so any hardcoded index would rot the next time
    the rails are regenerated. A mutual-nearest search re-derives itself.
  * Nearest-point projection makes the two cuts CORRESPOND BY CONSTRUCTION. So
    dtw_map's endpoint anchor now pins the seam to the seam: it is CORRECT here,
    not a workaround.

Both rails are CW (measured, see README), so once rolled to a common seam they
co-traverse and no reversal is needed.

Consequence worth stating: every lofted lane is then itself a CLOSED loop nesting
between DP and BP -- which is what a lamination in a closed harp frame physically
IS. CONVOY_ALGORITHM.md 8.3's "closed->open topology change at the cusp" worry is
defused rather than worked around. (8.3 is unreliable generally; see README.)
"""

import numpy as np


def mutual_nearest_seam(A, B):
    """(i_a, j_b, gap): the globally-closest sample pair between polylines A and B.

    Brute force over the dense samples. This IS the mutual-nearest pair (a global
    argmin is mutual by definition), so no iterate-to-fixpoint step is needed.
    Sample-resolution, not exact-projection: A/B are ~600 samples over ~4000mm of
    rail, so the cut lands within a few tenths of a mm of the true pinch. That is
    well inside the tolerance that matters here -- the seam only needs to be the
    same PLACE on both rails, and being a sample makes the roll exact.
    """
    d = np.linalg.norm(A[:, None, :] - B[None, :, :], axis=2)
    i, j = np.unravel_index(int(np.argmin(d)), d.shape)
    return int(i), int(j), float(d[i, j])


def roll_open(P, i):
    """Closed loop P (P[-1] == P[0]) -> open rail starting AND ending at P[i].

    Drops the duplicate closing sample, rolls index i to the front, then appends
    P[i] again at the tail. The result traverses the whole loop exactly once and
    its two endpoints are the same physical point -- so a lane lofted from it is
    closed too.
    """
    Q = np.asarray(P, float)
    if np.allclose(Q[0], Q[-1]):
        Q = Q[:-1]
    R = np.roll(Q, -i, axis=0)
    return np.vstack([R, R[:1]])


def seam_turn_angle(P):
    """Turn angle (deg) AT the seam of a closed lane: the exterior angle between
    the last segment coming in and the first segment going out. 0 = C1 across the
    seam. This is the number the dtw_map endpoint taper cannot protect, because the
    taper disables smoothing exactly at index 0/-1."""
    v_in = P[-1] - P[-2]
    v_out = P[1] - P[0]
    a = np.arctan2(v_in[1], v_in[0])
    b = np.arctan2(v_out[1], v_out[0])
    return float(abs(np.degrees(np.arctan2(np.sin(b - a), np.cos(b - a)))))


def max_turn_angle(P):
    """Largest exterior turn (deg) anywhere along P. Kink detector."""
    V = np.diff(P, axis=0)
    ang = np.arctan2(V[:, 1], V[:, 0])
    d = np.diff(ang)
    d = np.degrees(np.arctan2(np.sin(d), np.cos(d)))
    return float(np.max(np.abs(d))) if len(d) else 0.0
