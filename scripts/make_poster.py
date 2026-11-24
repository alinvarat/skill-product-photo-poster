"""Build a 3:4 (or 1:1) product poster: photos fill the whole canvas, title + bullets as plain text over soft dark gradients (no boxes).
Usage: python -I make_poster.py spec.json out.png
spec: {"title","subtitle"?,"photos":[paths],"bullets":[str],"accent"?:"#a66bff","bg"?:"#0f1318","width"?:1500,"focus"?:[x% per photo],"vfocus"?:[y% per photo],"ratio"?:"1:1"(default)|"3:4","layout"?:"cols"|"rows","split"?:[relative cell sizes],"bullet_size"?:0.03,"font"?:"noto"|"prompt","logo"?:true,"logo_opacity"?:1,"logo_size"?:0.13}
Rendered by headless Chrome (correct Thai tone marks; Pillow without raqm drops them).
Photos fill cropped cells edge to edge; text sits over the approved soft edge gradients. The default ratio is 1:1.
"""
import argparse, json, math, os, shutil, subprocess, sys, tempfile, pathlib

CHROME = [p for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser") if (p := shutil.which(name))] + [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
          r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
          os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")]

FONTS = pathlib.Path(__file__).resolve().parent.parent / "assets" / "fonts"

def esc(t): return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def validate_spec(s, base, out_path):
    photos = s.get("photos")
    if not isinstance(photos, list) or not 1 <= len(photos) <= 3 or any(not isinstance(p, str) or not p for p in photos):
        raise ValueError("photos must contain 1 to 3 file paths")
    resolved = [(base / p).resolve() for p in photos]
    if any(not p.is_file() for p in resolved):
        raise ValueError("one or more photo files do not exist")
    if pathlib.Path(out_path).resolve() in resolved:
        raise ValueError("output must not replace a source photo")
    width = s.get("width", 1500)
    if isinstance(width, bool) or not isinstance(width, int) or width <= 0:
        raise ValueError("width must be a positive integer")
    try:
        parts = s.get("ratio", "1:1").split(":")
        if len(parts) != 2: raise ValueError()
        rw, rh = map(int, parts)
        if rw <= 0 or rh <= 0 or width * rh // rw <= 0: raise ValueError()
    except (ValueError, AttributeError):
        raise ValueError("ratio must contain two positive integers, e.g. 1:1") from None
    if s.get("layout", "cols") not in ("cols", "rows"):
        raise ValueError("layout must be cols or rows")
    for key in ("focus", "vfocus", "split"):
        if key not in s: continue
        values = s[key]
        if not isinstance(values, list) or len(values) != len(photos):
            raise ValueError(key + " must have one value per photo")
        if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in values):
            raise ValueError(key + " values must be finite numbers")
        if key == "split" and any(v <= 0 for v in values):
            raise ValueError("split values must be positive")
        if key != "split" and any(not 0 <= v <= 100 for v in values):
            raise ValueError(key + " percentages must be between 0 and 100")
    if not isinstance(s.get("bullets", []), list) or any(not isinstance(x, str) for x in s.get("bullets", [])):
        raise ValueError("bullets must be a list of strings")
    return resolved


