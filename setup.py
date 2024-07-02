from setuptools import setup, find_packages

setup(
    name="vpmobil",
    version="0.1",
    packages=find_packages(),
    install_requires=["selenium"],  # Hier können Abhängigkeiten aufgelistet werden
    author="Annhilati & Joshi",
    #author_email="Ihre Email",
    #description="Eine kurze Beschreibung Ihres Pakets",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    #url="https://example.com/mypackage",  # URL zu Ihrem Projekt (optional)
)
