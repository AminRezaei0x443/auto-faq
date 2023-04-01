from setuptools import find_packages, setup

setup(
    name="auto-faq",
    version="0.4.0",
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
)
