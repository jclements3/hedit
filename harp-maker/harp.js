"use strict";
/*
 * harp.js -- Maker.js ASSEMBLY script.
 *
 * The division of labor:
 *   hedit  = AUTHORING  (drag the DP/BP/SP curves + lay out the strings)  -> harp.json + strings.svg
 *   harp.js = ASSEMBLY  (code: import those, build the Maker.js model, export SVG/DXF[/3-D])
 *
 * This script IMPORTS the hedit-authored curves (paraguayan_overrides.json schema:
 * DP/BP/SP node+handle chains, WP profile) and the strings (from an SVG), builds a
 * Maker.js model, and exports harp.svg + harp.dxf in millimeters.
 *
 * Coordinates: the JSON is Y-up mm -- which is exactly Maker.js's native frame, so the
 * rails import 1:1 with no flip.
 *
 * Usage:  node harp.js [harp.json] [strings.svg]
 * Default: ../../paraguayan/paraguayan_overrides.json  and  ../strings.svg
 */

const fs = require("fs");
const path = require("path");
const makerjs = require("makerjs");

const JSON_PATH = process.argv[2] || path.join(__dirname, "..", "..", "paraguayan", "paraguayan_overrides.json");
const SVG_PATH  = process.argv[3] || path.join(__dirname, "..", "strings.svg");
const RAIL_COLOR = { DP: "blue", BP: "red", SP: "purple" };   // dimple / bulge / spine

// ---- a hedit/paraguayan node-chain -> array of cubic control-point sets ----
function chainToBeziers(ch){
  const n = ch.nodes, segs = [];
  const hp = (node, h) => [node.x + (node[h] ? node[h].dx : 0), node.y + (node[h] ? node[h].dy : 0)];
  const seg = (a, b) => [[a.x, a.y], hp(a, "hout"), hp(b, "hin"), [b.x, b.y]];
  for(let k = 1; k < n.length; k++) segs.push(seg(n[k-1], n[k]));
  if(ch.closed && n.length > 1) segs.push(seg(n[n.length-1], n[0]));
  return segs;
}
function railModel(ch){
  const m = { models: {} };
  chainToBeziers(ch).forEach((c, i) => { m.models["c" + i] = new makerjs.models.BezierCurve(c[0], c[1], c[2], c[3]); });
  return m;
}

// ---- strings from the SVG <line> elements ----
function attr(tag, n){ const m = tag.match(new RegExp('\\b' + n + '="([^"]+)"')); return m ? m[1] : null; }
function loadStrings(svgText){
  const vb = (attr(svgText, "viewBox") || "0 0 800 600").split(/[\s,]+/).map(Number);
  const H = vb[3];
  const lines = [];
  for(const m of svgText.matchAll(/<line\b[^>]*?\/?>/g)){
    const t = m[0];
    if(/data-role="s-axis"/.test(t)) continue;
    const x1=+attr(t,"x1"), y1=+attr(t,"y1"), x2=+attr(t,"x2"), y2=+attr(t,"y2");
    if([x1,y1,x2,y2].some(isNaN)) continue;
    // SVG is y-down; flip to Y-up so strings share the rails' frame
    lines.push([[x1, H - y1], [x2, H - y2]]);
  }
  return lines;
}

function main(){
  const harp = { units: makerjs.unitType.Millimeter, models: {}, paths: {} };
  let report = [];

  // 1) rails from the authored JSON
  if(fs.existsSync(JSON_PATH)){
    const j = JSON.parse(fs.readFileSync(JSON_PATH, "utf8"));
    ["DP","BP","SP"].forEach(role => {
      if(j[role] && j[role].nodes){
        harp.models[role] = railModel(j[role]);
        harp.models[role].layer = role;
        report.push(`${role}: ${chainToBeziers(j[role]).length} cubic seg(s)`);
      }
    });
    if(j.WP) report.push(`WP: ${j.WP.nodes.length} profile nodes (f->r, used by the 3-D sweep, not 2-D)`);
    if(j.column_width != null) report.push(`column_width = ${j.column_width}`);
  } else {
    report.push("(no harp.json found at " + JSON_PATH + ")");
  }

  // 2) strings from the SVG
  if(fs.existsSync(SVG_PATH)){
    const strs = loadStrings(fs.readFileSync(SVG_PATH, "utf8"));
    if(strs.length){
      const m = { paths: {}, layer: "strings" };
      strs.forEach((s, i) => { m.paths["s" + i] = new makerjs.paths.Line(s[0], s[1]); });
      harp.models.strings = m;
      report.push(`strings: ${strs.length} lines`);
    }
  }

  // 3) export
  const svgOpts = {
    units: makerjs.unitType.Millimeter,
    layerOptions: { DP:{stroke:RAIL_COLOR.DP}, BP:{stroke:RAIL_COLOR.BP}, SP:{stroke:RAIL_COLOR.SP}, strings:{stroke:"#888"} },
  };
  fs.writeFileSync(path.join(__dirname, "harp.svg"), makerjs.exporter.toSVG(harp, svgOpts));
  fs.writeFileSync(path.join(__dirname, "harp.dxf"), makerjs.exporter.toDXF(harp, { units: makerjs.unitType.Millimeter }));

  let ext = null; try { ext = makerjs.measure.modelExtents(harp); } catch(e){}
  console.log("imported (Maker.js, Y-up mm):");
  report.forEach(r => console.log("  " + r));
  if(ext) console.log(`extents: ${ext.width.toFixed(1)} x ${ext.height.toFixed(1)} mm`);
  console.log("wrote: harp.svg, harp.dxf");
}

main();
