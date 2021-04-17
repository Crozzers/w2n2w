from setuptools import setup

setup(
    name='w2n2w',
    packages=['w2n2w'],
    version='0.1.0',
    license=open('LICENSE.txt').read(),
    description='Convert words to numbers and back again',
    author='Crozzers',
    author_email='captaincrozzers@gmail.com',
    url='https://github.com/Crozzers/w2n2w',
    keywords=['numbers', 'convert', 'words'],
    python_requires='>=3.6',
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python'
    ],
    long_description=open('README.md').read()
)
