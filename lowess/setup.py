from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import numpy as np

ext_modules = [
    Extension("lowess", ["lowess.pyx"],
        extra_objects=["_lowess.c"], libraries=['m'] ,
        include_dirs=[np.get_include()])]

setup(
  name = 'lowess',
  cmdclass = {'build_ext': build_ext},
  ext_modules = ext_modules
)
