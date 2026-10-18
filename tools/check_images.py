#!/usr/bin/env python3
"""Fail on photos that decode but show nothing: a blank or near-uniform picture, such as a soft mask
or an empty layer pulled out of the PDF by mistake. Run it after adding or re-cropping photos."""
import glob
import sys

from PIL import Image, ImageStat

ROOT = __file__.rsplit('/tools/', 1)[0]
SKIP = ('swatches/',)  # a flat colour swatch is meant to be uniform
bad = []
for f in sorted(glob.glob(f'{ROOT}/assets/img/**/*.jpg', recursive=True) + glob.glob(f'{ROOT}/portfolio/img/*.jpg')):
    if any(s in f for s in SKIP):
        continue
    try:
        im = Image.open(f)
        im.load()
        sd = ImageStat.Stat(im.convert('L')).stddev[0]
    except Exception as ex:
        bad.append(f'{f}: does not decode ({ex})')
        continue
    if sd < 12:
        bad.append(f'{f}: looks blank (grey spread {sd:.1f})')
print('\n'.join(bad) or 'all photos look fine')
sys.exit(1 if bad else 0)
