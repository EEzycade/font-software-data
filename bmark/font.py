from .svg import convert_from_image, remove_zigzags, get_height, stretch_char, to_str
from .merge_font import merge_font

import os
import sys
import pkg_resources
import fontTools.svgLib.path as svg_path
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen
import PIL.Image
import yaml
import numpy as np
try:
    # Use tqdm if installed
    from tqdm import tqdm
except ImportError:
    # But don't throw an error if not
    def tqdm(it): return it


def __main__():
    if len(sys.argv) < 2:
        print("Please pass the file directory path containing the svgs you want to create a font with as an argument!")
        return

    create(sys.argv[1])


def create(path, svg_path, font_path):
    char_types = yaml.safe_load(
        pkg_resources.resource_stream(__name__, "character-types.yaml")
        #    open(pkg_resources.get_resource_filename(__name__, "character-types.yaml"))
        #open(_os.join(_file__, "character-types.yaml"))
    )

    svgs = {}
    for filename in tqdm([
        filename for filename in os.listdir(path)
        if filename.split(".")[-1] in ["jpeg", "jpg", "png"]
        # there's gotta be a better way
    ]):
        char = filename.split(".")[0]
        input_path = f"{path}/{filename}"
        img = PIL.Image.open(input_path)
        img = img.transpose(PIL.Image.FLIP_TOP_BOTTOM)

        svgs[char] = convert_from_image(img)
        remove_zigzags(svgs[char])

    height_data = {char_type: [] for char_type in char_types.values()}
    for char, svg in svgs.items():
        height = get_height(svg)
        if np.isfinite(height):
            height_data[char_types[char[0]]].append(height)
        else:
            print(
                f"Warning! Character {char[0]} has an invalid height: {height}. Check unboxed image.")

    tall_upper = sum(height_data["tall"]) / \
        len(height_data["tall"]) if height_data["tall"] else 1
    small_upper = sum(
        height_data["small"]) / len(height_data["small"]) if height_data["small"] else 1
    desc_lower = (  # calculate average underhand taking base height into account
        (
            small_upper * len(height_data["descender"])
            + tall_upper * len(height_data["tall-descender"])
            - sum(height_data["descender"])
            - sum(height_data["tall-descender"])
        ) / (
            len(height_data["descender"])
            + len(height_data["tall-descender"])
        )
    ) if height_data["descender"] or height_data["tall-descender"] else 1

    scale_factor = 200 / tall_upper
    tall_upper *= scale_factor
    small_upper *= scale_factor
    desc_lower *= scale_factor

    for char, svg in svgs.items():
        char_type = char_types[char[0]]
        stretch_char(
            svg,
            lower=desc_lower if "descender" in char_type else 0.0,
            upper=tall_upper if "tall" in char_type else small_upper,
        )

        if svg:
            with open(os.path.join(svg_path, char+".svg"), "w") as file:
                file.write(to_str(svg, 200, 200))
        else:
            print(f"Warning! SVG {char}.svg is empty.")

    font = create_from_svgs(svg_path, font_path)
    print(f"Font complete: '{font_path}'")


def create_from_svgs(path, font_path):
    default_char = default_charstr()
    char_strings = {
        ".notdef": default_char,
        ".null": default_char,
        "space": draw_blank(),
    }

    glyph_order = [".notdef", ".null", "space"]
    char_map = {32: "space"}

    for filename in os.listdir(path):
        if filename.split(".")[-1] == "svg":
            char_string = draw_charstr(os.path.join(path, filename))
            char = filename.split('.')[0][0]
            char_strings[char] = char_string
            glyph_order.append(char)
            char_map[ord(char)] = char
    assert len(glyph_order) > 3, f"{path} does not contain any svgs"

    fb = FontBuilder(300, isTTF=False)
    fb.setupGlyphOrder(glyph_order)
    fb.setupCharacterMap(char_map)

    family_name = "GeneratedFont"
    style_name = "Test"
    version = "0.1"

    name_strings = dict(
        uniqueFontIdentifier="fontBuilder: " + family_name + "." + style_name,
        fullName=family_name + "-" + style_name,
        psName=family_name + "-" + style_name,
        version="Version " + version,
    )

    fb.setupCFF(name_strings["psName"], {
                "FullName": name_strings["psName"]}, char_strings, {})
    box = {gn: cs.calcBounds(None) for gn, cs in char_strings.items()}
    metrics = {}
    for char in char_strings:
        # width, left-bound
        metrics[char] = (box[char][2] + 20, -10)
    metrics["space"] = (120, 0)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=225, descent=-75)
    fb.setupNameTable(name_strings)
    fb.setupOS2(sTypoAscender=225, sTypoDescender=-75)
    fb.setupPost()
    fb.save(font_path)


# create char string to use in otf file from svg
def draw_charstr(filename):
    pen = T2CharStringPen(200, None)
    svg = svg_path.SVGPath(filename)
    svg.draw(pen)

    return pen.getCharString()


def draw_blank():
    pen = T2CharStringPen(200, None)
    pen.moveTo((0, 0))
    pen.closePath()
    return pen.getCharString()


# default char string; currently a placeholder
def default_charstr():
    pen = T2CharStringPen(200, None)
    pen.moveTo((0, 0))
    pen.lineTo((200, 0))
    pen.lineTo((200, 200))
    pen.lineTo((0, 200))
    pen.closePath()
    return pen.getCharString()


if __name__ == "__main__":
    __main__()
