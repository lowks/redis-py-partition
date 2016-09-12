#from distutils.core import setup
from setuptools import setup


setup(
    name='redispartition',
    version='0.1.1',
    packages=[
        'redispartition',
    ],
    license='MIT',
    url='http://github.com/phelimb/redis-py-partition',
    description='Simple partitioning of data across redis connections',
    author='Phelim Bradley',
    author_email='wave@phel.im',
    install_requires=[
            'redis',
            'crc16'],
    entry_points={
        'console_scripts': [
            'remcdbg = remcdbg.main:main',
        ]})
