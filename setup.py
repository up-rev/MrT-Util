import setuptools




with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
     name='mrtutils',
     version='0.0.05',
     author="Jason Berger",
     author_email="JBerger@up-rev.com",
     description="Utilities for MrT",
     long_description=long_description,
     scripts=['mrtutils/mrt-config','mrtutils/mrt-device'],
     long_description_content_type="text/markdown",
     url="http://www.up-rev.com/",
     packages=setuptools.find_packages(),
     install_requires=[
        'markdown',
        'mako',
        'pyyaml'
     ],
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )
