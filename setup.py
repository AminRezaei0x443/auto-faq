from pathlib import Path

from setuptools import find_packages, setup

# Read README contents
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="auto-faq",
    version="0.4.1",
    description="Automatic FAQ Mining Framework",
    license="MIT",
    packages=find_packages(exclude=["test"]),
    author="Amin Rezaei",
    author_email="AminRezaei0x443@gmail.com",
    keywords=[],
    entry_points={
        "console_scripts": [
            "autofaq = autofaq.cli.entry:entry",
        ],
    },
    url="https://github.com/AminRezaei0x443/auto-faq",
    install_requires=[],
    extras_require={},
    long_description=long_description,
    long_description_content_type="text/markdown",
)
