"""Test the encode_tree_mcpa tool."""
import numpy as np

from lmpy.matrix import Matrix
from lmpy.tools.encode_tree_mcpa import cli
from lmpy.tree import TreeWrapper


# .....................................................................................
def test_encode_tree_mcpa_with_branch_lengths(monkeypatch, generate_temp_filename):
    """Test the encode_tree_mcpa tool with a tree that has branch lengths.

    Args:
        monkeypatch (pytest.fixture): A fixture for monkeypatching code.
        generate_temp_filename (pytest.fixture): A fixture for making temp filenames.
    """
    # Generate filenames
    tree_filename = generate_temp_filename(suffix='.tre')
    tree_schema = 'newick'
    pam_filename = generate_temp_filename(suffix='.lmm')
    tree_matrix_filename = generate_temp_filename(suffix='.lmm')

    # Generate tree
    tree_data = '((((A:0.2,B:0.2):0.65,C:0.85):0.15,D:1.0):0.4,(E:0.5,F:0.5):0.9);'
    tree = TreeWrapper.get(data=tree_data, schema=tree_schema)
    tree.write(path=tree_filename, schema=tree_schema)

    # Generate PAM
    pam = Matrix(
        np.ones((5, 6)),
        headers={
            '0': [f'{i}' for i in range(5)],
            '1': ['A', 'B', 'C', 'D', 'E', 'F']
        }
    )
    pam.write(pam_filename)

    # Run tool
    # Set params
    params = [
        'encode_tree_mcpa.py',
        tree_filename,
        tree_schema,
        pam_filename,
        tree_matrix_filename,
    ]
    monkeypatch.setattr('sys.argv', params)

    # Call script
    cli()

    # Check outputs
    test_tree_matrix = Matrix(
        np.array(
            [
                [-1.0, -0.5, -0.28, -0.196, 0.0],
                [1.0, -0.5, -0.28, -0.196, 0.0],
                [0.0, 1.0, -0.439, -0.29, 0.0],
                [0.0, 0.0, 1.0, -0.319, 0.0],
                [0.0, 0.0, 0.0, 0.5, -1.0],
                [0.0, 0.0, 0.0, 0.5, 1.0]
            ]
        )
    )
    tree_matrix = Matrix.load(tree_matrix_filename)
    for i in range(tree_matrix.shape[0]):
        a = sorted(np.abs(tree_matrix[i]))
        b = sorted(np.abs(test_tree_matrix[i]))
        assert np.all(np.isclose(a, b, atol=0.001))


# .....................................................................................
def test_encode_tree_mcpa_without_branch_lengths(monkeypatch, generate_temp_filename):
    """Test the encode_tree_mcpa tool with a tree that doesn't have branch lengths.

    Args:
        monkeypatch (pytest.fixture): A fixture for monkeypatching code.
        generate_temp_filename (pytest.fixture): A fixture for making temp filenames.
    """
    # Generate filenames
    tree_filename = generate_temp_filename(suffix='.tre')
    tree_schema = 'newick'
    pam_filename = generate_temp_filename(suffix='.lmm')
    tree_matrix_filename = generate_temp_filename(suffix='.lmm')

    # Generate tree
    tree_data = '((((A,B),C),D),(E,F));'
    tree = TreeWrapper.get(data=tree_data, schema=tree_schema)
    tree.write(path=tree_filename, schema=tree_schema)

    # Generate PAM
    pam = Matrix(
        np.ones((5, 6)),
        headers={
            '0': [f'{i}' for i in range(5)],
            '1': ['A', 'B', 'C', 'D', 'E', 'F']
        }
    )
    pam.write(pam_filename)

    # Run tool
    # Set params
    params = [
        'encode_tree_mcpa.py',
        tree_filename,
        tree_schema,
        pam_filename,
        tree_matrix_filename,
    ]
    monkeypatch.setattr('sys.argv', params)

    # Call script
    cli()

    # Check outputs
    test_tree_matrix = Matrix(
        np.array(
            [
                [-1.0, -0.5, -0.25, -0.125, 0.0],
                [1.0, -0.5, -0.25, -0.125, 0.0],
                [0.0, 1.0, -0.5, -0.25, 0.0],
                [0.0, 0.0, 1.0, -0.5, 0.0],
                [0.0, 0.0, 0.0, 0.5, -1.0],
                [0.0, 0.0, 0.0, 0.5, 1.0]
            ]
        )
    )
    tree_matrix = Matrix.load(tree_matrix_filename)
    for i in range(tree_matrix.shape[0]):
        a = sorted(np.abs(tree_matrix[i]))
        b = sorted(np.abs(test_tree_matrix[i]))
        assert np.all(np.isclose(a, b, atol=0.001))
