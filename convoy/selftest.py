"""
selftest.py -- pins the premises lanes_dp_bp.py relies on.

    /home/james.clements/anaconda3/bin/python3 selftest.py

These are the claims that, if they silently changed, would make the lanes wrong
while still LOOKING fine. DP/BP are OUTPUTS of paraguayan/harp.py (HARP_PLAN.md),
so they can be regenerated out from under this code at any time. Run this first
if anything looks off.
"""

import numpy as np
from shapely.geometry import Polygon

import convoy
import rails_json as rj
import seam as sm

ok = True


def check(name, cond, detail=""):
    global ok
    ok &= bool(cond)
    print("  %-52s %s  %s" % (name, "PASS" if cond else "FAIL", detail))


print("rails_json: handle semantics mirror harp.js:29-34")
# A one-segment open chain with known handles: p1 = p0+hout, p2 = p3+hin.
ch = {"closed": False, "nodes": [
    {"x": 0.0, "y": 0.0, "hin": {"dx": 0, "dy": 0}, "hout": {"dx": 10, "dy": 0}},
    {"x": 30.0, "y": 0.0, "hin": {"dx": -10, "dy": 0}, "hout": {"dx": 0, "dy": 0}}]}
segs = rj.chain_to_segments(ch)
check("handles are RELATIVE offsets (p1 = p0 + hout)",
      np.allclose(segs[0][1], [10, 0]), "got %s" % (segs[0][1],))
check("hin attaches to its OWN node (p2 = p3 + hin)",
      np.allclose(segs[0][2], [20, 0]), "got %s" % (segs[0][2],))

# closed:true must append the wrap segment last->first (harp.js:33).
sq = {"closed": True, "nodes": [
    {"x": 0, "y": 0, "hin": {"dx": 0, "dy": 0}, "hout": {"dx": 0, "dy": 0}},
    {"x": 10, "y": 0, "hin": {"dx": 0, "dy": 0}, "hout": {"dx": 0, "dy": 0}},
    {"x": 10, "y": 10, "hin": {"dx": 0, "dy": 0}, "hout": {"dx": 0, "dy": 0}}]}
check("closed:true appends the wrap segment last->first",
      len(rj.chain_to_segments(sq)) == 3, "%d segs for 3 nodes" % len(rj.chain_to_segments(sq)))
check("open chain does NOT wrap",
      len(rj.chain_to_segments(ch)) == 1)

print("\nrails_json: missing-handle guard")
try:
    rj.assert_full_handles({"nodes": [{"x": 0, "y": 0, "hout": {"dx": 1, "dy": 1}}]}, "T")
    check("assert_full_handles rejects a missing handle", False)
except AssertionError:
    check("assert_full_handles rejects a missing handle", True)

print("\nlive rails from paraguayan_overrides.json")
DP, BP, SP = rj.rail("DP"), rj.rail("BP"), rj.rail("SP")
for nm, P, n_expect in (("DP", DP, 9), ("BP", BP, 10), ("SP", SP, 9)):
    ch = rj.load_overrides()[nm]
    check("%s closed:true" % nm, ch["closed"] is True)
    check("%s node count == %d" % (nm, n_expect), len(ch["nodes"]) == n_expect,
          "got %d" % len(ch["nodes"]))
    check("%s closure gap == 0" % nm, rj.closure_gap(P) < 1e-9,
          "%.2e mm" % rj.closure_gap(P))
    check("%s is CW (J2 co-traversal premise)" % nm, rj.signed_area(P) < 0,
          "area %.1f" % rj.signed_area(P))
check("DP nested strictly inside BP", Polygon(DP).within(Polygon(BP)))
check("SP between DP and BP (reference only)",
      Polygon(DP).within(Polygon(SP)) and Polygon(SP).within(Polygon(BP)))

print("\nseam")
i, j, gap = sm.mutual_nearest_seam(DP, BP)
check("pinch gap ~29.95 mm", abs(gap - 29.95) < 0.5, "%.3f mm" % gap)
R = sm.roll_open(BP, j)
check("roll_open returns a CLOSED rail (P[-1] == P[0])",
      np.allclose(R[0], R[-1]))
check("roll_open starts at the requested sample", np.allclose(R[0], BP[j]))
check("roll_open preserves the sample count",
      len(R) == len(BP), "%d vs %d" % (len(R), len(BP)))
check("roll_open preserves arc length",
      abs(np.sum(np.linalg.norm(np.diff(R, axis=0), axis=1))
          - np.sum(np.linalg.norm(np.diff(BP, axis=0), axis=1))) < 1e-6)

print("\nconvoy vendor adaptations")
check("core._flatten import is GONE (J4)",
      "from core import" not in open("convoy.py").read().split('"""')[2])
# Adaptation 1: the parser must survive H/V, which core.py's regex does not.
P = convoy._flatten("M 0,0 H 10 V 20 L 30,40")
check("_flatten_local parses H/V without losing a point",
      len(P) == 4 and np.allclose(P[1], [10, 0]) and np.allclose(P[2], [10, 20]),
      "%d pts" % len(P))
# Adaptation 2: smoothing must be self-limiting on clean input and kill sawtooth.
t = np.linspace(0, 2 * np.pi, 200)
circle = np.c_[100 * np.cos(t), 100 * np.sin(t)]
circle[-1] = circle[0]
moved = np.max(np.linalg.norm(convoy.smooth_closed(circle) - circle, axis=1))
check("smooth_closed is self-limiting on clean input", moved < 1.0, "%.4f mm" % moved)
saw = circle.copy()
saw[:-1, 0] += 5.0 * (-1) ** np.arange(len(saw) - 1)      # Nyquist sawtooth
saw[-1] = saw[0]
before = np.max(np.abs(saw[:-1, 0] - circle[:-1, 0]))
after = np.max(np.abs(convoy.smooth_closed(saw)[:-1, 0] - circle[:-1, 0]))
check("smooth_closed kills Nyquist sawtooth", after < before * 0.5,
      "%.2f -> %.2f mm" % (before, after))
check("smooth_closed keeps the lane closed",
      np.allclose(convoy.smooth_closed(saw)[0], convoy.smooth_closed(saw)[-1]))

print("\nJ3: co_orient agrees with the CW measurement")
G = sm.roll_open(DP, i)
check("co_orient does NOT reverse green", np.allclose(convoy.co_orient(R, G), G))

print("\n%s" % ("ALL PASS" if ok else "FAILURES ABOVE"))
raise SystemExit(0 if ok else 1)
