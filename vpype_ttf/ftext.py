import freetype

import click
import numpy as np
import vpype as vp
import vpype_cli

from vpype_cli.types import LayerType,LengthType

ON_CURVE_POINT = 1

@click.command()
@click.argument("filename",type=vpype_cli.PathType(exists=True))
@click.argument("text",type=str)
@click.option(
    "-s",
    "--size",
    type=LengthType(),
    default=18,
    help="Text size (default: 18)."
)
@click.option(
    "-l",
    "--layer",
    type=LayerType(accept_new=True),
    default=1,
    help="Layer for text (default: 1)."
)
@vpype_cli.global_processor

def ftext(document: vp.Document, layer: int, filename: str, text: str, size: float):
    """
    Load a TrueType Font (TTF) file for text generation.
    """
    target_layer = vpype_cli.single_to_layer_id(layer, document)

    face = freetype.Face(filename)
    resolution_factor = 1024
    font_size = size
    interpolation_points = 50

    # Set the font size in pixels
    face.set_char_size(resolution_factor)

    pen = freetype.Vector()
    x_position = 0
    y_position = 0
    lc = vp.LineCollection()

    is_first_in_line = True

    old_character = any

    for character in text:
        if face.has_kerning:
          if is_first_in_line:
              is_first_in_line = False
          else:
              kerning_vector = face.get_kerning(old_character, character);
              print(old_character, character, kerning_vector.x, kerning_vector.y)
              x_position += kerning_vector.x
              y_position += kerning_vector.y
        old_character = character
        face.load_char(character)
        slot = face.glyph
        outline = slot.outline
        start, end = 0, 0


        for contour in range(len(outline.contours)):
            # see https://github.com/opentypejs/opentype.js/blob/c37fcdfbd89c1bd0aac1cecb2b287dfb7d00cee0/src/tables/glyf.js#L214
            verts = []
            end = outline.contours[contour]
            points = [(outline.points[p][0] + 1j * outline.points[p][1], outline.tags[p]) for p in range(start, end+1)]
            start = end + 1
            curr = points[-1]
            next = points[0]

            if curr[1] & 1:
                verts.append(curr[0])
            else:
                if next[1] & ON_CURVE_POINT:
                    verts.append(next[0])
                else:
                    verts.append((curr[0] + next[0]) / 2)

            for i in range(len(points)):
                curr = next
                next = points[(i + 1) % len(points)]

                if curr[1] & ON_CURVE_POINT:
                    verts.append(curr[0])

                else:
                    next2 = next[0]
                    if not next[1] & ON_CURVE_POINT:
                        next2 = (curr[0] + next[0]) / 2

                    # Quadratic bezier?
                    t = np.linspace(0, 1, interpolation_points)
                    p0 = verts[-1]
                    p1 = curr[0]
                    p2 = next2
                    n_pos = 1 - t
                    pos_2 = t * t
                    n_pos_2 = n_pos * n_pos
                    n_pos_pos = n_pos * t

                    ps = n_pos_2 * p0 + 2 * n_pos_pos * p1 + pos_2 * p2
                    verts.extend(ps)

            verts = np.array(verts, dtype="complex")
            verts += x_position + 1j * y_position
            lc.append(verts)

        dx = slot.advance.x
        dy = slot.advance.y
        x_position += dx
        y_position += dy
        pen.x += dx
        pen.y += dy

    lc.scale(font_size/resolution_factor,-font_size/resolution_factor)
    document.add(lc, target_layer)
    del pen
    del face
    return document


ftext.help_group = "Text"
