#!/usr/bin/env python3
"""
Correction du TP1 du cours de Géomatique et SIG.

Usage:

python3 tp1.py <tp_dir>

where `<tp_dir>` is the path to the directory with all student submissions.
"""

import os
import sys

from glob import glob
from argparse import ArgumentParser

import aprx


USAGE = """python tp1.py <tp_dir>"""


# Some formatting constants for printing to the console
BLACK = '\033[30m'
RED = '\033[31m'
GREEN = '\033[32m'
BLUE = '\033[34m'
MAGENTA = '\033[35m'
BOLD = '\033[1m'
END = '\033[0m'


def print_error(msg: str) -> None:
    """
    Prints a message in red bold to the console.
    """
    print(RED + BOLD + msg + END)


def print_bold(msg: str) -> None:
    """
    Prints a message in bold to the console.
    """
    print(BOLD + msg + END)


def correct_aprx(aprx_path: str) -> list[float]:
    """
    Correct an individual APRX file.
    """
    # The points for this project
    pts = 0.0

    # Open the .aprx file
    proj = aprx.Project(aprx_path)

    # Check first if there is a map which is from the MXD file.
    print(f'{BOLD}. Criteria 01:   map import{END}')
    pts01, msg01, _imported_maps = check_map_import(proj)
    print(msg01, f'{BOLD}→ {pts01} points{END}')
    pts += pts01

    print(f'{BOLD}. Criteria 02:   layout{END}')
    pts02, msg02, layouts = check_layouts(proj)
    print(msg02, f'{BOLD}→ {pts02} points{END}')
    pts += pts02

    print(f'{BOLD}. Criteria 03:   map view extent{END}')
    pts03, msg03 = check_map_view_extent(layouts)
    print(msg03, f'{BOLD}→ {pts03} points{END}')
    pts += pts03

    print(f'{BOLD}. Criteria 04:   labels for layer "Towns"{END}')
    pts04, msg04 = check_town_labels(layouts)
    print(msg04, f'{BOLD}→ {pts04} points{END}')
    pts += pts04

    print(f'{BOLD}. Criteria 05:   labels of lakes smaller than those of the cities{END}')
    pts05, msg05 = check_lake_labels(layouts)
    print(msg05, f'{BOLD}→ {pts05} points{END}')
    pts += pts05

    print(f'{BOLD}. Criteria 06:   symbol size and color for layer "Towns" changed{END}')
    pts06, msg06 = check_towns_symbol(layouts)
    print(msg06, f'{BOLD}→ {pts06} points{END}')
    pts += pts06

    print(f'{BOLD}. Criteria 07:   fill and stroke for layer "Cantons" changed{END}')
    pts07, msg07 = check_cantons_style(layouts)
    print(msg07, f'{BOLD}→ {pts07} points{END}')
    pts += pts07

    print(f'{BOLD}. Criteria 08:   stroke color and width for layer "Roads" changed{END}')
    pts08, msg08 = check_roads_style(layouts)
    print(msg08, f'{BOLD}→ {pts08} points{END}')
    pts += pts08

    print(f'{BOLD}. Criteria 09:   transparency for layer "HillshadeCH" changed{END}')
    pts09, msg09 = check_hillshade_transparency(layouts)
    print(msg09, f'{BOLD}→ {pts09} points{END}')
    pts += pts09

    print(f'{BOLD}. Criteria 10:   layer order changed{END}')
    pts10, msg10 = check_layer_order(layouts)
    print(msg10, f'{BOLD}→ {pts10} points{END}')
    pts += pts10

    print(f'{BOLD}. Total: {pts} points{END}')
    print('')

    # Close the file
    proj.close()

    return [pts01, pts02, pts03, pts04, pts05, pts06, pts07, pts08, pts09, pts10]


def check_map_import(proj: aprx.Project) -> tuple:
    """
    Verifies if the map has been imported.
    """
    maps = proj.maps

    if len(maps) == 0:
        return 0.0, f'  {RED}{BOLD}✘ No map found at all (!!!){END}', []

    # Find the candidate maps: they should start with "Layers"
    layer_maps = [m for m in maps if is_imported_map(m)]
    if len(layer_maps) == 0:
        return 0.0, f'  {RED}{BOLD}✘ No imported map found.{END}', []

    layer_maps_str = '", "'.join([l.name for l in layer_maps])

    if len(layer_maps) > 1:
        return (
            0.5,
            f'  {MAGENTA}! {len(layer_maps)} imported map found: "{layer_maps_str}"{END}',
            layer_maps
        )

    return 1.0, f'  {GREEN}✔ One imported map found: "{layer_maps_str}"{END}', layer_maps


