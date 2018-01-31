'''from distutils.core import setup, Extension

module = Extension('knapsack',
                    sources = ['knapsack.c'])

setup (name = 'Separator knapsack',
       version = '1.0',
       description = '',
       ext_modules = [module])'''

from distutils.core import setup
from Cython.Build import cythonize
from distutils.extension import Extension

sourcefiles = ['knapsack.pyx']

extensions = [Extension("knapsack", sourcefiles)]

setup(
    ext_modules = cythonize(extensions)
)