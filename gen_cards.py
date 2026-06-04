import json
import os

FONT = "ui-monospace,SFMono-Regular,SF Mono,Menlo,monospace"
W = 495


def fmt_n(n):
    return f"{n/1000:.1f}k" if n >= 1000 else str(n)


def _svg(repos, tot, upd, theme):
    if theme == "plain":
        bg, bd        = "#0d1117", "#30363d"
        h_col, t_col  = "#e6edf3", "#c9d1d9"
        d_col, acc    = "#7d8590", "#58a6ff"
        n_sz, row_h   = 22, 26
        num_y, lbl_y  = 70, 86
        div2, col_y   = 98, 114
        hdr           = 122
    else:
        bg, bd        = "#0f0e17", "#ff6b35"
        h_col, t_col  = "#ffd700", "#fffffe"
        d_col, acc    = "#00d4aa", "#ff6b35"
        n_sz, row_h   = 28, 28
        num_y, lbl_y  = 74, 92
        div2, col_y   = 104, 120
        hdr           = 128

    H = hdr + len(repos) * row_h + 12
    o = [
        f'<svg width="{W}" height="{H}" xmlns="http://www.w3.org/2000/svg">',
        f'<rect width="{W}" height="{H}" rx="6" fill="{bg}" stroke="{bd}" stroke-width="1.5"/>',
        f'<text x="18" y="34" font-family="{FONT}" font-size="15" font-weight="600" fill="{h_col}">Psy-Fer&#x27;s GitHub Stats</text>',
        f'<text x="{W-14}" y="34" font-family="{FONT}" font-size="11" fill="{d_col}" text-anchor="end">updated {upd}</text>',
        f'<line x1="14" y1="46" x2="{W-14}" y2="46" stroke="{bd}" stroke-width="0.5"/>',
    ]

    prs_str = f'{tot.get("prs_open", 0)}/{tot.get("prs_closed", 0)}'
    for i, (label, disp, col) in enumerate([
        ("total stars",     fmt_n(tot["stars"]),        acc),
        ("PRs open/closed", prs_str,                    t_col),
        ("total clones",    fmt_n(tot["clones_total"]), d_col),
    ]):
        cx = W // 6 + i * (W // 3)
        o += [
            f'<text x="{cx}" y="{num_y}" font-family="{FONT}" font-size="{n_sz}" font-weight="700" fill="{col}" text-anchor="middle">{disp}</text>',
            f'<text x="{cx}" y="{lbl_y}" font-family="{FONT}" font-size="11" fill="{d_col}" text-anchor="middle">{label}</text>',
        ]

    o += [
        f'<line x1="14" y1="{div2}" x2="{W-14}" y2="{div2}" stroke="{bd}" stroke-width="0.5"/>',
        f'<text x="195" y="{col_y}" font-family="{FONT}" font-size="10" fill="{d_col}" text-anchor="middle">stars</text>',
        f'<text x="275" y="{col_y}" font-family="{FONT}" font-size="10" fill="{d_col}" text-anchor="middle">PRs</text>',
        f'<text x="355" y="{col_y}" font-family="{FONT}" font-size="10" fill="{d_col}" text-anchor="middle">issues</text>',
        f'<text x="{W-14}" y="{col_y}" font-family="{FONT}" font-size="10" fill="{d_col}" text-anchor="end">lang</text>',
    ]

    for idx, (name, r) in enumerate(repos.items()):
        y = hdr + (idx + 1) * row_h - 8
        lang = r.get("language") or "—"
        prs = f'{r.get("prs_open", 0)}/{r.get("prs_closed", 0)}'
        iss = f'{r.get("issues_open", 0)}/{r.get("issues_closed", 0)}'
        o += [
            f'<text x="18" y="{y}" font-family="{FONT}" font-size="12" fill="{t_col}">{name}</text>',
            f'<text x="195" y="{y}" font-family="{FONT}" font-size="12" fill="{acc}" text-anchor="middle">★ {r["stars"]}</text>',
            f'<text x="275" y="{y}" font-family="{FONT}" font-size="12" fill="{t_col}" text-anchor="middle">{prs}</text>',
            f'<text x="355" y="{y}" font-family="{FONT}" font-size="12" fill="{d_col}" text-anchor="middle">{iss}</text>',
            f'<text x="{W-14}" y="{y}" font-family="{FONT}" font-size="11" fill="{d_col}" text-anchor="end">{lang}</text>',
        ]

    o.append('</svg>')
    return '\n'.join(o)


def main():
    with open("data/stats.json") as f:
        stats = json.load(f)
    os.makedirs("cards", exist_ok=True)
    for theme in ("plain", "weird"):
        path = f"cards/stats-{theme}.svg"
        with open(path, "w") as f:
            f.write(_svg(stats["repos"], stats["totals"], stats["updated"], theme))
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
