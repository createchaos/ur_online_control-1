# UR Online Control


## Getting started

### Compas and Compas Fab Installation (via Anaconda Terminal) - Fresh
    
    (base)  conda config --add channels conda-forge
    (base)  conda remove --name your_env_name --all
    (base)  conda create -n your_env_name python=3.6 compas=0.11.4 compas_fab=0.10.1 --yes
    (base)  conda activate your_env_name
    (your_env_name) python -m compas_rhino.install
    (your_env_name) python -m compas_fab.rhino.install -v 6.0

### Compas and Compas Fab Installation (via Anaconda Terminal) - Update

Activate your `your_env_name` environment and update it as follows:

    (base)  conda activate your_env_name
    (your_env_name) conda install compas=0.15.6 compas_fab=0.11.0 --yes
    (your_env_name) python -m compas_rhino.install
    (your_env_name) python -m compas_fab.rhino.install -v 6.0

### Verify Installation

    (your_env_name) python
    >>> import compas_fab
    >>> compas_fab.__version__
    '0.10.1'
    >>> exit()

### Iron Python Installation

Install Ironpython 2.7.9. via following this [link](https://github.com/IronLanguages/ironpython2/releases/tag/ipy-2.7.9)

### UR Online Control Installation

First, clone the current version of the [ur_online_control repository](https://github.com/augmentedfabricationlab/ur_online_control) 
into your project folder.

Then, add the following two directories to the Python Path in Rhino via >> EditPythonScript >> Tools >> Options >> Add to search path:

1. Ironpython Path, e.g., C:\Program Files\IronPython 2.7\Lib
2. Parent folder or ur_online_control repository, e.g., C:\Users\yourname\workspace\projects

## Example files

You find the `grasshopper playground` in the rhino folder:

Setup with one robot:

    ur_online_control_base_setup_x1.ghx
    u10e_setup_x1.3dm

Setup with two robots:

    ur_online_control_base_setup_x2.ghx
    u10e_setup_x2.3dm

Copy the .3dm and .ghx files of your choice into your own project folder, use and modify it. Voilà!


![`grasshopper playground`](ghcomp/images/gui_example.PNG)