def is_imported_map(mp: aprx.Map):
    """
    Returns True if the provided map seems to be imported.
    A map is imported if its name starts with "Layers" and it contains the 7 layers:
    towns, towns2, roads, hillshadech, cantons, lakes, dem
    """
    if not mp.name.startswith('Layers'):
        return False

    n_corresponding_layers = 0
    for lyr in mp.layers:
        if lyr.id in ('towns', 'towns2', 'roads', 'hillshadech', 'cantons', 'lakes', 'dem'):
            n_corresponding_layers += 1

    # If there are 4 or more corresponding layers, we assume is the imported map
    return n_corresponding_layers >= 4


def check_layouts(proj: aprx.Project) -> list:
    """
    Verifies if there is a layout in the project.
    """
    layouts = proj.layouts

    if len(layouts) == 0:
        return 0.0, f'  {RED}{BOLD}✘ No layout found at all (!!!){END}', layouts

    layout_names = '", "'.join([l.name for l in layouts])

    if len(layouts) > 1:
        return 0.5, f'  {MAGENTA}! {len(layouts)} layouts found: "{layout_names}"{END}', layouts

    # There is extacly one layout.
    return 1.0, f'  {GREEN}✔ One layout found: "{layout_names}"{END}', layouts


def check_map_view_extent(layouts: list[aprx.Layout]):
    """
    Checks if the map view extent is the same or not for the provided layout.
    """
    # Variable for tracking if there is a change in one of the layouts (list of booleans)
    pts, msg = [], []

    for layout in layouts:
        map_frames = layout.map_frames
        layout_msg = ''

        if len(map_frames) == 0:
            layout_msg = f'  {RED}{BOLD}✘ No map frame found in layout "{layout.name}"{END}'
            pts.append(0.0)
            continue

        if len(map_frames) > 1:
            layout_msg = f'  {MAGENTA}! Several map frames found in layout "{layout.name}"{END}'

        # Take the first map frame by default
        mf = map_frames[0]

        # Get the map extent (the MapView)
        view = mf.map_view

        # Create a MapView with the original extent.
        orig_view = aprx.MapView({
            "type": "CIMMapView",
            "viewingMode": "Map",
            "camera": {
            "type": "CIMViewCamera",
            "pitch": -90,
            "scale": 1610926.9243986572,
            "x": 659627.07655732706,
            "y": 180810.99999999642,
            "z": "NaN",
            "viewportHeight": -1,
            "viewportWidth": -1
            }
        })

        mv_change = not view.is_equal(orig_view, tolerance={ 'x': 1, 'y': 1, 'scale': 100 })
        if mv_change:
            layout_msg += ('\n' if len(layout_msg) > 0 else '') + \
                f'  {GREEN}✔ Map extent has been changed (in at least one layout)"{END}'
            pts.append(0.5 if len(map_frames) > 1 else 1.0)
        else:
            layout_msg += ('\n' if len(layout_msg) > 0 else '') + \
                f'  {RED}{BOLD}✘ Map extent did not change{END}'
            pts.append(0.0)

        msg.append(layout_msg)

    if len(pts) == 0:
        return 0.0, f'  {RED}{BOLD}✘ No layout found, map extent did not change{END}'

    max_pts = max(pts)
    max_idx = pts.index(max_pts)
    return max_pts, msg[max_idx]


def check_town_labels(layouts: list) -> (float, str):
    """
    Iterates over all layouts and checks if there is a "Towns" layer with labels on field [ID1]
    """
    ok = False
    for layout in layouts:
        mfs = layout.map_frames
        for mf in mfs:
            lyrs = mf.map.layers
            for lyr in lyrs:
                if lyr.name == 'Towns':
                    lbls = lyr.labels
                    if lbls['shown'] and lbls['expression']['value'] == '[ID1]':
                        ok = True

    if ok:
        return 1.0, f'  {GREEN}✔ Labels for layer "Towns" are shown{END}'
    else:
        return 0.0, f'  {RED}{BOLD}✘ No labels found for all layers "Towns"{END}'


