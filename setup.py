import sys
from setuptools import setup


if sys.version_info < (3, 0):
    sys.stderr.write("Sorry, Python < 3.0 is not supported\n")
    sys.exit(1)


setup(name='zen_tui',
      version='1.2.1',
      description="""A simple text user interface (TUI) library.""",
      long_description=open('README.rst').read(),
      url='https://github.com/iva2k/py_zen_tui',
      author='iva2k',
      author_email='iva2k@yahoo.com',
      license='MIT',
      packages=['zen_tui'])
