import sys
# Remove current dir from sys.path, otherwise setuptools will peek up our
# module instead of system.
sys.path.pop(0)
from setuptools import setup

setup(
    name='micropython-bmp180',
    version='0.1',
    author='Sebastian Plamauer',
    author_email='oeplse@gmail.co',
    packages=['bmp180'],
    url='https://github.com/turbinenreiter/micropython-bmp180',
    license='LICENSE.txt',
    description='Micropython module for the BMP180 pressure sensor.',
    long_description=open('docs/README.md').read(),
)
