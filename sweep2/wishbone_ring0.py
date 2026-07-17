"""
wishbone_ring0.py — split the authored floor (base.svg) into the two wishbone arm
ring-0 cross-sections. First geometry step of the base→arms branch.

The base footprint (soundbox limaçon ∪ 12-flute rose, joined at the reunion) is one
closed loop. Just above the floor it branches: right lobe → arm A (soundbox), left
lobe → arm B (pillar/rose). This cuts at the authored reunion plane x = XSPLIT and
closes each lobe across the seam, giving two clean closed ring-0 loops.

Run:  python3 wishbone_ring0.py base.svg.txt
(needs core.py in the same dir for _flatten; numpy.)
"""
import sys, re, numpy as np
import core   # core._flatten parses base.svg's relative+cubic path correctly

XSPLIT = 80.0   # authored reunion plane (decision: between rose center ~28 and soundbox ~113)

def load(path, idv):
    s = open(path).read()
    i = s.index('id="%s"' % idv); ps = s.rfind('<path', 0, i)
    pe = s.index('/>', i) if '/>' in s[i:i+9000] else s.index('>', i)
    return core._flatten(re.search(r'\sd="([^"]*)"', s[ps:pe]).group(1))

def split_lobe(P, xs, keep):
    """Largest contiguous run on the keep side, closed with a straight seam at x=xs."""
    side = (P[:, 0] > xs) if keep == 'right' else (P[:, 0] < xs)
    idx = np.where(side)[0]
    runs, cur = [], [idx[0]]
    for a, b in zip(idx[:-1], idx[1:]):
        if b == a + 1:
            cur.append(b)
        else:
            runs.append(cur); cur = [b]
    runs.append(cur)
    if side[0] and side[-1] and len(runs) > 1:            # wrap-around
        runs[0] = runs[-1] + runs[0]; runs.pop()
    run = max(runs, key=len); L = P[run]
    seam = np.array([[xs, L[-1][1]], [xs, L[0][1]]])       # close across the reunion
    return np.vstack([L, seam])

def area(L):
    Q = np.vstack([L, L[:1]])
    return 0.5 * abs(np.sum(Q[:-1, 0]*Q[1:, 1] - Q[1:, 0]*Q[:-1, 1]))

if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "base.svg.txt"
    red = load(src, "red_outer")
    A = split_lobe(red, XSPLIT, 'right')   # soundbox lobe -> arm A ring-0
    B = split_lobe(red, XSPLIT, 'left')    # rose lobe     -> arm B ring-0
    print("arm A (soundbox) ring-0: %d pts, closed, area %.0f mm^2" % (len(A), area(A)))
    print("arm B (rose)     ring-0: %d pts, closed, area %.0f mm^2" % (len(B), area(B)))
    # NEXT: sweep each up its spine, blend lobe->formula over ~2 stations (core.section_rings
    # / opened / the rose block in _frame_rings), then cap-and-bond the joints.
