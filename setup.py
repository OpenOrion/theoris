from setuptools import setup, find_packages
from pathlib import Path

# Read the requirements from the requirements.txt file
requirements = []
if Path('requirements.txt').exists():
    with open('requirements.txt') as f:
        requirements = f.read().splitlines()

# Read README.md for long description
long_description = ""
if Path('README.md').exists():
    with open('README.md') as f:
        long_description = f.read()

setup(
    name='theoris',
    version='0.1.0',
    packages=find_packages(exclude=['tests*', 'examples*']),
    install_requires=requirements,
    url='https://github.com/OpenOrion/theoris',
    license='MIT',
    author='Open Orion, Inc.',
    description="A Python library for symbolic computation, proof verification, and unit handling",
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='symbolic computation, code generation, proof verification',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Code Generators',
    ],
    python_requires='>=3.8',
)
