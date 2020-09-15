from setuptools import setup, find_packages


setup(
    name="drawbot-skia",
    python_requires=">=3.6",
    package_dir={"": "src"},
    packages=find_packages("src"),
    install_requires=[
        "skia-python",
        "fonttools",
        "numpy",  # unlisted skia-python dependency
    ],
)
