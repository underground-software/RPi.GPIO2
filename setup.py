from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="RPi.GPIO2",
    version="0.3.0a2",

    author="Joel Savitz",
    author_email="joelsavitz@gmail.com",

    description="Compatibility layer between RPi.GPIO syntax and libgpiod semantics",
    long_description=long_description,
    long_description_content_type="text/markdown",

    url="https://github.com/underground-software/python3-libgpiod-rpi",
    packages=find_packages(),

    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: POSIX :: Linux",
        "Intended Audience :: Education",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Topic :: Home Automation",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: System :: Hardware",
    ],

    keywords="Raspberry Pi GPIO libgpiod RPi.GPIO",

    python_requires=">=3.7",

    project_urls={
        "Source":       "https://github.com/underground-software/python3-libgpiod-rpi",
        "Bug Reports":  "https://github.com/underground-software/python3-libgpiod-rpi/issues",
    },
)