def check_lake_labels(layouts: list) -> (float, str):
    """
    Iterates over all layouts and checks if there is a "Lakes" layer with labels on field [NAME],
    and for which the font size is smaller than for the labels of the "Towns" layer (on field [ID0])
    """
    # Comparison is done layout by layout. There should be at least one layout where there are
    # labels on both layers, and where the font size for the lakes layer is smaller.
    pts, msg = [], []
    for layout in layouts:
        mfs = layout.map_frames
        for mf in mfs:
            lyrs = mf.map.layers
            # Set a default value for the font size of 0.
            fsize = { 'Towns': 0, 'Lakes': 0 }
            # Get the font sizes of the "Towns" layers and the "Lakes" layer.
            for lyr in lyrs:
                if lyr.name == 'Towns':
                    lbls = lyr.labels
                    if lbls['shown'] and lbls['expression']['value'] == '[ID1]':
                        fsize['Towns'] = lbls['font']['size']

                if lyr.name == 'Lakes':
                    lbls = lyr.labels
                    if lbls['shown'] and lbls['expression']['value'] == '[NAME]':
                        fsize['Lakes'] = lbls['font']['size']

            # Compute the points we should give this map frame
            if fsize['Towns'] > 0 and fsize['Lakes'] > 0 and fsize['Lakes'] < fsize['Towns']:
                # This gives all points, just return 1
                msg = f'  {GREEN}✔ Labels for "Towns" and "Lakes" shown, "Lakes" smaller than "Towns".{END}'
                return 1.0, msg

            if fsize['Towns'] > 0 and fsize['Lakes'] > 0:
                # Labels for towns and lakes shown, but label for lakes is not smaller
                msg.append(f'  {MAGENTA}! Labels for "Towns" and "Lakes" shown, but "Lakes" not smaller than "Towns".{END}')
                pts.append(0.5)
            elif fsize['Lakes'] == 0:
                msg.append(f'  {BOLD}{RED}✘ Labels for "Lakes" not shown.{END}')
                pts.append(0.0)
            elif fsize['Lakes'] > 0 and fsize['Towns'] == 0:
                msg.append(f'  {MAGENTA}! Labels for "Lakes" shown, but not for the "Towns".{END}')
                pts.append(0.5)
            else:
                msg.append(f'  {BOLD}{RED}✘ Labels for "Lakes" not shown.{END}')
                pts.append(0.0)

    if len(pts) == 0:
        return 0.0, f'  {BOLD}{RED}✘ Labels for "Lakes" not found.{END}'

    max_pts = max(pts)
    max_idx = pts.index(max_pts)

    return max_pts, msg[max_idx]


def check_towns_symbol(layouts: list) -> (float, str):
    """
    Iterates over all layouts and checks if there is a "Towns" layer where the symbol is different
    than in the original MXD.
    """
    # Comparison is done layout by layout.
    pts, msg = [], []
    for layout in layouts:
        mfs = layout.map_frames
        for mf in mfs:
            lyrs = mf.map.layers
            for lyr in lyrs:
                if lyr.name == 'Towns':
                    lyr_pts, lyr_msg = [], []

                    symb = lyr.symbol
                    if symb is None:
                        pts.append(0.0)
                        msg.append(f'  {BOLD}{RED}✘ No symbol for layer "Towns" found{END}')
                        continue

                    ref_size, ref_col = None, None
                    if symb['type'] == 'CIMVectorMarker':
                        ref_size, ref_col = 4, aprx.RGBA(133, 0, 44, 100)
                    if symb['type'] == 'CIMCharacterMarker':
                        ref_size, ref_col = 16, aprx.RGBA(76, 230, 0, 100)

                    if symb['size'] == ref_size:
                        lyr_pts.append(0.0)
                        lyr_msg.append(f'  {BOLD}{RED}✘ Symbol size not changed{END}')
                    else:
                        lyr_pts.append(0.5)
                        lyr_msg.append(f'  {GREEN}✔ Symbol size changed{END}')

                    if ref_col.is_equal(symb['color']):
                        lyr_pts.append(0.0)
                        lyr_msg.append(f'  {BOLD}{RED}✘ Symbol color not changed{END}')
                    else:
                        lyr_pts.append(0.5)
                        lyr_msg.append(f'  {GREEN}✔ Symbol color changed{END}')

                    pts.append(sum(lyr_pts))
                    msg.append('\n'.join(lyr_msg))

    if len(pts) == 0:
        return 0.0, f'  {BOLD}{RED}✘ No candidate layer found{END}'

    max_pts = max(pts)
    max_idx = pts.index(max_pts)

    return max_pts, msg[max_idx]


