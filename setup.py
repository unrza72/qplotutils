from setuptools import setup

setup(name='qplotutils',
      version='0.0.1',
      description='Collection of widgets to compose iteractive plotting environments with PyQt',
      url='https://github.com/unrza72/qplotutils',
      author='Philipp Baust',
      author_email='philipp.baust@gmail.com',
      license='MIT',
      packages=['qplotutils',],
      install_requires=[
            'PyQt4',
      ],
      zip_safe=False)