import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="easy-module-attribute-getter",
    version="0.9.41",
    author="Kevin Musgrave",
    description="Select module classes and functions using yaml, without any if-statements.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/KevinMusgrave/easy-module-attribute-getter",
    packages=setuptools.find_packages(include=["easy_module_attribute_getter"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.0',
    install_requires=[
      'PyYAML >= 5.3.1',
      'torchvision >= 0.4.0'
    ],
)
