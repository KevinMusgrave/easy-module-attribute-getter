import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="easy_module_attribute_getter",
    version="0.9.16",
    author="Kevin Musgrave",
    author_email="tkm45@cornell.edu",
    description="Select module classes and functions using yaml, without any if-statements.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/KevinMusgrave/easy_module_attribute_getter",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[
      'PyYAML'
    ],
)