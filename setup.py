import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gridsearch_analysis",
    version="0.1.0",
    author="Malte Esders",
    author_email="git@maltimore.info",
    description="Analysis of gridsearch performed with gridsearch_helper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/maltimore/gridsearch_helper",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: custom non-military",
        "Operating System :: OS Independent",
    ],
)
