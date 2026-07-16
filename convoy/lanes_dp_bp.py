"""
lanes_dp_bp.py -- generate lamination lanes filling the DP/BP band of the hedit harp.

    /home/james.clements/anaconda3/bin/python3 lanes_dp_bp.py

Reads  /home/james.clements/projects/paraguayan/paraguayan_overrides.json  READ-ONLY.
Writes, in this directory ONLY:  lanes_dp_bp.html, lanes_dp_bp.json, ladder.txt

red = BP (bulge / outer rail), green = DP (dimple / inner rail), per convoy.py's
vocabulary. See README.md for every judgement call.
"""

import json
import numpy as np
from shapely.geometry import LineString, Polygon

import convoy
import rails_json as rj
import seam as seam_mod

OUT_HTML = "lanes_dp_bp.html"
OUT_JSON = "lanes_dp_bp.json"
OUT_LADDER = "ladder.txt"
N = 500                      # correspondence samples per rail
ITERATIONS = (1, 2, 3, 4, 5)
SHIP = 3                     # dyadic: 2**n - 1 lanes. Re-derived, not assumed -- see README.


# ----------------------------------------------------------------- measurement --
def hf_residual(P):
    """Mean |P - [1,2,1]/4 smoothed P| in mm: how much high-frequency content the
    curve carries. Lesson 1 from the 3-D convoy work: lofted lanes can carry
    Nyquist sawtooth from the section generator (~7.3mm there vs ~1mm on the
    rails). MEASURE BEFORE SMOOTHING. A clean curve scores near 0 because a
    binomial pass barely moves it; sawtooth scores large."""
    S = convoy.smooth_closed(P)
    return float(np.mean(np.linalg.norm(S - P, axis=1)))


def min_lane_gap_near(lanes, pt, radius=60.0):
    """Smallest lane-to-lane distance, restricted to samples within `radius` of
    `pt` (the pinch). The pinch is what bounds lane count: 29.95mm of band cannot
    hold 7 lanes at HARP_PLAN's TOW_W=6."""
    best = np.inf
    for a in range(len(lanes)):
        A = lanes[a]
        A = A[np.linalg.norm(A - pt, axis=1) < radius]
        if not len(A):
            continue
        for b in range(a + 1, len(lanes)):
            B = lanes[b]
            B = B[np.linalg.norm(B - pt, axis=1) < radius]
            if not len(B):
                continue
            d = np.min(np.linalg.norm(A[:, None, :] - B[None, :, :], axis=2))
            best = min(best, d)
    return float(best)


def nesting_chain(lanes, DP, BP):
    """THE REAL ACCEPTANCE TEST. Returns (ok, rows).

    count_crossings is weak here, twice over:
      * shapely `.crosses()` is FALSE for touching / collinear-overlapping lines, so
        two TANGENT lanes score 0. CONVOY_ALGORITHM.md 5's standing rule ("0 is
        necessary, not sufficient") plus that blind spot means the count alone is
        close to meaningless for this build.
      * a lane that escaped the band entirely still scores 0 against its siblings.

    Because the seam trick (J2) makes every lane a CLOSED loop, we get a much
    stronger property to test than "did any two lanes cross": the whole family must
    form a strict containment chain

        BP > lane1 > lane2 > ... > laneM > DP

    with no touching. That subsumes crossings, tangency AND band containment in one
    check, and it is the actual physical requirement for a lamination: each ply
    nests inside the last. f increases toward green=DP, so lane order is outer->inner.
    """
    chain = [("BP", BP)] + [("lane%d" % k, P) for k, P in enumerate(lanes, 1)] + [("DP", DP)]
    rows, ok = [], True
    for (na, A), (nb, B) in zip(chain[:-1], chain[1:]):
        pa, pb = Polygon(A), Polygon(B)
        within = pb.within(pa)
        touches = LineString(B).touches(LineString(A))
        sep = float(pa.exterior.distance(pb.exterior))
        good = within and not touches
        ok &= good
        rows.append(dict(outer=na, inner=nb, within=bool(within),
                         touches=bool(touches), min_separation_mm=sep, ok=bool(good)))
    return ok, rows


