"""Module testing the tool documentation in sphinx."""
import glob
import os


# .....................................................................................
def test_check_sphinx_doc_exist():
    """Check that a sphinx page exists for each of the tools."""
    tools_dir = '../../lmpy/tools/'
    sphinx_tools_idr = '../../_sphinx_config/scripts/'
    for tool_fn in glob.glob(os.path.join(tools_dir, '*.py')):
        tool_name = os.path.splitext(os.path.basename(tool_fn))[0]
        if not tool_name.startswith('_'):
            doc_fn = os.path.join(sphinx_tools_idr, f'{tool_name}.rst')
            assert os.path.exists(doc_fn)
