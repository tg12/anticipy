from pathlib import Path

from setuptools import find_packages, setup

# Configuration
PACKAGE_NAME = "anticipy-sawyer"
PACKAGE_VERSION = "0.2.2"
PYTHON_REQUIRES = ">=3.10"
README_PATH = Path("README.md")
ZIP_SAFE = False
MODULES: list[str] = []
DEPENDENCIES = [
    "numpy>=2.0.0",
    "pandas>=2.2.3",
    "scipy>=1.14.0",
    "plotly>=5.22.0",
]
EXTRAS_REQUIRE = {
    "extras": [
        "matplotlib>=3.8.0",
        "ipython>=8.0.0",
        "notebook>=7.0.0",
        "ipywidgets>=8.1.2",
    ],
    "dev": [
        "ruff>=0.4.0",
        "vulture>=2.13",
        "pytest>=8.0.0",
        "pytest-html>=4.0.0",
        "pytest-cov>=4.0.0",
    ],
}
ENTRY_POINTS = {
    "console_scripts": ["anticipy-forecast=anticipy.app:main"],
}


LONG_DESCRIPTION = README_PATH.read_text(encoding="utf-8")

setup(
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,
    description="Fork of Anticipy forecasting tools",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author="Pedro Capelastegui",
    author_email="pedro.capelastegui@sky.uk",
    maintainer="James Sawyer",
    url="https://github.com/jamessawyer/anticipy",
    license="BSD",
    packages=find_packages(exclude=("tests", "benchmarks", "docs")),
    py_modules=MODULES,
    include_package_data=True,
    install_requires=DEPENDENCIES,
    python_requires=PYTHON_REQUIRES,
    zip_safe=ZIP_SAFE,
    entry_points=ENTRY_POINTS,
    extras_require=EXTRAS_REQUIRE,
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
