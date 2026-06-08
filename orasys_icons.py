#!/usr/bin/env python3
"""
OraSys Desk - Generation et placement des icones pour tous les OS.
Lit le fichier master 'orasys_master.png' (a la racine du repo) et place
les icones aux bons emplacements pour Windows / macOS / Linux / Android.
Concu pour tourner dans le workflow GitHub Actions avant la compilation.
Robuste : si un chemin n'existe pas, on l'ignore avec un avertissement.
"""
import os, sys, glob

try:
    from PIL import Image
except ImportError:
    os.system(f"{sys.executable} -m pip install --quiet pillow")
    from PIL import Image

ROOT = os.getcwd()
MASTER = os.path.join(ROOT, "orasys_master.png")

if not os.path.exists(MASTER):
    print(f"[ERREUR] master introuvable: {MASTER}")
    sys.exit(0)  # ne casse pas le build

master = Image.open(MASTER).convert("RGBA")
print(f"[OK] master charge: {master.size}")

def save_png(size, dest):
    d = os.path.dirname(dest)
    if d and not os.path.isdir(d):
        print(f"[skip] dossier absent: {d}")
        return False
    master.resize((size, size), Image.LANCZOS).save(dest)
    print(f"[png] {dest} ({size}px)")
    return True

def replace_existing(path, size):
    """Remplace un fichier png seulement s'il existe deja."""
    if os.path.exists(path):
        master.resize((size, size), Image.LANCZOS).save(path)
        print(f"[repl] {path} ({size}px)")
        return True
    return False

# ---------- WINDOWS : app_icon.ico ----------
win_ico = os.path.join(ROOT, "flutter", "windows", "runner", "resources", "app_icon.ico")
if os.path.isdir(os.path.dirname(win_ico)):
    sizes = [16, 24, 32, 48, 64, 128, 256]
    imgs = [master.resize((s, s), Image.LANCZOS) for s in sizes]
    imgs[0].save(win_ico, sizes=[(s, s) for s in sizes], append_images=imgs[1:])
    print(f"[ico] {win_ico}")
else:
    print(f"[skip] {win_ico}")

# ---------- LINUX / res : png standard ----------
for size, name in [(32,"32x32.png"),(64,"64x64.png"),(128,"128x128.png"),(256,"128x128@2x.png")]:
    replace_existing(os.path.join(ROOT, "res", name), size)
# logo generique eventuel
replace_existing(os.path.join(ROOT, "res", "icon.png"), 512)
# flutter assets (logo in-app si present)
for p in glob.glob(os.path.join(ROOT, "flutter", "assets", "*.png")):
    if os.path.basename(p).lower() in ("icon.png", "logo.png"):
        replace_existing(p, 512)

# ---------- macOS : AppIcon.appiconset ----------
mac_dir = os.path.join(ROOT, "flutter", "macos", "Runner", "Assets.xcassets", "AppIcon.appiconset")
if os.path.isdir(mac_dir):
    # remplace tous les png existants en deduisant leur taille du nom si possible
    mac_sizes = {
        "app_icon_16.png":16, "app_icon_32.png":32, "app_icon_64.png":64,
        "app_icon_128.png":128, "app_icon_256.png":256, "app_icon_512.png":512,
        "app_icon_1024.png":1024,
    }
    for f in os.listdir(mac_dir):
        if f.endswith(".png"):
            sz = mac_sizes.get(f)
            if sz is None:
                # tente d'extraire un nombre du nom
                import re
                m = re.search(r"(\d+)", f)
                sz = int(m.group(1)) if m else 512
            master.resize((sz, sz), Image.LANCZOS).save(os.path.join(mac_dir, f))
            print(f"[mac] {f} ({sz}px)")
else:
    print(f"[skip] {mac_dir}")

# ---------- ANDROID : mipmaps ----------
android_res = os.path.join(ROOT, "flutter", "android", "app", "src", "main", "res")
android_densities = {
    "mipmap-mdpi":48, "mipmap-hdpi":72, "mipmap-xhdpi":96,
    "mipmap-xxhdpi":144, "mipmap-xxxhdpi":192,
}
if os.path.isdir(android_res):
    for dens, sz in android_densities.items():
        ddir = os.path.join(android_res, dens)
        if os.path.isdir(ddir):
            for f in os.listdir(ddir):
                if f.endswith(".png") and "ic_launcher" in f:
                    master.resize((sz, sz), Image.LANCZOS).save(os.path.join(ddir, f))
                    print(f"[android] {dens}/{f} ({sz}px)")
else:
    print(f"[skip] {android_res}")

print("[TERMINE] generation des icones OraSys Desk")
