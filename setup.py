from setuptools import find_packages, setup

setup(
    name="auto-faq",
    version="0.0.1",
    description="Automatic FAQ Mining Framework",
    license="MIT",
    packages=find_packages(),
    author="Amin Rezaei",
    author_email="AminRezaei0x443@gmail.com",
    keywords=[],
    entry_points={
        "console_scripts": [
            # "autofaq = autofaq.cli.entry:entry",
        ],
    },
    url="https://github.com/AminRezaei0x443/auto-faq",
    install_requires=[],
    extras_require={},
)
