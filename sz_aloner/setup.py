from distutils.core import setup
from Cython.Build import cythonize

setup(
  name = 'Empire knapsack',
  ext_modules = cythonize("knapsack.pyx"),
)