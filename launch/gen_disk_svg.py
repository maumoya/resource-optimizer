"""Generate assets/disk-cleanup.svg: the before/after card, animated (SMIL loop).

Numbers come from launch/facts.json (macOS Storage screenshots, GB decimal).
"""
import json
import pathlib
import sys

T = 12  # seconds per loop
S, E = 0.12, 0.62  # cleanup phase as fraction of the loop
K = 24  # counter steps
FACTS = json.loads((pathlib.Path(__file__).parent / "facts.json").read_text())
TOTAL, USED0, USED1 = (float(FACTS[k]["value"]) for k in ("disk_total_gb", "used_before_gb", "used_after_gb"))
FREE0, FREE1 = TOTAL - USED0, TOTAL - USED1
SANS = "-apple-system,Helvetica,Arial,sans-serif"
MONO = "ui-monospace,Menlo,monospace"
f = lambda x: f"{x:.4f}".rstrip("0").rstrip(".")
anim = lambda attr, values, times, mode="linear": (
    f'<animate attributeName="{attr}" dur="{T}s" repeatCount="indefinite" '
    f'calcMode="{mode}" values="{values}" keyTimes="{times}"/>')
appear = lambda at: anim("opacity", "0;1", f"0;{f(at)}", "discrete")
BAR_X, BAR_W = 160, 560
W0, W1 = round(BAR_W * FREE0 / TOTAL), round(BAR_W * FREE1 / TOTAL)
pct = lambda gb: round(gb * 100 / TOTAL)


def frames(text_for, x, y, fill, size, weight="400", anchor="start"):
    """One text per step k=0..K, each shown only during its slice of the cleanup."""
    out = []
    for k in range(K + 1):
        start, end = S + (E - S) * k / K, S + (E - S) * (k + 1) / K
        if k == 0:
            vals, kt = "1;0", f"0;{f(end)}"
        elif k == K:
            vals, kt = "0;1", f"0;{f(start)}"
        else:
            vals, kt = "0;1;0", f"0;{f(start)};{f(end)}"
        out.append(
            f'<text x="{x}" y="{y}" fill="{fill}" font-family="{SANS}" font-size="{size}" '
            f'font-weight="{weight}" text-anchor="{anchor}" opacity="{vals[0]}">{text_for(k / K)}'
            f'{anim("opacity", vals, kt, "discrete")}</text>')
    return "\n".join(out)


free_at = lambda t: FREE0 + (FREE1 - FREE0) * t
checks = ["caches", "temp files", "unused models", "old simulators", "unused apps", "Trash"]
check_svg = []
for i, name in enumerate(checks):
    at = S + (E - S) * (i + 0.7) / len(checks)
    check_svg.append(
        f'<text x="{48 + (i % 3) * 230}" y="{452 + (i // 3) * 34}" fill="#a7c4a0" font-family="{SANS}" '
        f'font-size="20" opacity="0"><tspan fill="#a3e635">✓</tspan> {name}{appear(at)}</text>')

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="560" viewBox="0 0 800 560" role="img" aria-label="Animation: on a 494 GB Mac mini, free space grows from {FREE0:.1f} GB ({pct(FREE0)} percent) to {FREE1:.1f} GB ({pct(FREE1)} percent) as caches, temp files, unused models, old simulators, unused apps and Trash are cleared: {FREE1 - FREE0:.1f} GB freed, {pct(FREE1 - FREE0)} percent of the disk, every delete approved by the user">
<rect width="800" height="560" fill="#0f1a12"/>
<g>{anim("opacity", "0;1;1;0", "0;0.03;0.97;1")}
<text x="48" y="78" fill="#d9f99d" font-family="{MONO}" font-size="22">$ run resource-optimizer<tspan fill="#a3e635" opacity="0"> ✓ check done{appear(E)}</tspan></text>
<text x="48" y="140" fill="#ecfdf5" font-family="{SANS}" font-size="26" font-weight="600">Free space, 494 GB Mac mini</text>
<text x="48" y="215" fill="#a7c4a0" font-family="{SANS}" font-size="20">Before</text>
<rect x="{BAR_X}" y="192" width="{BAR_W}" height="34" rx="6" fill="#1f3324"/>
<rect x="{BAR_X}" y="192" width="{W0}" height="34" rx="6" fill="#f87171"/>
<text x="{BAR_X + W0 + 12}" y="216" fill="#fecaca" font-family="{SANS}" font-size="20">{FREE0:.1f} GB free ({pct(FREE0)}%)</text>
<text x="{BAR_X + BAR_W - 12}" y="216" fill="#a7c4a0" font-family="{SANS}" font-size="18" text-anchor="end">{USED0:.1f} GB used</text>
<text x="48" y="295" fill="#a7c4a0" font-family="{SANS}" font-size="20">After</text>
<rect x="{BAR_X}" y="272" width="{BAR_W}" height="34" rx="6" fill="#1f3324"/>
<rect x="{BAR_X}" y="272" width="{W0}" height="34" rx="6" fill="#f87171">
{anim("width", f"{W0};{W0};{W1};{W1}", f"0;{f(S)};{f(E)};1")}
{anim("fill", "#f87171;#f87171;#a3e635;#a3e635", f"0;{f(S)};{f(E)};1")}
</rect>
<g><animateTransform attributeName="transform" type="translate" dur="{T}s" repeatCount="indefinite" values="0 0;0 0;{W1 - W0} 0;{W1 - W0} 0" keyTimes="0;{f(S)};{f(E)};1"/>
{frames(lambda t: f"{free_at(t):.1f} GB free ({pct(free_at(t))}%)", BAR_X + W0 + 12, 296, "#d9f99d", 20)}
</g>
{frames(lambda t: f"{TOTAL - free_at(t):.1f} GB used", BAR_X + BAR_W - 12, 296, "#a7c4a0", 18, anchor="end")}
{frames(lambda t: f"{pct(free_at(t) - FREE0)}% of the disk freed", 48, 400, "#a3e635", 64, "700")}
{chr(10).join(check_svg)}
<text x="48" y="530" fill="#ecfdf5" font-family="{SANS}" font-size="22" font-weight="600" opacity="0">{FREE1 - FREE0:.1f} GB freed. 100% of deletes approved by you.{appear(E)}</text>
</g>
</svg>
'''
sys.stdout.write(svg)
