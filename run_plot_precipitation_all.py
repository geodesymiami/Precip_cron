#!/usr/bin/env python3

from itertools import product
import os
import argparse
import matplotlib.pyplot as plt
from precip.cli import plot_precipitation
import pandas as pd

# This is needed to run on a server without a display
import matplotlib
matplotlib.use('Agg')

PRECIP_HOME = os.environ.get('PRECIP_HOME')
SCRATCH_DIR = os.environ.get('SCRATCHDIR')
VOLCANO_FILE = PRECIP_HOME + '/src/precip/Holocene_Volcanoes_precip_cfg..xlsx'
DEFAULT_STYLES = ['map', 'bar', 'annual', 'strength']
# DEFAULT_STYLES = ['bar', 'annual', 'strength']        # FA 7/2025  map gives problems woth GMT
BINS = [1, 2, 3, 4]

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

plot_precipitation --help for more options
"""

def create_parser():
    synopsis = 'Wrapper tool to run plot_precipitation with multiple styles and all volcanoes'
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

    volcanoes = get_volcanoes()
    failures = {}

    for volcano, info in volcanoes.items():
        id = info['id']
        volcano_dir = os.path.join(plot_dir, str(id))
        os.makedirs(volcano_dir, exist_ok=True)
        for style, bins in product(args.styles, BINS):
            inps = argparse.Namespace(style=style,
                                      name=[volcano],
                                      no_show=True,
                                      bins=bins)
            try:
                plot_precipitation.main(unknown_args, inps)
            except KeyboardInterrupt:
                raise
            except Exception as e:
                failures[volcano] = e
                print('#'*50)
                print(f'Failed to plot {volcano} with style {style} and bins {bins}')
            png_path = os.path.join(volcano_dir, f'{id}_{style}_bin_{bins}.png')
            plt.savefig(png_path)
            print('#'*50)
            print(f'{'#'*50}\nSaved {png_path}')

    print('#'*50)
    print(f'Failed to plot for the following volcanoes: {len(failures)}')
    print(failures)

if __name__ == '__main__':
    main()
