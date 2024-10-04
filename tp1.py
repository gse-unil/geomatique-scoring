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


def correct_aprx(aprx_path: str) -> None:
    """
    Correct an individual APRX file.
    """
    # Open the .aprx file
    proj = aprx.Project(aprx_path)

    # Check first if there is a map which is from the MXD file.
    _imported_maps = check_map_import(proj)

    # Close the file
    proj.close()


def check_map_import(proj: aprx.Project) -> list:
    """
    Verifies if the map has been imported.
    """
    print(f'{BOLD}. Criteria 01:   map import{END}')
    maps = proj.maps

    if len(maps) == 0:
        print(f'  {RED}{BOLD}✘ No map found at all (!!!){END}\n')
        return []

    # Find the candidate maps: they should start with "Layers"
    layer_maps = [m for m in maps if is_imported_map(m)]
    if len(layer_maps) == 0:
        print(f'  {RED}{BOLD}✘ No imported map found.{END}')

    layer_maps_str = '", "'.join([l.name for l in layer_maps])

    if len(layer_maps) == 1:
        print(f'  {GREEN}✔ One imported map found: "{layer_maps_str}"{END}')
    if len(layer_maps) > 1:
        print(f'  {MAGENTA}! {len(layer_maps)} imported map found: "{layer_maps_str}"{END}')

    print('')

    return layer_maps


def is_imported_map(mp: aprx.ProjectItem):
    """
    Returns True if the provided map seems to be imported.
    A map is imported if its name starts with "Layers" and it contains the 7 layers:
    towns, towns2, roads, hillshadech, cantons, lakes, dem
    """
    if not mp.name.startswith('Layers'):
        return False

    lyrs = mp.layers()
    n_corresponding_layers = 0
    for lyr in lyrs:
        if lyr.id in ('towns', 'towns2', 'roads', 'hillshadech', 'cantons', 'lakes', 'dem'):
            n_corresponding_layers += 1

    # If there are 4 or more corresponding layers, we assume is the imported map
    return n_corresponding_layers >= 4


def main(tp_dir: str):
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

    # Go through every student directory and start the correction for each of them.
    for st_dir in student_dirs:
        print(f'Correction for "{st_dir}":')

        # Is there an .aprx file in the student submission ?
        aprx_files = glob(os.path.join(basedir, st_dir, '*.aprx'))

        if len(aprx_files) == 0:
            print_error(' . No APRX file found. Skipping.\n')
            continue
        elif len(aprx_files) > 1:
            print_error(f' . Several APRX files found. "{aprx_files[0]}" will be used.')

        correct_aprx(os.path.join(basedir, st_dir, aprx_files[0]))



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
    args = parser.parse_args()
    if args.tp_dir is None:
        print(USAGE)
        sys.exit(0)

    main(args.tp_dir)
