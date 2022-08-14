import setuptools  # type: ignore

version = {}
with open("mutwo/mbrola_version/__init__.py") as fp:
    exec(fp.read(), version)

VERSION = version["__version__"]


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

extras_require = {
    "testing": [
        "nose",
        "coveralls",
        "sox==1.4.1",
        "tensorflow>=2.0.0",
        "crepe==0.0.12",
    ]
}

setuptools.setup(
    name="mutwo.mbrola",
    version=VERSION,
    license="GPL",
    description="mbrola extension for event based framework for generative art",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Levin Eric Zimmermann",
    author_email="levin.eric.zimmermann@posteo.eu",
    url="https://github.com/mutwo-org/mutwo.mbrola",
    project_urls={"Documentation": "https://mutwo.readthedocs.io/en/latest/"},
    packages=[
        package
        for package in setuptools.find_namespace_packages(include=["mutwo.*"])
        if package[:5] != "tests"
    ],
    setup_requires=[],
    install_requires=[
        "mutwo.core>=0.61.4, <1.00.0",
        "mutwo.music>=0.17.0, <1.0.0",
        "voxpopuli>=0.3.7, <1",
    ],
    extras_require=extras_require,
    python_requires=">=3.9, <4",
)
