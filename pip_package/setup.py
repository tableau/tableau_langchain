from setuptools import setup, find_packages

setup(
    name="langchain-tableau-test",  # Package name
    version="0.1.4",    # Version
    packages=find_packages(),  # Automatically find sub-packages
    install_requires=[],  # List dependencies
    author="Tableau Langchain Team",
    author_email="tableau-langchain@tableau.com",
    description="Tableau tools for Agentic use cases with Langchain",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Tab-SE/tableau_langchain",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
)