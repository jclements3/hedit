# erand47 — Session Handoff

Hand-off for the next Claude.ai desktop session to continue the **erand47** design.

## 1. What this is
**erand47** = 47-string (C1–G7) **solid-body electric DOUBLE-ACTION pedal harp**.
Closed twin-plate **304 stainless** frame: two ¼″ (6.35 mm) bars, **inner faces at y = ±6.5**
(clear gap 13 mm), bar centres ±9.675, **string centreline at y = 0**. Axes: z = string length,
x = bass→treble station, y = depth. Strings raked **7°** (tops toward the pillar).
Canonical design record = **clements47.md**.

> NOTE on memory: the assistant's stored "memories" describe a *different* project (a Paraguayan
> carbon-fiber harp / harp.py). That is NOT this project. Only the working style carries over
> (phone user: terse, tables over prose, act don't ask, SVG not PNG).

## 2. Canonical files (rebuild from these)
- **clements47.md** — design doc. §1–§7 frame geometry + the parametric generator; §8 hand-curated
  final SVG (with the string-connections *loupe* = "exploded string tips"); §9 pitch mechanism (this
  session). The generator reports: closing load 6606 N, shear 811 N, bare frame 12.11 kg, rigged 14.5 kg.
- **gen.py** — the generator extracted from §7 (frame, strings, N/S disc-cut curves) → writes `erand47.svg`.
- **gen_bones.py** — `gen.py` **+ §8 disc/prong sizing (real, per-string) + bone-path skeleton +
  to-scale state diagram**. Writes `erand47_bones.svg`, `erand47_bone_detail.svg`, `disc_state_scale.svg`.
- **parts.py** — actuation **parts library** (importable). Gold standard links + grey variable
  connectors → writes `parts.svg`.
- **sizing.py** — original disc/prong/axle sizing analysis (source of the real numbers).
- **bezierfit.py** — Bézier fit utility.
- **txt-tar.py / txt-untar.py** — text-archive tools (from the other harp project; kept for reference).

### Rebuild
`python3 gen_bones.py` and `python3 parts.py` (needs `numpy`, `cairosvg`). Outputs land beside the scripts.
Always render a PNG to check, present only the SVG.

## 3. The mechanism (designed this session)
Each string is tuned **flat**; the **natural** disc shortens it 1 semitone (node at **5.61 % L** from the
neck), the **sharp** disc 2 (**10.91 % L**). `F_NAT = 1−2^(−1/12)`, `F_SHP = 1−2^(−1/6)`.

**Disc = capsule** with a **round prong-pin seated flush at each tip**. At **flat** the prongs are
**horizontal**, straddling the string with ~0.8 mm air/side. **ENGAGE = rotate CCW ~55°**: the **lower
prong lands on the pitch node**, the **upper prong grabs above**. Sequence: pedal **notch 1 →
natural disc CCW**; **notch 2 → sharp disc CCW** (natural stays engaged). Return springs reverse on lift.

### Real per-string sizing (now in gen_bones.py as arrays RP, PC, LH, WW)
`F_side = 2T·sin(7.5°)`, prong Ø from a 6.5 mm cantilever, **pc (axle→prong) = rp + Ø/2 + 0.8**,
disc half-length **Lh = pc + rp**, width **2(rp+0.3)**, disc ~2 mm thick, axle Ø ~3 mm.

| note | string Ø | prong Ø | pc | disc L×W |
|---|---|---|---|---|
| C1 | 1.68 | 2.40 | 2.84 | 8.08 × 3.00 |
| E2 | 2.64 | 2.30 | 3.27 | 8.84 × 2.90 |
| B3 | 1.27 | 2.10 | 2.49 | 7.07 × 2.70 |
| G7 | 0.64 | 1.50 | 1.87 | 5.23 × 2.10 |

## 4. Full bone chain (foot → prong)
**pedal → control rod (+regulation turnbuckle) → L bell-crank (pillar top, vertical→rotary) →
relay fork → natural rod (upper) + sharp rod (lower) → ternary disc levers chained by binary links →
axle → disc → prong → string.** Held by the pedal **notch**; **return spring** runs it back.

## 5. Pedals / class→bar / planes
7 pedals, 3 positions (upper=flat, notch1=natural, notch2=sharp): **Left foot D C B · Right foot E F G A**.
Pedals **cross at the tips** → left foot drives the **−y (right) bar** (D,C,B = 20 strings), right foot
the **+y (left) bar** (E,F,G,A = 27). A string's natural AND sharp discs share its class bar.
Each class = its **own constant-y plane** (planar linkage); the 7 planes stack in y
(≈ −15,−18,−21 for D,C,B; +15..+24 for E,F,G,A). Discs at y=0; cranks/links/rods on the bar backs;
each axle bridges through the bar. Pillar carries 7 stacked control rods.

## 6. Naming scheme (bone control points)
String name: `"CDEFGAB"[i%7] + str(1 + i//7)` (i=0→c1 … i=46→g7).
Per disc: `<str><n|s><ti|ta|to>` = input / **axle** / output; plus `…nd` (node = pitch point on the
N/S curve) and `…up` (upper prong). The **axle is offset off the N/S curve by the prong** (lower prong
sits on the node). Bell crank per class: `<class>BCi / BCa / BCo`. Control-rod end / pedal: `<class>PED`.

## 7. Bone-path parameters (gen_bones.py — tune to set placement & sizes)
`ENGAGE_DEG=55, CRANK_R_MM=8, LEVER_HALF_DEG=30, LEVER_SIDE=+1,
BC_PIVOT_OFF, BC_IN_ARM, BC_OUT_ARM, CTRL_ROD_LEN=130`. The `…ta` axles are derived (node minus
per-string `PC` along the engaged lower-prong direction).

## 8. Parts library (parts.py)
- **GOLD (standard, fixed shape; pass `scale<1` for treble):** `disc_lever` (big axle/spindle hole Ø3 +
  two pin holes Ø1.6, 8 mm arms ±30°), `relay_lever` (3 pin holes, no disc), `bell_crank` (bent ternary).
- **GREY (variable):** `grey_link(p0, p1, bow)` — capsule connector; **length = span**, **bow = local
  N/S Bézier curvature**. These are the only parts that change per string.

## 9. STATUS — real vs TODO
**REAL (built + rendered this session):**
- §9 mechanism added to clements47.md (renames ST→ET etc.; N/S quintic fits; orientation note).
- Real disc/prong sizing arrays in gen_bones.py. To-scale state diagram `disc_state_scale.svg`
  (pins seated flush, CCW, per-string numbers).
- Bone-path skeleton `erand47_bones.svg` + station detail `erand47_bone_detail.svg`.
- Parts catalog `parts.svg` + importable `parts.py`.
- Combined extended-canvas drawing `erand47_profile_state.svg` (profile+loupe on top, state panel below).
- Explanatory drawings: engagement (`engage_v3`), one-string state (`disc_state_v1`), pedal mech
  (`pedal_mech_v2`), action train (`action_train_v2`), neck plan (`neck_plan_v2`), labeled relay
  (`relay_labeled_v1`), single disc (`one_disc_v1`, `one_disc_exploded_v1`), harp profile w/ mechanism
  (`harp_profile_v3`), yz mounting (`disc_yz_v10`).

**TODO / open (in priority order):**
1. **Engaged string deflection** — the state diagram still draws the string straight; the true node is
   the *tangent point* where the string kinks to the lower prong. Add the deflection.
2. **Re-add `build_class_bones` / `draw_bones` using per-string `PC`** — the last gen_bones.py rewrite
   kept the sizing + state diagram but dropped the bone-builder; re-add it, offsetting axles by `PC[i]`
   (NOT the old constant 2.45).
3. **Assemble the real relay** — import `parts.py` into gen_bones.py; place a scaled `disc_lever` at each
   `…ta` along the N/S curves, a `bell_crank` at the pillar top, `grey_link`s between consecutive levers
   with `bow` = local Bézier curvature. Render one class (B) assembled, then all 7.
4. **y-stack / end-on view** — show the 7 class planes stacked behind the two bars.
5. **Two-notch sequencing** — design the lost-motion element so notch1 = natural fully home, then
   notch2 = sharp (natural held). Not yet designed.
6. **Solve the throws / bone lengths** — needs three inputs from the designer: **pillar run + lean**,
   **pedal pivot-to-tip + notch travel**, a **chosen crank length**. Then solve
   pedal ratio × bell-crank ratio × crank length so notch1 = Δθ_natural, notch2 = Δθ_sharp.
7. **Treble collisions** — F7 nat+sharp fit only shrunk (17-4PH); G7 marginal → single-action or set string.
8. **Fold the disc/prong sizing into clements47.md §9** (numbers currently live only in gen_bones.py).
9. **Fold the state panel into the generator** (erand47_profile_state.svg is currently a post-combine of
   the §8 SVG + the state SVG; could be emitted in one pass).

## 10. Conventions
Palette: frame `#ff9e6b`, strings `#7d7762`, neck dots green `#6ee0a0`, eyelet gold `#e0b86e`,
natural violet `#c0a0ff`, sharp orange `#ff8c5a`, rods blue `#7fb0ff`, gold parts `#e7c97e`,
grey links `#c3c7cd`, bg `#13110d`. Engage rotation is **CCW**.
Phone user → terse replies, tables over prose, no clarifying-question pickers, act directly.

## 11. File manifest (key)
- clements47.md, gen.py, gen_bones.py, parts.py, sizing.py, bezierfit.py
- erand47.svg, erand47_bones.svg, erand47_bone_detail.svg, disc_state_scale.svg, erand47_profile_state.svg, parts.svg
- engage_v3.svg, disc_state_v1.svg, pedal_mech_v2.svg, action_train_v2.svg, neck_plan_v2.svg,
  relay_labeled_v1.svg, one_disc_v1.svg, one_disc_exploded_v1.svg, harp_profile_v3.svg, disc_yz_v10.svg
- (earlier iterations and helper scripts also included)

## 12. Suggested next-session opening prompt
```
Continue erand47. Unpack the tarball, read HANDOFF.md, then `python3 gen_bones.py` and
`python3 parts.py` to confirm the baseline renders. Then do TODO #2 and #3: re-add
build_class_bones/draw_bones using per-string PC, import parts.py, and render class B
assembled on the real neck (scaled disc_lever at each …ta, bell_crank at the pillar top,
grey_links with bow from the local N/S Bézier curvature). Show me the assembled SVG.
```
