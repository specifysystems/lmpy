"""Tree encoding module tests."""
import numpy as np
import pytest

from lmpy import Matrix, TreeWrapper
from lmpy.data_preparation.tree_encoder import EncodingException, TreeEncoder


# ............................................................................
class Test_EncodingException:
    """Test the EncodingException class."""

    # ............................
    def test_constructor(self):
        """Test the construction since it is just a wrapper class."""
        assert EncodingException('Testing') is not None


# .....................................................................................
class Test_TreeEncoder:
    """Test the TreeEncoder class."""

    # ............................
    def test_basic_constructor(self):
        """Test with a TreeWrapper and Matrix."""
        tree = TreeWrapper.get(data='(A,(B,C));', schema='newick')
        pam = Matrix(np.array([[1, 0, 1], [0, 1, 1], [1, 0, 0]]))
        _ = TreeEncoder(tree, pam)

    # ............................
    def test_basic_constructor_numpy(self):
        """Test with a TreeWrapper and numpy array."""
        tree = TreeWrapper.get(data='(A,(B,C));', schema='newick')
        pam = np.array([[1, 0, 1], [0, 1, 1], [1, 0, 0]])
        _ = TreeEncoder(tree, pam)

    # ............................
    def test_constructor_from_file(self, generate_temp_filename):
        """Test constructor from file.

        Args:
            generate_temp_filename (pytest.fixture): Fixture to generate filenames.
        """
        tree = TreeWrapper.get(data='(A,(B,C));', schema='newick')
        pam = Matrix(np.array([[1, 0, 1], [0, 1, 1], [1, 0, 0]]))
        tree_filename = generate_temp_filename(suffix='.tre')
        pam_filename = generate_temp_filename(suffix='.lmm')
        tree.write(path=tree_filename, schema='newick')
        pam.write(pam_filename)
        _ = TreeEncoder.from_file(tree_filename, pam_filename)

    # ............................
    def test_constructor_mismatch(self):
        """Test constructor with mismatched PAM and tree."""
        tree = TreeWrapper.get(data='(A,(B,(C,D)));', schema='newick')
        pam = Matrix(np.array([[1, 0, 1], [0, 1, 1], [1, 0, 0]]))
        te = TreeEncoder(tree, pam)
        with pytest.raises(EncodingException):
            te.encode_phylogeny()

    # ............................
    def test_encode_branch_lengths(self):
        """Test encoding a tree with branch lengths."""
        tree_data = '((((A:0.2,B:0.2):0.65,C:0.85):0.15,D:1.0):0.4,(E:0.5,F:0.5):0.9);'
        tree = TreeWrapper.get(data=tree_data, schema='newick')
        pam = Matrix(
            np.ones((5, 6)),
            headers={
                '0': [f'{i}' for i in range(5)],
                '1': ['A', 'B', 'C', 'D', 'E', 'F']
            }
        )
        encoder = TreeEncoder(tree, pam)
        tree_mtx = encoder.encode_phylogeny()
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
        for i in range(tree_mtx.shape[0]):
            a = sorted(np.abs(tree_mtx[i]))
            b = sorted(np.abs(test_tree_matrix[i]))
            assert np.all(np.isclose(a, b, atol=0.001))

    # ............................
    def test_encode_no_branch_lengths(self):
        """Test encoding a tree without branch lengths."""
        tree_data = '((((A,B),C),D),(E,F));'
        tree = TreeWrapper.get(data=tree_data, schema='newick')
        pam = Matrix(
            np.ones((5, 6)),
            headers={
                '0': [f'{i}' for i in range(5)],
                '1': ['A', 'B', 'C', 'D', 'E', 'F']
            }
        )
        encoder = TreeEncoder(tree, pam)
        tree_mtx = encoder.encode_phylogeny()
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
        for i in range(tree_mtx.shape[0]):
            a = sorted(np.abs(tree_mtx[i]))
            b = sorted(np.abs(test_tree_matrix[i]))
            assert np.all(np.isclose(a, b, atol=0.001))