# ----------------------------------------------------------------------- build --
def main():
    log = []
    def say(s=""):
        print(s)
        log.append(s)

    # 1. load + assert the premises. Do not trust them; measure them.
    DP, BP = rj.rail("DP"), rj.rail("BP")
    SP = rj.rail("SP")
    say("rails from paraguayan_overrides.json (read-only)")
    for nm, P in (("DP", DP), ("BP", BP), ("SP", SP)):
        a = rj.signed_area(P)
        say("  %s: %d samples  closure gap %.6f  area %.1f (%s)"
            % (nm, len(P), rj.closure_gap(P), a, "CW" if a < 0 else "CCW"))
        assert rj.closure_gap(P) < 1e-9, "%s not closed" % nm
        assert a < 0, "%s is not CW -- J2's co-traversal premise is void" % nm
    assert Polygon(DP).within(Polygon(BP)), "DP is not nested inside BP"
    say("  DP.within(BP): True")

    # 2. J3 self-test: both rails are CW, so co_orient should NOT reverse green.
    #    Verify the claim once rather than asserting it, then bypass co_orient in
    #    the driver (it costs 2 extra DTW solves).
    i_dp, j_bp, gap = seam_mod.mutual_nearest_seam(DP, BP)
    say("\nseam (mutual-nearest DP/BP pair, J2):")
    say("  DP[%d] = (%.2f, %.2f)   BP[%d] = (%.2f, %.2f)   gap = %.3f mm"
        % (i_dp, DP[i_dp][0], DP[i_dp][1], j_bp, BP[j_bp][0], BP[j_bp][1], gap))
    pinch = 0.5 * (DP[i_dp] + BP[j_bp])

    R = seam_mod.roll_open(BP, j_bp)       # red  = outer
    G = seam_mod.roll_open(DP, i_dp)       # green = inner

    chosen = convoy.co_orient(R, G)
    reversed_ = not np.allclose(chosen, G)
    say("\nJ3 self-test: co_orient(red=BP, green=DP) reversed green? %s" % reversed_)
    if reversed_:
        say("  !! co_orient DISAGREES with the CW measurement. J2's premise is void.")
        say("  !! Stopping. Do not ship lanes built on a premise the code denies.")
        return 1
    say("  matches the CW measurement -- bypassing co_orient in the loft (J3).")

    # 3. correspondence, once, reused across the whole ladder.
    Rs = convoy.resample(R, N)
    Gs = convoy.resample(G, N)
    Gp = convoy._apply_map(Gs, convoy.dtw_map(Rs, Gs))

    # 4. the ladder (J8). Do NOT assume iteration 3 is the ceiling: that ceiling is
    #    a property of the CLEMENTS frame's green head/tail reunion. DP/BP have
    #    different topology, so re-derive it.
    say("\nladder -- iteration: lanes, crossings, min pinch gap, max turn, seam turn, HF")
    rows = []
    for it in ITERATIONS:
        lanes = [convoy.loft(Rs, Gp, k / 2 ** it) for k in range(1, 2 ** it)]
        nx, hits = convoy.count_crossings(lanes)
        mg = min_lane_gap_near(lanes, pinch) if len(lanes) > 1 else float("nan")
        mt = max(seam_mod.max_turn_angle(P) for P in lanes)
        st = max(seam_mod.seam_turn_angle(P) for P in lanes)
        hf = max(hf_residual(P) for P in lanes)
        nest_ok, nest_rows = nesting_chain(lanes, DP, BP)
        sep = min(r["min_separation_mm"] for r in nest_rows)
        rows.append(dict(iteration=it, lanes=len(lanes), crossings=nx,
                         crossing_pairs=hits[:8], min_pinch_gap=mg, max_turn=mt,
                         seam_turn=st, hf_residual=hf, nesting_ok=nest_ok,
                         min_separation_mm=sep))
        say("  iter %d: %2d lanes  %2d crossings  pinch %6.2f mm  turn %5.2f deg  "
            "seam %5.2f deg  HF %.4f mm  nesting %s"
            % (it, len(lanes), nx, mg, mt, st, hf,
               "PASS" if nest_ok else "FAIL %s"
               % ([(r["outer"], r["inner"]) for r in nest_rows if not r["ok"]][:3],)))
        if hits:
            say("        crossing pairs (1-based): %s" % (hits[:8],))

    # 5. ship iteration=SHIP.
    lanes = [convoy.loft(Rs, Gp, k / 2 ** SHIP) for k in range(1, 2 ** SHIP)]
    nx, hits = convoy.count_crossings(lanes)
    hf = max(hf_residual(P) for P in lanes)
    hf_rails = max(hf_residual(DP), hf_residual(BP))

    # SMOOTHING IS CONDITIONAL. Measure first (task requirement + lesson 1).
    HF_TRIGGER = 3.0    # mm. Rails sit ~1mm; the 3-D sawtooth sat ~7.3mm.
    smoothed = hf > HF_TRIGGER
    say("\nHF residual: lanes max %.4f mm vs rails %.4f mm  (trigger %.1f mm)"
        % (hf, hf_rails, HF_TRIGGER))
    if smoothed:
        seam_before = max(seam_mod.seam_turn_angle(P) for P in lanes)
        lanes = [convoy.smooth_closed(P) for P in lanes]
        say("  -> sawtooth present: applied circular [1,2,1]/4. seam turn %.2f -> %.2f deg"
            % (seam_before, max(seam_mod.seam_turn_angle(P) for P in lanes)))
        nx, hits = convoy.count_crossings(lanes)
    else:
        say("  -> NO sawtooth. Smoothing NOT applied (lanes are lofts of clean")
        say("     Bezier rails; nothing here generates Nyquist content).")

    # 6. acceptance -- 0 crossings is necessary, NOT sufficient (CONVOY_ALGORITHM.md 5).
    closes = max(float(np.linalg.norm(P[-1] - P[0])) for P in lanes)
    nest_ok, nest_rows = nesting_chain(lanes, DP, BP)
    seam_t = max(seam_mod.seam_turn_angle(P) for P in lanes)
    say("\nacceptance for the shipped iteration=%d (%d lanes):" % (SHIP, len(lanes)))
    say("  crossings (count_crossings)     : %d %s   <- necessary, NOT sufficient" % (nx, hits[:8]))
    say("  every lane closed (max seam gap): %.2e mm" % closes)
    say("  max seam turn                   : %.2f deg" % seam_t)
    say("  min lane gap at the pinch       : %.2f mm" % min_lane_gap_near(lanes, pinch))
    say("  STRICT NESTING CHAIN            : %s" % ("PASS" if nest_ok else "FAIL"))
    for r in nest_rows:
        say("    %-6s > %-6s  within=%-5s touches=%-5s  min sep %6.3f mm  %s"
            % (r["outer"], r["inner"], r["within"], r["touches"],
               r["min_separation_mm"], "ok" if r["ok"] else "FAIL"))
    say("  render                          : %s -- LOOK AT IT" % OUT_HTML)
    accepted = (nx == 0) and nest_ok and closes < 1e-9

    # 7. emit. Sidecar only: never paraguayan_overrides.json.
    write_html(lanes, DP, BP, SP, hits, pinch, rows, nx, smoothed)
    meta = dict(
        _comment="Lamination lanes for the DP/BP band. GENERATED by "
                 "hedit/convoy/lanes_dp_bp.py from paraguayan_overrides.json. "
                 "SIDECAR -- not merged into the overrides; paraguayan_server.py's "
                 "merge against a new top-level key is UNVERIFIED. Y-up mm.",
        source="/home/james.clements/projects/paraguayan/paraguayan_overrides.json",
        seam=dict(dp_index=i_dp, bp_index=j_bp, gap_mm=gap,
                  dp_point=list(map(float, DP[i_dp])), bp_point=list(map(float, BP[j_bp]))),
        iteration=SHIP, smoothing_applied=bool(smoothed),
        crossings=nx, crossing_pairs=hits,
        accepted=bool(accepted),
        acceptance=dict(
            note="0 crossings is necessary, NOT sufficient (CONVOY_ALGORITHM.md 5). "
                 "shapely .crosses() is False for tangent lines, so the real test is "
                 "the strict nesting chain BP > lane1 > ... > laneM > DP.",
            crossings=nx, nesting_chain_ok=bool(nest_ok),
            max_seam_gap_mm=closes, max_seam_turn_deg=seam_t,
            nesting=nest_rows),
        ladder=rows,
        LANES=[dict(closed=True, fraction=(k + 1) / 2 ** SHIP,
                    polyline=[[round(float(x), 4), round(float(y), 4)] for x, y in P])
               for k, P in enumerate(lanes)],
    )
    with open(OUT_JSON, "w") as f:
        json.dump(meta, f, indent=1)
    with open(OUT_LADDER, "w") as f:
        f.write("\n".join(log) + "\n")
    say("\nwrote %s, %s, %s" % (OUT_HTML, OUT_JSON, OUT_LADDER))
    return 0


