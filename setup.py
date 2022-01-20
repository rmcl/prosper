import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="prosper-client",
    version="0.1.0",
    author="Russell McLoughlin",
    author_email="russ.mcl@gmail.com",
    description="A python client for the Prosper Lending platform.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rmcl/prosper",
    packages=setuptools.find_packages(),
    install_requires=[
        'nose',
        'coverage',
        'requests',
        'types-requests',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
