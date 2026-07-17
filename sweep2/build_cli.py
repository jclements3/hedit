#!/usr/bin/env python3
"""One-command build for app integration:
    python3 build_cli.py harp_spec.json out_prefix
Writes:
    out_prefix.json  — rings/bores/base as JSON (viewer format)
    out_prefix.obj   — outer + bore + base surfaces as quad-strip OBJ meshes
Exit code nonzero (with a named error) if the frame orientation guard fails.
"""
import sys, json, numpy as np
import sweep2

def quads(rings, name, f, voff):
    S = len(rings); M = len(rings[0])
    for rg in rings:
        for x, y, z in rg:
            f.write("v %.3f %.3f %.3f\n" % (x, y, z))
    f.write("g %s\n" % name)
    for i in range(S - 1):
        for j in range(M):
            a = voff + i * M + j
            b = voff + i * M + (j + 1) % M
            c = voff + (i + 1) * M + (j + 1) % M
            d = voff + (i + 1) * M + j
            f.write("f %d %d %d %d\n" % (a + 1, b + 1, c + 1, d + 1))
    return voff + S * M

def main():
    spec, prefix = sys.argv[1], sys.argv[2]
    rings, bores, (bo, bi), meta = sweep2.wishbone_spec(spec)
    pack = lambda L: [np.round(np.asarray(r), 2).tolist() for r in L]
    json.dump(dict(S=len(rings), M=len(rings[0]), fam=meta["fam"], ZM=meta["ZM"],
                   outer=pack(rings), bore=pack(bores),
                   base_o=pack(bo), base_i=pack(bi)),
              open(prefix + ".json", "w"), separators=(",", ":"))
    with open(prefix + ".obj", "w") as f:
        v = 0
        v = quads(rings, "outer", f, v)
        v = quads(bores, "bore", f, v)
        v = quads(bo, "base_outer", f, v)
        v = quads(bi, "base_inner", f, v)
    print("wrote %s.json and %s.obj  (%d stations, ZM %.1f)" % (prefix, prefix, len(rings), meta["ZM"]))

if __name__ == "__main__":
    main()
