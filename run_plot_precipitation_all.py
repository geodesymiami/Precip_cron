#!/usr/bin/env python3

import os
import argparse
import matplotlib.pyplot as plt
from precip.cli import get_precipitation_lalo
import pandas as pd

# This is needed to run on a server without a display
import matplotlib
matplotlib.use('Agg')

PRECIP_HOME = os.environ.get('PRECIP_HOME')
SCRATCH_DIR = os.environ.get('SCRATCHDIR')
VOLCANO_FILE = PRECIP_HOME + '/src/precip/Holocene_Volcanoes_precip_cfg..xlsx'
DEFAULT_STYLES = ['map', 'bar', 'annual', 'strength']

EXAMPLES = """
Examples:

Plot all styles for all volcanoes:
    run_plot_precipitation_all.py --period 20060101:20070101

Plot all volcanoes with a different plot directory:
    run_plot_precipitation_all.py --plot-dir .
    run_plot_precipitation_all.py --plot-dir /path/to/plot_dir

Plot with a different volcano file:
    run_plot_precipitation_all.py --volcano-file /path/to/volcano_file.xlsx

Plot with different styles:
    run_plot_precipitation_all.py --styles map bar

get_precipitation_lalo --help for more options
"""

def create_parser():
    synopsis = 'Wrapper tool to run get_precipitation_lalo with multiple styles and all volcanoes'
    parser = argparse.ArgumentParser(
        description=synopsis,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=EXAMPLES
    )
    parser.add_argument('--volcano-file',
                        default=VOLCANO_FILE,
                        metavar='',
                        help='File with volcano names (default: %(default)s)')
    parser.add_argument('--plot-dir',
                        default=PRECIP_HOME,
                        help='Directory to save plots (default: %(default)s)')
    parser.add_argument('--styles',
                        nargs='+',
                        default=DEFAULT_STYLES,
                        help='List of plot styles to use (default: %(default)s)')
    return parser

def get_volcanoes():
    df = pd.read_excel(VOLCANO_FILE, skiprows=1)
    df = df[df['Precip'] != False]

    volcano_dict = {
        r['Volcano Name'] : {
            'id': r['Volcano Number']
        } for _, r in df.iterrows()}

    return volcano_dict

def clean_string(string):
    string = string.replace(' ', '_')
    string = string.replace(',', '')
    return string

def main():
    parser = create_parser()
    args, unknown_args = parser.parse_known_args()

    plot_dir = os.path.join(args.plot_dir, 'precip_plots')
    os.makedirs(plot_dir, exist_ok=True)

    volcano_dict = get_volcanoes()
    list_failed = []

    for volcano, info in volcano_dict.items():
        id = info['id']
        volcano_dir = os.path.join(plot_dir, str(id))
        os.makedirs(volcano_dir, exist_ok=True)
        for style in args.styles:
            inps = argparse.Namespace(style=style, name=[volcano], no_show=True)
            try:
                get_precipitation_lalo.main(unknown_args, inps)
            except (IndexError, ValueError) as e:
                list_failed.append(volcano)
                continue
            png_path = os.path.join(volcano_dir, f'{id}_{style}.png')
            plt.savefig(png_path)
            print('#'*50)
            print(f'{'#'*50}\nSaved {png_path}')

    print('#'*50)
    print(f'Failed to plot for the following volcanoes: {list_failed}')

if __name__ == '__main__':
    main()
