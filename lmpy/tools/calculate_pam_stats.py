"""Tool for creating PAM statistics."""
import argparse

from lmpy.matrix import Matrix
from lmpy.tree import TreeWrapper
from lmpy.statistics.pam_stats import PamStats

DESCRIPTION = 'Compute statistics for a PAM and optionally a tree.'


# .....................................................................................
def cli():
    """Provide a command-line tool for computing statistics."""
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('--tree_filename', type=str, help='Path to matching tree.')
    parser.add_argument(
        '--tree_matrix', type=str, nargs=3, help='Path to tree matrix.'
    )

    # Output matrices
    parser.add_argument(
        '--covariance_matrix',
        type=str,
        help='Path to write covariance matrix if desired.',
    )
    parser.add_argument(
        '--diversity_matrix',
        type=str,
        help='Path to write diversity matrix if desired.',
    )
    parser.add_argument(
        '--site_stats_matrix',
        type=str,
        help='Path to write site statistics matrix if desired.',
    )
    parser.add_argument(
        '--species_stats_matrix',
        type=str,
        help='Path to write species statistics matrix if desired.',
    )

    # PAM
    parser.add_argument('pam_filename', type=str, help='Path to PAM file.')

    args = parser.parse_args()

    tree = tree_matrix = None
    pam = Matrix.load(args.pam_filename)

    if args.tree_filename is not None:
        tree = TreeWrapper.from_filename(args.tree_filename)

    if args.tree_matrix is not None:
        tree_matrix = Matrix.load(args.tree_matrix[0])
        node_heights_matrix = Matrix.load(args.tree_matrix[1])
        tip_lengths_matrix = Matrix.load(args.tree_matrix[2])

    stats = PamStats(pam, tree=tree)

    # Write requested stats
    if args.covariance_matrix is not None:
        with open(args.covariance_matrix, mode='wt') as out_json:
            json.dump(stats.calculate_covariance_statistics())

    if args.diversity_matrix is not None:
        stats.calculate_diversity_statistics().write(args.diversity_matrix)

    if args.site_stats_matrix is not None:
        stats.calculate_site_statistics().write(args.site_stats_matrix)

    if args.species_stats_matrix is not None:
        stats.calculate_species_statistics().write(args.species_stats_matrix)


# .....................................................................................
__all__ = ['cli']


# .....................................................................................
if __name__ == '__main__':  # pragma: no cover
    cli()
