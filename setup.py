from setuptools import setup, find_packages


setup(
    name="drawbot-skia",
    use_scm_version={"write_to": "src/drawbot_skia/_version.py"},
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
    setup_requires=["setuptools_scm"],
    python_requires=">=3.6",
    classifiers=[
    ],
)
