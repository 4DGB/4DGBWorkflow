import setuptools

# read the description file 
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'doc/description.md'), encoding='utf-8') as f:
    long_description_text = f.read()

this_directory = path.abspath(path.dirname(__file__))
version = ""
with open(path.join(this_directory, 'version.txt'), encoding='utf-8') as f:
    version_text = f.read().strip()

setuptools.setup(
    name="4dgb-workflow",
    version=version_text,
    author="David H. Rogers",
    author_email="dhr@lanl.gov",
    description="4D Genome Browser Workflow.",
    long_description=long_description_text,
    long_description_content_type='text/markdown',
    url="https://github.com/4dgb/4DGBWorkflow",
    include_package_data=True,
    packages=['4dgb-workflow'],
    scripts=['4DGBWorkflow', 'doc/description.md', 'version.txt'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
)
