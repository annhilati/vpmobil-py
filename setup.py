from setuptools import setup, find_packages

setup(
    name="vpmobil",
    version="0.1",
    packages=find_packages(),
    install_requires=["requests"],  # Hier können Abhängigkeiten aufgelistet werden
    author="Annhilati & Joshi",
    #author_email="Ihre Email",
    description="A python package for interacting with a stundenplan24.de substitution plan",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    #url="https://example.com/mypackage",  # URL zu Ihrem Projekt (optional)
)
