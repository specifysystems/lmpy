"""Test the create tree matrix tool."""

from lmpy.matrix import Matrix
from lmpy.tree import TreeWrapper
from lmpy.tools.create_tree_matrix import cli


# .....................................................................................
def test_create_tree_matrix(monkeypatch, generate_temp_filename):
    """Test the cretae_tree_matrix tool.

    Args:
        monkeypatch (pytest.fixture): A fixture for monkeypatching code.
        generate_temp_filename (pytest.fixture): A fixture for making temp filenames.
    """
    # Generate filenames
    tree_filename = generate_temp_filename(suffix='.tre')
    tree_schema = 'newick'
    tree_matrix_filename = generate_temp_filename(suffix='.lmm')
    node_heights_filename = generate_temp_filename(suffix='.lmm')
    tip_lengths_filename = generate_temp_filename(suffix='.lmm')

    # Generate a tree
    tree_tips = ['A', 'B', 'C', 'D', 'E']
    tip_lengths = [1.0, 1.0, 1.5, 1.5, 5.0]
    node_heights = [1.0, 1.5, 2.0, 5.0]
    tree_data = '(((A:1.0,B:1.0):1.0,(C:1.5,D:1.5):0.5):3.0,E:5.0):0.0;'
    tree = TreeWrapper.get(data=tree_data, schema=tree_schema)
    tree.write(path=tree_filename, schema=tree_schema)

    # Run encoding tool
    params = [
        'create_tree_matrix.py',
        tree_filename,
        tree_schema,
        tree_matrix_filename,
        node_heights_filename,
        tip_lengths_filename,
    ]

    monkeypatch.setattr('sys.argv', params)
    cli()

    # Load tree matrix
    tree_matrix = Matrix.load(tree_matrix_filename)

    # Check headers
    assert sorted(tree_matrix.get_row_headers()) == sorted(tree_tips)

    # Check tip lengths and node heights
    tip_lengths_matrix = Matrix.load(tip_lengths_filename)
    assert sorted(tip_lengths_matrix.tolist()) == sorted(tip_lengths)

    node_heights_matrix = Matrix.load(node_heights_filename)
    assert sorted(node_heights_matrix.tolist()) == sorted(node_heights)
