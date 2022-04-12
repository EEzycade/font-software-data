from setuptools import setup, find_packages

setup(
    name='bookmarked-utils',
    version='0.1',
    description='bmark',
    url='https://github.com/EEzycade/font-software-data',
    packages=find_packages(),
    package_data={"bmark": ["character-types.yaml"]},
    install_requires=[
        "Pillow==9.1.0",
        "potracer==0.0.1",
        "numpy",
        "fonttools==4.31.2",
        "pyyaml",
        "imutils",
        "pytesseract",
    ],
)
