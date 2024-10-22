#!/usr/bin/env python3
"""
Correction du TP1 du cours de Géomatique et SIG.

Usage:

python3 tp3.py <tp_dir>

where `<tp_dir>` is the path to the directory with all student submissions.
"""

import json
import os
import re
import sys

from glob import glob
from argparse import ArgumentParser

import aprx


USAGE = """python tp3.py <tp_dir>"""

# Read first the list of criteria
with open('tp3-criteria.json', 'r', encoding='utf-8') as f:
    CRITERIA = json.loads(f.read())


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


def eval_c01(proj) -> tuple:
    return 1, 'no message', {}


def correct_submission(aprx_path: str, gdb_path: str) -> list[float]:
    """
    Correct an individual submission.
    """
    # The points for this project
    pts_sum = 0.0
    pts_lst = []

    # Open the .aprx file and the Geodatabase
    proj = aprx.Project(aprx_path)

    # Iterate over all criteria:
    for crit_id, crit in CRITERIA.items():
        m = re.search(r'[0-9]+[a-zA-Z]*', crit_id)
        crit_no = m.group()
        crit_title = crit.get('title', 'Untitled')
        print(f'{BOLD}. Criteria {crit_no}:   {crit_title}{END}')
        pts_crit, msg_crit, opts = eval_c01(proj)
        print(msg_crit, f'{BOLD}→ {pts_crit} points{END}')
        pts_sum += pts_crit
        pts_lst.append(pts_crit)

    print(f'{BOLD}. Total: {pts_sum} points{END}')
    print('')

    # Close the file
    proj.close()

    return pts_lst




def main(tp_dir: str, result_file: str):
    """
    Evaluates the Geodatabase and ArcGIS project files in `tp_dir`.
    The directory needs to have a subfolder for each submission, and inside the subfolder a .aprx
    file and a .gdb directory. The Geodatabase can be a ZIP archive.
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

        pts = correct_submission(
            aprx_path = os.path.join(basedir, st_dir, aprx_files[0]),
            gdb_path = 'oups'
        )

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
