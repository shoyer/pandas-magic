from setuptools import setup, find_packages


setup(name='pandas-magic',
      version='0.1-dev',
      license='MIT',
      author='Stephan Hoyer',
      author_email='shoyer@gmail.com',
      install_requires=['pandas'],
      url='https://github.com/shoyer/pandas-magic',
      packages=find_packages())
