from setuptools import setup, find_packages

setup(
    name="langchain_tableau",
    version="0.2",
    packages=find_packages(),
    install_requires=[],
    author="Tableau",
    author_email="tab-se@tableau.com",
    description="Tableau tools for Agentic use cases with Langchain",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    include_package_data=True,
    license_files=["LICENSE.txt"],
    long_description_content_type="text/markdown",
    long_description=open("README.md").read(),
)
