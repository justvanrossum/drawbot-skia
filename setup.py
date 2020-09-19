from setuptools import setup, find_packages


setup(
    name="drawbot-skia",
    python_requires=">=3.6",
    entry_points={
        'console_scripts': ['drawbot=drawbot_skia.__main__:main'],
    },
    package_dir={"": "src"},
    packages=find_packages("src"),
    install_requires=[
        "skia-python",
        "fonttools[unicode]",
        "numpy",  # unlisted skia-python dependency, TODO: is this true?
        "uharfbuzz",
        "python-bidi",
        "unicodedata2",
    ],
)
