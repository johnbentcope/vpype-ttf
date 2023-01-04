import click
import numpy as np
import vpype as vp
import vpype_cli
import freetype


@click.command()
@click.argument("filename", type=vpype_cli.PathType(exists=True))
@click.argument("text", type=str)
@vpype_cli.global_processor
def render(document: vp.Document, filename: str, text: str):
    face = freetype.Face(filename)
    resolution_factor = 1024
    font_size = 16 # 16px = 12pt

    # Set the font size in pixels
    face.set_char_size(resolution_factor * 96)

    pen = freetype.Vector()
    x_position = 0
    y_position = 0
    for character in text:
        lc = vp.LineCollection()
        face.load_char(character)
        slot = face.glyph
        outline = slot.outline
        start, end = 0, 0
        for contour in range(len(outline.contours)):
            # print(f"New Contour: {contour}")
            verts = []
            end = outline.contours[contour]
            points = outline.points[start:end + 1]
            tags = outline.tags[start:end + 1]
            points.append(points[0])
            tags.append(tags[0])
            start = end + 1
            segments = [[points[0], ], ]
            for j in range(0, len(points)):
                segments[-1].append(points[j])
                if tags[j] & 1:
                    segments.append([points[j], ])

            for segment in segments:
                if len(segment) == 3:
                    t = np.linspace(0, 1, 50)
                    x0, y0 = segment[0]
                    x1, y1 = segment[1]
                    x2, y2 = segment[2]
                    n_pos = 1 - t
                    pos_2 = t * t
                    n_pos_2 = n_pos * n_pos
                    n_pos_pos = n_pos * t

                    xs = n_pos_2 * x0 + 2 * n_pos_pos * x1 + pos_2 * x2
                    ys = n_pos_2 * y0 + 2 * n_pos_pos * y1 + pos_2 * y2
                    verts.extend(xs + 1j * ys)
                elif len(segment) == 4:
                    x0, y0 = segment[0]
                    x1, y1 = segment[1]
                    x2, y2 = segment[2]
                    x3, y3 = segment[3]
                    t = np.linspace(0, 1, 50)
                    pos_3 = t * t * t
                    n_pos = 1 - t
                    n_pos_3 = n_pos * n_pos * n_pos
                    pos_2_n_pos = t * t * n_pos
                    n_pos_2_pos = n_pos * n_pos * t
                    xs = n_pos_3 * x0 + 3 * (n_pos_2_pos * x1 + pos_2_n_pos * x2) + pos_3 * x3
                    ys = n_pos_3 * y0 + 3 * (n_pos_2_pos * y1 + pos_2_n_pos * y2) + pos_3 * y3
                    verts.extend(xs + 1j * ys)
                elif len(segment) == 2:
                    x, y = segment[-1]
                    verts.append(x + 1j * y)
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
        document.add(lc)
    del pen
    del face
    return document


render.help_group = "Text"