def main(spec_path, out_path):
    s = json.load(open(spec_path, encoding="utf-8"))
    base = pathlib.Path(spec_path).resolve().parent     # photo paths are relative to the spec file
    s["photos"] = [str(p) for p in validate_spec(s, base, out_path)]
    W = s.get("width", 1500)
    rw, rh = (int(x) for x in s.get("ratio", "1:1").split(":")); H = W * rh // rw
    square = rw == rh                                    # 1:1 needs a tighter vertical layout
    n = len(s["photos"]); M = round(W * .04)
    foc = s.get("focus", [50] * n)                      # horizontal focus % per photo
    vf = s.get("vfocus", [50] * n)                      # vertical focus % per photo
    sp = s.get("split", [1] * n)                        # relative size of each photo cell (rows/cols)
    ph = "".join('<div style="flex:%s;background-image:url(%s);background-position:%s%% %s%%"></div>'
                 % (sp[i], pathlib.Path(p).resolve().as_uri(), foc[i], vf[i]) for i, p in enumerate(s["photos"]))
    logo = ""
    if s.get("logo", True):                             # PULSE logo, clear, bottom-right: always on unless logo=false
        lo = s.get("logo_opacity", 1)
        logo = '<img class=logo src="%s" style="opacity:%s">' % ((FONTS.parent / "logo" / "pulse_logo.webp").as_uri(), lo)
    lis = "".join(f"<li>{esc(b)}</li>" for b in s.get("bullets", []))
    sub = f'<div class="sub">{esc(s["subtitle"])}</div>' if s.get("subtitle") else ""
    top = '<div class="p top"><h1>%s</h1>%s<div class=bar></div></div>' % (esc(s["title"]), sub) if s.get("title") else ""
    bot = '<div class="p bot"><ul>%s</ul></div>' % lis if s.get("bullets") else ""
    ac = s.get("accent", "#a66bff")
    if s.get("font", "noto") == "prompt":
        ff = "".join("@font-face{font-family:Pf;font-weight:%d;src:url(%s)}" % (w, (FONTS / ("Prompt-%s.ttf" % n)).as_uri()) for w, n in ((400, "Regular"), (500, "Medium"), (600, "SemiBold")))
        fam = "Pf,sans-serif"
    else:  # Mac-like: Inter for Latin (if installed) + Noto Sans Thai (variable, bundled)
        ff = "@font-face{font-family:NT;font-weight:100 900;src:url(%s)}" % (FONTS / "NotoSansThai.ttf").as_uri()
        fam = "Inter,NT,sans-serif"
    html = f"""<!doctype html><meta charset=utf-8><style>
{ff}
*{{box-sizing:border-box;margin:0}}
html,body{{width:{W}px;height:{H}px;overflow:hidden;background:#000;color:#fff;
font-family:{fam}}}
.ph{{position:absolute;inset:0;display:flex;gap:6px;flex-direction:{'column' if s.get('layout') == 'rows' else 'row'}}}
.ph div{{background-size:cover}}
.p{{position:absolute;left:{M}px;right:{M}px;text-shadow:0 2px 14px rgba(0,0,0,.9),0 0 3px rgba(0,0,0,.8);
padding:0 {int(M*(1.4 if square else 1.1))}px}}
.logo{{position:absolute;right:{M}px;bottom:{M}px;width:{int(W*s.get('logo_size', .14))}px;border-radius:50%;box-shadow:0 0 0 3px rgba(255,255,255,.55),0 4px 18px rgba(0,0,0,.55);pointer-events:none}}
.sc{{position:absolute;left:0;right:0;pointer-events:none}}
.sc.t{{top:0;height:{int(W*.2)}px;background:linear-gradient(rgba(10,8,16,.7),transparent)}}
.sc.b{{bottom:0;height:{int(W*.32)}px;background:linear-gradient(transparent,rgba(10,8,16,.8) 75%)}}
.top{{top:{int(M*1.2)}px;text-align:center}}
h1{{font-size:{int(W*.075)}px;line-height:1.15;font-weight:600}}
.sub{{font-size:{int(W*.036)}px;color:#c4ccd4;margin-top:6px}}
.bar{{width:120px;height:6px;border-radius:3px;background:{ac};margin:16px auto 0}}
.bot{{bottom:{int(M*1.2)}px}}
ul{{list-style:none;padding:0;font-weight:500;font-size:{int(W*s.get('bullet_size', (.026 if len(s.get('bullets', [])) > 5 else .03) if square else .033))}px;line-height:{1.35 if square else 1.5}}}
li{{position:relative;padding-left:{int(W*.04)}px;margin:.12em 0}}
li:before{{content:"";position:absolute;left:0;top:.55em;width:.38em;height:.38em;border-radius:50%;background:{ac}}}
</style><div class=ph>{ph}</div>
<div class="sc t"></div><div class="sc b"></div>{logo}
{top}
{bot}"""
    chrome = next((c for c in CHROME if os.path.isfile(c)), None)
    if not chrome: sys.exit("Chrome not found")
    pathlib.Path(out_path).resolve().parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        f = pathlib.Path(td, "p.html"); f.write_text(html, encoding="utf-8")
        subprocess.run([chrome, "--headless", "--disable-gpu", "--hide-scrollbars",
                        f"--window-size={W},{H}", f"--screenshot={os.path.abspath(out_path)}",
                        "--allow-file-access-from-files", "--virtual-time-budget=1500",
                        f"--user-data-dir={pathlib.Path(td, 'profile')}", f.as_uri()], check=True, capture_output=True, timeout=45)
    if not pathlib.Path(out_path).is_file() or pathlib.Path(out_path).stat().st_size == 0:
        raise RuntimeError("browser did not produce a nonempty PNG")
    print(out_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Render a product photo poster with Chrome/Chromium")
    parser.add_argument("spec", help="JSON specification")
    parser.add_argument("output", help="output PNG path")
    args = parser.parse_args()
    try:
        main(args.spec, args.output)
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        parser.exit(1, str(exc) + "\n")
