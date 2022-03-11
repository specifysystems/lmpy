"""Tree encoding module tests."""
import tempfile
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


# ............................................................................
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
    def test_constructor_from_file(self):
        """Test constructor from file."""
        tree = TreeWrapper.get(data='(A,(B,C));', schema='newick')
        pam = Matrix(np.array([[1, 0, 1], [0, 1, 1], [1, 0, 0]]))
        tmp_file = tempfile.NamedTemporaryFile(delete=True)
        tree_filename = '{}.tre'.format(tmp_file.name)
        pam_filename = '{}.lmm'.format(tmp_file.name)
        tmp_file.close()
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
