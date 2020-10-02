from setuptools import setup, find_packages


with open("README.md", encoding="utf-8") as f:
    long_description = f.read()


setup(
    name="drawbot-skia",
    use_scm_version={"write_to": "src/drawbot_skia/_version.py"},
    description="Drawbot implements a simple drawing API to generate 2D vector graphics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Just van Rossum",
    author_email="justvanrossum@gmail.com",
    url="http://github.com/justvanrossum/drawbot-skia",
    license="Apache License 2.0",
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
    extras_require={
        "mp4": ["pyffmpeg==1.6.1"],  # pin for now, this package is not very stable
    },
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Multimedia :: Graphics",
    ],
)
