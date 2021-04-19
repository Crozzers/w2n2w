from setuptools import setup

setup(
    name='w2n2w',
    packages=['w2n2w'],
    version='0.1.3',
    license='MIT',
    description='Convert words to numbers and back again',
    author='Crozzers',
    author_email='captaincrozzers@gmail.com',
    url='https://github.com/Crozzers/w2n2w',
    keywords=['numbers', 'convert', 'words'],
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3 :: Only'
    ],
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown'
)
