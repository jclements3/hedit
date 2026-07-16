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

// ---- a hedit cubic-bezier path "d" ("M x y C x1 y1 x2 y2 x3 y3 C ...") -> Maker.js BezierCurve models (Y-up) ----
function cubicPathToBeziers(d, H){
  // grab the leading moveto, then each subsequent C (6 numbers) builds one cubic seg
  const mm = d.match(/M\s*(-?[\d.eE+]+)[\s,]+(-?[\d.eE+]+)/);
  if(!mm) return [];
  let cx = +mm[1], cy = +mm[2];               // current point (svg y-down)
  const segs = [];
  const re = /C\s*(-?[\d.eE+]+)[\s,]+(-?[\d.eE+]+)[\s,]+(-?[\d.eE+]+)[\s,]+(-?[\d.eE+]+)[\s,]+(-?[\d.eE+]+)[\s,]+(-?[\d.eE+]+)/g;
  let c;
  while((c = re.exec(d)) !== null){
    const x1=+c[1], y1=+c[2], x2=+c[3], y2=+c[4], x3=+c[5], y3=+c[6];
    // flip every y to H - y so curves share the rails' Y-up frame
    segs.push(new makerjs.models.BezierCurve([cx, H-cy], [x1, H-y1], [x2, H-y2], [x3, H-y3]));
    cx = x3; cy = y3;
  }
  return segs;
}
// Reflection constant C for the y-flip (y -> C - y), reflecting about the viewBox's OWN frame.
// Must be minY + height, NOT height: `return vb[3]` is only correct when min-y == 0. Commit
// f408936 ("c1-origin canvas") re-datumed strings.svg to viewBox="-120 -1734.9 807.7 1864.9" --
// a NEGATIVE origin -- which silently offset every flipped y by 1734.9 mm, throwing the strings
// clear above the frame. vb[0] (min-x) is deliberately NOT used: x is a pass-through, not a
// reflection, so it needs no axis constant (see DATUM_NOTE.md).
function svgHeight(svgText){
  const raw = attr(svgText, "viewBox");
  if(!raw) console.warn("WARN: no viewBox on the SVG; falling back to \"0 0 800 600\" -- every y will be flipped about 600.");
  const vb = (raw || "0 0 800 600").split(/[\s,]+/).map(Number);
  return vb[1] + vb[3];
}
function loadStrings(svgText){
  const H = svgHeight(svgText);
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

// ---- hedit fitted curves: <path data-role="bottom-curve"|"top-curve" d="..."> ----
function loadCurves(svgText, role){
  const H = svgHeight(svgText);
  for(const m of svgText.matchAll(/<path\b[^>]*?\/?>/g)){
    const t = m[0];
    if(!new RegExp('data-role="' + role + '"').test(t)) continue;
    const d = attr(t, "d");
    if(d) return cubicPathToBeziers(d, H);
  }
  return [];
}

// ---- hedit circles by data-role (pins / natural / sharp / midi) -> Maker.js Circles (Y-up) ----
function loadCircles(svgText, role){
  const H = svgHeight(svgText);
  const circles = [];
  for(const m of svgText.matchAll(/<circle\b[^>]*?\/?>/g)){
    const t = m[0];
    if(!new RegExp('data-role="' + role + '"').test(t)) continue;
    const cx=+attr(t,"cx"), cy=+attr(t,"cy"), r=+attr(t,"r");
    if([cx,cy,r].some(isNaN)) continue;
    // SVG is y-down; flip cy to Y-up
    circles.push(new makerjs.paths.Circle([cx, H - cy], r));
  }
  return circles;
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

  // 2) strings + hedit-authored elements from the SVG
  if(fs.existsSync(SVG_PATH)){
    const svgText = fs.readFileSync(SVG_PATH, "utf8");

    // 2a) strings
    const strs = loadStrings(svgText);
    if(strs.length){
      const m = { paths: {}, layer: "strings" };
      strs.forEach((s, i) => { m.paths["s" + i] = new makerjs.paths.Line(s[0], s[1]); });
      harp.models.strings = m;
      report.push(`strings: ${strs.length} lines`);
    }

    // 2b) fitted curves: bottom-curve -> soundboard, top-curve -> neck
    const curveDefs = [
      { role: "bottom-curve", key: "bottomCurve", layer: "soundboard", label: "bottom curve" },
      { role: "top-curve",    key: "topCurve",    layer: "neck",       label: "top curve" },
    ];
    curveDefs.forEach(cd => {
      const segs = loadCurves(svgText, cd.role);
      const m = { models: {}, layer: cd.layer };
      segs.forEach((bz, i) => { m.models["c" + i] = bz; });
      harp.models[cd.key] = m;
      if(!segs.length) console.warn(`WARN: no <path data-role="${cd.role}"> in the SVG -- ${cd.label} is empty.`);
      report.push(`${cd.label}: ${segs.length} segs`);
    });

    // 2c) pins
    const pins = loadCircles(svgText, "pin");
    const pm = { paths: {}, layer: "pins" };
    pins.forEach((c, i) => { pm.paths["p" + i] = c; });
    harp.models.pins = pm;
    if(!pins.length) console.warn('WARN: no <circle data-role="pin"> in the SVG -- pins layer is empty.');
    report.push(`pins: ${pins.length}`);

    // 2d) sensor dots: natural / sharp / midi
    const dotRoles = ["natural", "sharp", "midi"];
    const dotCounts = {};
    dotRoles.forEach(role => {
      const dots = loadCircles(svgText, role);
      const m = { paths: {}, layer: role };
      dots.forEach((c, i) => { m.paths["d" + i] = c; });
      harp.models[role] = m;
      dotCounts[role] = dots.length;
    });
    report.push(`sensor dots: natural=${dotCounts.natural} sharp=${dotCounts.sharp} midi=${dotCounts.midi}`);
  }

  // 3) export
  const svgOpts = {
    units: makerjs.unitType.Millimeter,
    layerOptions: {
      DP:{stroke:RAIL_COLOR.DP}, BP:{stroke:RAIL_COLOR.BP}, SP:{stroke:RAIL_COLOR.SP}, strings:{stroke:"#888"},
      soundboard:{stroke:"red"}, neck:{stroke:"blue"}, pins:{stroke:"#ffb454"},
      natural:{stroke:"#e6261f"}, sharp:{stroke:"#3ad13a"}, midi:{stroke:"#2d7ff9"},
    },
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