def check_cantons_style(layouts: list) -> (float, str):
    """
    Iterates over all layouts and checks if there is a "Cantons" layer where the symbol is different
    than in the original MXD.
    """
    # Comparison is done layout by layout.
    pts, msg = [], []
    for layout in layouts:
        mfs = layout.map_frames
        for mf in mfs:
            lyrs = mf.map.layers
            for lyr in lyrs:
                if lyr.name == 'Cantons':
                    lyr_pts, lyr_msg = [], []

                    stl = lyr.style
                    if stl is None:
                        pts.append(0.0)
                        msg.append(f'  {BOLD}{RED}✘ No style for layer "Cantons" found{END}')
                        continue

                    ref_width = 2
                    ref_col = aprx.RGBA(255, 190, 190, 100)

                    if stl['stroke'] is None or stl['stroke']['width'] != ref_width:
                        lyr_pts.append(0.5)
                        lyr_msg.append(f'  {GREEN}✔ Stroke width changed{END}')
                    else:
                        lyr_pts.append(0.0)
                        lyr_msg.append(f'  {BOLD}{RED}✘ Stroke width not changed{END}')

                    if stl['fill'] is None or not ref_col.is_equal(stl['fill']['color']):
                        lyr_pts.append(0.5)
                        lyr_msg.append(f'  {GREEN}✔ Fill color changed{END}')
                    else:
                        lyr_pts.append(0.0)
                        lyr_msg.append(f'  {BOLD}{RED}✘ Fill color not changed{END}')

                    pts.append(sum(lyr_pts))
                    msg.append('\n'.join(lyr_msg))

    if len(pts) == 0:
        return 0.0, f'  {BOLD}{RED}✘ No candidate layer found{END}'

    max_pts = max(pts)
    max_idx = pts.index(max_pts)

    return max_pts, msg[max_idx]


def check_roads_style(layouts: list) -> (float, str):
    """
    Iterates over all layouts and checks if there is a "Roads" layer where the stroke width and
    color is different from the original MXD.
    """
    # Comparison is done layout by layout.
    pts, msg = [], []
    for layout in layouts:
        mfs = layout.map_frames
        for mf in mfs:
            lyrs = mf.map.layers
            for lyr in lyrs:
                if lyr.name == 'Roads':
                    lyr_pts, lyr_msg = [], []

                    stl = lyr.style
                    if stl is None:
                        pts.append(0.0)
                        msg.append(f'  {BOLD}{RED}✘ No style for layer "Roads" found{END}')
                        continue

                    ref_width = 1
                    ref_col = aprx.RGBA(156, 156, 156, 100)

                    if stl['stroke'] is None:
                        lyr_pts.append(0.0)
                        lyr_msg.append(f'  {BOLD}{RED}✘ No stroke style found{END}')
                    else:
                        if stl['stroke']['width'] != ref_width:
                            lyr_pts.append(0.5)
                            lyr_msg.append(f'  {GREEN}✔ Stroke width changed{END}')
                        else:
                            lyr_pts.append(0.0)
                            lyr_msg.append(f'  {BOLD}{RED}✘ Stroke width not changed{END}')

                        if not ref_col.is_equal(stl['stroke']['color']):
                            lyr_pts.append(0.5)
                            lyr_msg.append(f'  {GREEN}✔ Stroke color changed{END}')
                        else:
                            lyr_pts.append(0.0)
                            lyr_msg.append(f'  {BOLD}{RED}✘ Stroke color not changed{END}')

                    pts.append(sum(lyr_pts))
                    msg.append('\n'.join(lyr_msg))

    if len(pts) == 0:
        return 0.0, f'  {BOLD}{RED}✘ No candidate layer found{END}'

    max_pts = max(pts)
    max_idx = pts.index(max_pts)

    return max_pts, msg[max_idx]


