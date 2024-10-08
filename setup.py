from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as readme:
    description = readme.read() 
   
setup(
    name="vpmobil",
    version="0.4.1",
    packages=find_packages(),
    install_requires=[
        "requests",
        "acemeta"
        ],
    author="Annhilati & Joshi",
    description="A python wrapper package for interacting with a stundenplan24.de substitution plan",
    long_description=description,
    long_description_content_type="text/markdown",
    url="https://github.com/annhilati/vpmobil-py"
)
