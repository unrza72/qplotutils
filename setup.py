from setuptools import setup

setup(name='qplotutils',
      version='0.0.2',
      description='Collection of widgets to compose iteractive plotting environments with PyQt / PySide',
      url='https://github.com/unrza72/qplotutils',
      author='Philipp Baust',
      author_email='philipp.baust@gmail.com',
      license='MIT',
      packages=['qplotutils',],
      install_requires=[
            'qtpy', 'numpy', 'PyOpenGL',
      ],
      zip_safe=False)