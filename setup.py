import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="RPi.GPIO",
    version="0.0.2",
    author="Underground Software",
    author_email="fedora-rpi@googlegroups.com",
    description="Compatibility layer between RPi.GPIO syntax and libgpiod semantics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/underground-software/python3-libgpiod-rpi",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 2 - Pre-Alpha"
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)"
        "Operating System :: POSIX :: Linux"
    ],
    python_requires='>=3.6',
)
