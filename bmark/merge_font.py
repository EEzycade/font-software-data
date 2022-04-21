import argparse
from fontTools import ttLib, subset, merge
from subprocess import run
from uuid import uuid4
import shutil
import os
from .scale_font import main as scale_font
from .otf2ttf import main as otf2ttf

def merge_font(main_file, default_file, output_file=None):
    tmp1 = "tmp-" + str(uuid4())
    tmp2 = "tmp-" + str(uuid4())
    tmp3 = "tmp-" + str(uuid4())
    if default_file.endswith("otf"):
        otf2ttf(["-o=" + tmp1, main_file])
    elif default_file.endswith("ttf"):
        shutil.copy(default_file, tmp1)
    else: assert False
    if main_file.endswith("otf"):
        otf2ttf(["-o=" + tmp2, main_file])
    elif main_file.endswith("ttf"):
        shutil.copy(main_file, tmp2)
    else: assert False

    if output_file is None:
        output_file = main_file

    default_font = ttLib.TTFont(tmp1)
    main_font = ttLib.TTFont(tmp2)
    missing_chars = set(default_font.getGlyphOrder()) - set(main_font.getGlyphOrder())

    subset.main([tmp1, "--glyphs=" + ",".join(missing_chars), "--output-file=" + tmp3])
    scale_font([tmp2, str(default_font["head"].unitsPerEm), "--output=" + tmp2])
    merge.main([tmp3, tmp2, "--output-file=" + output_file])
    for f in [tmp1, tmp2, tmp3]:
        os.remove(f)

