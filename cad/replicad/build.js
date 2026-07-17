#!/usr/bin/env node
// build.js — kernel-exact soundbox-arm solid + 2-D vector profiles via Replicad
// (OpenCascade WASM). Consumes the harp_spec.json that hedit's "Export spec"
// writes (or sweep2/harp_spec.json), rebuilds the verified section pipeline
// (lib/pipeline.js + lib/section.js — the same math golden-tested against
// sweep2/core.py), lofts the true limaçon sections through OCC, and projects
// front / left / top drawings with real hidden-line removal.
//
//   node build.js [harp_spec.json] [frame.svg]
//   → out/soundbox_front.svg  out/soundbox_left.svg  out/soundbox_top.svg
//   → out/soundbox.step       (exact B-rep for FreeCAD/Fusion/TechDraw)
//
// Scope: the SOUNDBOX arm (the acoustically-tuned piece). The full wishbone
// union (pillar + neck + morphs) is the next step once the §6.2 pillar taper
// conflict is ruled on — a loft through self-intersecting sections is exactly
// what the kernel will refuse.
const path = require("path");
const fs = require("fs");

// node's require(esm) loads the emscripten single-file build as ESM, which
// expects CJS globals — shim them before the require.
globalThis.__dirname = path.join(__dirname, "node_modules/replicad-opencascadejs/src");
globalThis.require = require;
const initOC = require("replicad-opencascadejs/src/replicad_single.js").default;
const { setOC, makePolygon, loft, drawProjection } = require("replicad");

const P = require("./lib/pipeline.js");
const S = require("./lib/section.js");

const specPath = process.argv[2] || path.join(__dirname, "../../sweep2/harp_spec.json");
const framePath = process.argv[3] || path.join(__dirname, "../../sweep2/frame.svg");

function getD(svg, id) {
  const i = svg.indexOf('id="' + id + '"');
  const ps = svg.lastIndexOf("<path", i), pe = svg.indexOf("/>", i);
  return /\sd="([^"]*)"/.exec(svg.slice(ps, pe))[1];
}

(async () => {
  const spec = JSON.parse(fs.readFileSync(specPath, "utf8"));
  const svg = fs.readFileSync(framePath, "utf8");
  const green = P.flatten(getD(svg, "green_curve"));
  const red = P.flatten(getD(svg, "red_curve"));
  P.assertGreenOrientation(green);   // the four-month invariant — always first

  const sb = spec.soundbox || {};
  const cOut = sb.c_out != null ? sb.c_out : 2.0;
  const bDiv = sb.b_divisor != null ? sb.b_divisor : 4;
  const stations = P.soundboxStations(green, red, {
    S: (spec.sampling && spec.sampling.S) || 160,
    trimZ: (spec.base && spec.base.trim_z) || 130,
    sh_in: (spec.windows && spec.windows.sh_in) || { x: 965.2, y: 525.3 },
  });
  console.log("stations:", stations.length, " c_out:", cOut, " b divisor:", bDiv);

  setOC(await initOC({ locateFile: f => path.join(globalThis.__dirname, f) }));

  // world frame (same as hedit/sweep2): x = spine x, y = out-of-plane, z = FLOOR - spine y
  const FLOOR = P.FLOOR;
  const RING_PTS = 64, STATION_STRIDE = 3;
  const wires = [];
  for (let k = 0; k < stations.length; k += STATION_STRIDE) {
    const st = stations[k];
    const b = st.h / bDiv;
    let ring = S._curve(cOut, b, 720);
    let ymin = Infinity; for (const p of ring) if (p[1] < ymin) ymin = p[1];
    ring = ring.map(p => [p[0], p[1] - ymin]);           // dimple -> spine
    ring = S._resample(ring, RING_PTS);
    const o = [st.spine[0], 0, FLOOR - st.spine[1]];
    const pts = ring.map(q => [o[0] + q[1] * st.N[0], q[0], o[2] + q[1] * (-st.N[1])]);
    wires.push(makePolygon(pts).outerWire());
  }
  console.log("lofting", wires.length, "wires through OCC…");
  const solid = loft(wires, { ruled: false });
  console.log("solid:", solid.constructor.name);

  const outDir = path.join(__dirname, "out");
  fs.mkdirSync(outDir, { recursive: true });

  for (const view of ["front", "left", "top"]) {
    const proj = drawProjection(solid, view);
    const vis = proj.visible.toSVGPaths(), hid = proj.hidden.toSVGPaths();
    const vb = proj.visible.toSVGViewBox ? proj.visible.toSVGViewBox(5) : null;
    const paths = [
      ...vis.map(d => `<path d="${d}" fill="none" stroke="#111" stroke-width="1"/>`),
      ...hid.map(d => `<path d="${d}" fill="none" stroke="#111" stroke-width="0.5" stroke-dasharray="4 2"/>`),
    ].join("\n");
    const doc = `<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg"${vb ? ` viewBox="${vb}"` : ""}>\n${paths}\n</svg>\n`;
    const file = path.join(outDir, `soundbox_${view}.svg`);
    fs.writeFileSync(file, doc);
    console.log(view, "→", file, `(${vis.length} visible, ${hid.length} hidden paths)`);
  }

  try {
    const blob = await solid.blobSTEP();
    fs.writeFileSync(path.join(outDir, "soundbox.step"), Buffer.from(await blob.arrayBuffer()));
    console.log("STEP →", path.join(outDir, "soundbox.step"));
  } catch (e) { console.log("STEP export skipped:", e.message); }

  console.log("done.");
})().catch(e => { console.error("BUILD FAIL:", e.message); process.exit(1); });
