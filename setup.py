import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

install_requires = [
    'pyelftools',
    'pymanifest',
]

setuptools.setup(
    name='dwarfgen',
    version='0.2',
    packages=[
        'dwarfgen',
        'dwarfgen.src',
        'dwarfgen.src.lang_generators'
    ],
    author="Clay Brooks",
    author_email="clay_brooks@outlook.com",
    description="IDL/Code generation utility",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/claybrooks/dwarfgen",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: The Unlicense (Unlicense)",
        "Operating System :: OS Independent",
    ],
    install_requires=install_requires
)