from setuptools import setup
from setuptools.command.install import install
import nltk

class PostInstallCommand(install):
    def run(self):
        install.run(self)
        # NLTK dependencies
        corpora_deps = ['words', 'stopwords', 'wordnet']
        for dependency in corpora_deps:
            try:
                nltk.data.find(f'corpora/{dependency}')
            except LookupError:
                print(f"Did not found corpora '{dependency}'. Downloading...")
                nltk.download(dependency)

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='poslog',
    version='0.6',
    author='Kilian Dangendorf',
    description='PosLog: A CRF-based Part-of-Speech Tagger for Log Messages',
    long_description=long_description,
    long_description_content_type='text/markdown',
    #url='https://github.com/kiliandangendorf/poslog',
    project_urls={
        'GitHub': 'https://github.com/kiliandangendorf/poslog',
    },
    packages=['poslog', 'poslog.words'],
    include_package_data=True,
    package_data={
        'poslog': ['models/pos_log_upos_crf_10k_model.pkl', 'words/*.txt'],
    },
    install_requires=['nltk', 'sklearn-crfsuite'],
    cmdclass={
        'install': PostInstallCommand,
    },
    python_requires=">=3.11",

)