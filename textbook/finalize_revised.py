"""Build the final verified delivery using the current edition packager."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name('finalize_final.py')), run_name='__main__')
