import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gridsearch_analysis",
    version="0.0.2",
    author="Malte Esders",
    author_email="will_add@later.com",
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
