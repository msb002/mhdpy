# MHD Lab python package

## Installation
1. Make sure you have installed Anaconda3 following the instructions in the [Docs](https://github.com/MHDLab/Documentation/blob/master/README.md), an anaconda prompt is opened and the py36 conda environment is activated.
2. Download the Git repository
     * In your MHDLab folder right click and select 'Git Bash Here'
     * type `git clone https://github.com/MHDLab/mhdpy`
     * close git bash
4. Navigate the anaconda prompt to the mhdpy repository: copy the local path to your repository, type `cd ` and paste the repository path into the anaconda prompt. Note: the Control-v shortcut doesn't work in command prompts, right click and say paste or use Shift+Insert to insert text in the prompt. 
5. enter `python setup.py install`
6. enter `conda develop .`

You can confirm that mhdpy has installed correctly by starting python (enter `python` in the anaconda prompt) and running the following commands:

`>> import mhdpy`

`>> mhdpy.__file__`

which should show a path to your repository. 
