import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="websitemonitor", # Replace with your own username
    version="0.1",
    author="Holger Macht",
    author_email="holger@homac.de",
    description="Website monitoring via kafka and SQL storage",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/homac/websitemonitor",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