# ---------------------------------------------------------------------- render --
def write_html(lanes, DP, BP, SP, hits, pinch, rows, nx, smoothed):
    """Self-contained, no CDN.

    Display flip: the JSON is Y-up (harp.js:13). SVG is y-down. We negate y so the
    render reads Y-UP like harp.svg -- the harp stands on its foot. NOTE
    hedit.html:4378 importHarpJSON writes JSON coords straight into `d` with NO
    flip, so anything eyeballed in that editor is vertically MIRRORED. Do not copy
    that.
    """
    def d(P):
        return "M " + " L ".join("%.2f,%.2f" % (x, -y) for x, y in P)

    allP = np.vstack([DP, BP])
    x0, x1 = allP[:, 0].min() - 40, allP[:, 0].max() + 40
    y0, y1 = (-allP[:, 1]).min() - 40, (-allP[:, 1]).max() + 40
    vb = "%.1f %.1f %.1f %.1f" % (x0, y0, x1 - x0, y1 - y0)

    body = [
        '<path d="%s" fill="none" stroke="#7c3aed" stroke-width="1.2" '
        'stroke-dasharray="9 7" opacity=".55"/>' % d(SP),
        '<path d="%s" fill="none" stroke="#dc2626" stroke-width="3"/>' % d(BP),
        '<path d="%s" fill="none" stroke="#2563eb" stroke-width="3"/>' % d(DP),
    ]
    for k, P in enumerate(lanes, 1):
        body.append('<path d="%s" fill="none" stroke="#0f766e" stroke-width="1.6" '
                    'opacity=".9"/>' % d(P))
    # seam overlay: one tick per lane at its seam sample.
    for P in lanes:
        body.append('<circle cx="%.2f" cy="%.2f" r="2.6" fill="none" '
                    'stroke="#f59e0b" stroke-width="1.2"/>' % (P[0][0], -P[0][1]))
    body.append('<circle cx="%.2f" cy="%.2f" r="14" fill="none" stroke="#f59e0b" '
                'stroke-width="1.6" stroke-dasharray="4 3"/>' % (pinch[0], -pinch[1]))
    body.append('<text x="%.2f" y="%.2f" font-size="13" fill="#b45309">pinch / seam'
                '</text>' % (pinch[0] + 18, -pinch[1]))
    # crossings, if any, as marked dots.
    for a, b in hits:
        A, B = LineString(lanes[a - 1]), LineString(lanes[b - 1])
        g = A.intersection(B)
        for pt in (list(g.geoms) if hasattr(g, "geoms") else [g]):
            if pt.geom_type == "Point":
                body.append('<circle cx="%.2f" cy="%.2f" r="9" fill="none" '
                            'stroke="#ef4444" stroke-width="2.5"/>' % (pt.x, pt.y))

    lad = "".join(
        "<tr><td>%d</td><td>%d</td><td class='%s'>%d</td><td class='%s'>%s</td>"
        "<td>%.2f</td><td>%.2f</td><td>%.2f</td><td>%.3f</td></tr>"
        % (r["iteration"], r["lanes"], "ok" if r["crossings"] == 0 else "bad",
           r["crossings"], "ok" if r["nesting_ok"] else "bad",
           "nested" if r["nesting_ok"] else "FAIL",
           r["min_pinch_gap"], r["max_turn"], r["seam_turn"],
           r["hf_residual"]) for r in rows)

    seam_t = max(seam_mod.seam_turn_angle(P) for P in lanes)
    mg = min_lane_gap_near(lanes, pinch)
    mt = max(seam_mod.max_turn_angle(P) for P in lanes)
    nest_ok, _ = nesting_chain(lanes, DP, BP)
    hdr = ("%d lanes &middot; <b class='%s'>%d crossings</b> &middot; "
           "<b class='%s'>nesting %s</b> &middot; pinch gap %.2f mm "
           "&middot; max turn %.2f&deg; &middot; seam turn %.2f&deg; &middot; smoothing: %s"
           % (len(lanes), "ok" if nx == 0 else "bad", nx,
              "ok" if nest_ok else "bad", "PASS" if nest_ok else "FAIL",
              mg, mt, seam_t,
              "applied" if smoothed else "not applied (no sawtooth measured)"))

    html = """<!doctype html><html><head><meta charset="utf-8">
<title>hedit convoy -- DP/BP lamination lanes</title><style>
html,body{margin:0;height:100%;background:#f4f4f2;font:13px system-ui}
#wrap{position:absolute;inset:0;overflow:hidden;cursor:grab}#wrap.drag{cursor:grabbing}
svg{width:100%;height:100%;touch-action:none}
#t{position:fixed;top:8px;left:10px;color:#222;background:#ffffffd8;padding:7px 11px;
   border-radius:7px;border:1px solid #ddd;max-width:62%}
#l{position:fixed;bottom:8px;left:10px;background:#ffffffd8;padding:7px 11px;
   border-radius:7px;border:1px solid #ddd}
table{border-collapse:collapse;font:11px ui-monospace,monospace}
td,th{padding:1px 7px;text-align:right;border-bottom:1px solid #eee}
.ok{color:#047857}.bad{color:#dc2626;font-weight:700}
#k{position:fixed;top:8px;right:8px;background:#ffffffd8;padding:7px 11px;
   border-radius:7px;border:1px solid #ddd}
button{background:#1b1b1d;color:#eee;border:1px solid #555;border-radius:6px;padding:4px 10px}
</style></head><body>
<div id="t"><b>DP/BP lamination lanes</b> &mdash; __HDR__
<div style="color:#666;margin-top:4px">Y-up (harp stands on its foot).
<span style="color:#2563eb">DP inner</span> &middot;
<span style="color:#dc2626">BP outer</span> &middot;
<span style="color:#7c3aed">SP spine (reference)</span> &middot;
<span style="color:#0f766e">lanes</span> &middot;
<span style="color:#b45309">seam ticks</span></div></div>
<div id="l"><table><tr><th>iter</th><th>lanes</th><th>cross</th><th>nesting</th>
<th>pinch</th><th>turn</th><th>seam</th><th>HF</th></tr>__LAD__</table>
<div style="color:#666;margin-top:4px;max-width:340px">nesting = strict chain
BP&gt;lane1&gt;..&gt;DP, no touching. The real test: .crosses() is blind to tangency.</div></div>
<div id="k"><button id="rst">reset</button></div>
<div id="wrap"><svg viewBox="__VB__">__BODY__</svg></div><script>
var s=document.querySelector('svg');
var B={x:__X0__,y:__Y0__,w:__W__,h:__H__},V=Object.assign({},B);
function A(){s.setAttribute('viewBox',V.x+' '+V.y+' '+V.w+' '+V.h)}A();
var w=document.getElementById('wrap'),dg=0,px,py;
w.onmousedown=function(e){dg=1;px=e.clientX;py=e.clientY;w.classList.add('drag')};
onmouseup=function(){dg=0;w.classList.remove('drag')};
onmousemove=function(e){if(!dg)return;var r=w.getBoundingClientRect();
 V.x-=(e.clientX-px)*V.w/r.width;V.y-=(e.clientY-py)*V.h/r.height;px=e.clientX;py=e.clientY;A()};
w.addEventListener('wheel',function(e){e.preventDefault();var r=w.getBoundingClientRect(),
 mx=V.x+(e.clientX-r.left)/r.width*V.w,my=V.y+(e.clientY-r.top)/r.height*V.h,
 f=e.deltaY<0?.86:1.16;V.x=mx-(mx-V.x)*f;V.y=my-(my-V.y)*f;V.w*=f;V.h*=f;A()},{passive:false});
document.getElementById('rst').onclick=function(){V=Object.assign({},B);A()};
</script></body></html>"""
    html = (html.replace("__HDR__", hdr).replace("__LAD__", lad)
                .replace("__VB__", vb).replace("__X0__", "%.1f" % x0)
                .replace("__Y0__", "%.1f" % y0).replace("__W__", "%.1f" % (x1 - x0))
                .replace("__H__", "%.1f" % (y1 - y0))
                .replace("__BODY__", "\n".join(body)))
    with open(OUT_HTML, "w") as f:
        f.write(html)


if __name__ == "__main__":
    raise SystemExit(main())
