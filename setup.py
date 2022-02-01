import setuptools  # type: ignore


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
    name="mutwo.ext-mbrola",
    version="0.2.0",
    license="GPL",
    description="mbrola extension for event based framework for generative art",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Levin Eric Zimmermann",
    author_email="levin.eric.zimmermann@posteo.eu",
    url="https://github.com/mutwo-org/mutwo.ext-mbrola",
    project_urls={"Documentation": "https://mutwo.readthedocs.io/en/latest/"},
    packages=[
        package
        for package in setuptools.find_namespace_packages(include=["mutwo.*"])
        if package[:5] != "tests"
    ],
    setup_requires=[],
    install_requires=[
        "mutwo.ext-core>=0.55.0, <1.00.0",
        "mutwo.ext-music>=0.7.0, <1.0.0",
        "voxpopuli>=0.3.7, <1",
    ],
    extras_require=extras_require,
    python_requires=">=3.9, <4",
)
