import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="jinsi",
    version="0.0.3",
    author="Julian Fleischer",
    author_email="tirednesscankill@warhog.net",
    description="JSON/YAML homoiconic templating language",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/scravy/jinsi",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