def check_hillshade_transparency(layouts: list) -> (float, str):
    """
    Iterates over all layouts and checks if there is a "HillshadeCH" layer where the transparency
    is different from the original MXD.
    """
    # Comparison is done layout by layout.
    pts, msg = [], []
    for layout in layouts:
        mfs = layout.map_frames
        for mf in mfs:
            lyrs = mf.map.layers
            for lyr in lyrs:
                if lyr.name == 'HillShadeCH':
                    lyr_pts, lyr_msg = [], []

                    transparency = lyr.json.get('transparency', None)

                    if transparency is None:
                        lyr_pts.append(0.0)
                        lyr_msg.append(f'  {BOLD}{RED}✘ No transparency found{END}')
                        continue

                    if transparency != 30:
                        lyr_pts.append(1.0)
                        lyr_msg.append(f'  {GREEN}✔ Transparency changed{END}')
                    else:
                        lyr_pts.append(0.0)
                        lyr_msg.append(f'  {BOLD}{RED}✘ Transparency not changed{END}')

                    pts.append(sum(lyr_pts))
                    msg.append('\n'.join(lyr_msg))

    if len(pts) == 0:
        return 0.0, f'  {BOLD}{RED}✘ No candidate layer found{END}'

    max_pts = max(pts)
    max_idx = pts.index(max_pts)

    return max_pts, msg[max_idx]


def check_layer_order(layouts: list) -> (float, str):
    """
    Check if the order of the layers has changed in one of the layouts.
    """
    orig_order = [
        "CIMPATH=layers/towns.json",
        "CIMPATH=layers/towns2.json",
        "CIMPATH=layers/lakes.json",
        "CIMPATH=layers/hillshadech.json",
        "CIMPATH=layers/roads.json",
        "CIMPATH=layers/cantons.json",
        "CIMPATH=layers/dem.json"
    ]

    for layout in layouts:
        mfs = layout.map_frames
        for mf in mfs:
            mp = mf.map
            lyrs_json = mp.json.get('layers', [])
            if lyrs_json != orig_order:
                return 1.0, f'  {GREEN}✔ Order of layers changed{END}'

    return 0.0, f'  {BOLD}{RED}✘ Order of layers has not changed{END}'


def main(tp_dir: str, result_file: str):
    """
    Evaluates the ArcGIS project files in `tp_dir`. The directory needs to have a subfolder for
    each submission, and inside the subfolder a .aprx file.
    """
    print('--- START CORRECTIONS ---\n')

    basedir = os.path.abspath(tp_dir)

    # Get all the subdirectories
    student_dirs = [d for d in os.listdir(basedir) if os.path.isdir(os.path.join(basedir, d))]
    print(f'Number of subdirectories found: {len(student_dirs)}\n')

    # Make the correction in alphabetical order
    student_dirs.sort()

    # Write the points to a TSV file
    f = open(result_file, 'w', encoding='utf-8')
    f.write('Student\tc01\tc02\tc03\tc04\tc05\tc06\tc07\tc08\tc09\tc10\ttot\n')

    # Go through every student directory and start the correction for each of them.
    for st_dir in student_dirs:
        st = st_dir.split('_')[0]
        print(f'Correction for {st}:')

        # Is there an .aprx file in the student submission ?
        aprx_files = glob(os.path.join(basedir, st_dir, '*.aprx'))

        if len(aprx_files) == 0:
            print_error(' . No APRX file found. Skipping.\n')
            continue
        elif len(aprx_files) > 1:
            print_error(f' . Several APRX files found. "{aprx_files[0]}" will be used.')

        pts = correct_aprx(os.path.join(basedir, st_dir, aprx_files[0]))
        pts_str = '\t'.join([f'{p:.1f}' for p in pts])
        pts_tot = sum(pts)
        f.write(f'{st}\t{pts_str}\t{pts_tot}\n')

    f.close()


if __name__ == '__main__':
    parser = ArgumentParser(
        prog='tp1.py',
        description="Correction automatique du TP1 de Géomatique & SIG"
    )
    parser.add_argument(
        'tp_dir',
        metavar='<TP_DIR>',
        help="Chemin vers le dossier avec l'ensemble des soumissions"
    )
    parser.add_argument(
        'result_file',
        metavar='<RESULT_FILE>',
        help="Chemin vers le fichier avec les résultats"
    )
    args = parser.parse_args()
    if args.tp_dir is None:
        print(USAGE)
        sys.exit(0)

    main(args.tp_dir, args.result_file)
