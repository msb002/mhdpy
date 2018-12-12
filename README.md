# MHD python package

## Installation
1. Make sure you have installed Anaconda.
2. Download the Git repository by typing `git clone https://github.com/MHDLab/mhdpy` in Git bash.
3. Open an anaconda prompt as an administrator (type anaconda into the windows search bar and right click to open as administrator) and make sure a Python 3.6 conda environment is selected (see [Docs](https://github.com/MHDLab/Documentation/blob/master/README.md) for setting up Anaconda). 
4. Navigate the prompt to your repository. Copy the local path to your repository and type `cd <repository path>` into the anaconda prompt. Note you have to right click and say paste or use Shift+Insert to insert text in the prompt. 
5. type `conda install .`. 

## Alternative install for development

Alternatively you can install the repository using `python setup.py develop`. `develop` is similar to `install` but it will allow for you to change and use the mhdpy python package without having to run install again.  For this method type `python setup.py clean`.  This just cleans temporary setup files in your repository. 
