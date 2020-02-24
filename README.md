# UR Online Control

## Iron Python Installation

Install Ironpython 2.7.9. via following this [link](https://github.com/IronLanguages/ironpython2/releases/tag/ipy-2.7.9)

### Compas Fab Installation - Fresh

If you run into installation problems, please remove and reinstall your `afab19` environment as follows:
    
    (base)  conda config --add channels conda-forge
    (base)  conda remove --name afab19 --all
    (base)  conda create -n afab19 python=3.6 compas=0.11 compas_fab=0.9 --yes
    (base)  conda activate afab19
    (afab19) python -m compas_rhino.install
    (afab19) python -m compas_fab.rhino.install -v 6.0

## Compas Fab Installation - Update

Use the `afab19` environment and update it as follows:

    (base)  conda activate afab19
    (afab19) conda install compas=0.11 compas_fab=0.9 --yes
    (afab19) python -m compas_rhino.install
    (afab19) python -m compas_fab.rhino.install -v 6.0

## Verify Installation

    (afab19) python
    >>> import compas_fab
    >>> compas_fab.__version__
    '0.9.0'
    >>> exit()

## UR Online Control Installation

First, clone the current version of the [ur_online_control repository](https://github.com/augmentedfabricationlab/ur_online_control) 
into your project folder.

Then, add the following two directories to the Python Path in Rhino via >> EditPythonScript >> Tools >> Options >> Add to search path:

1. Ironpython Path, e.g., C:\Program Files\IronPython 2.7\Lib
2. Parent folder or ur_online_control repository, e.g., C:\Users\yourname\workspace\projects

## Example files

You find the `grasshopper playground` in the ghcomp folder:

Setup with one robot:

    ur_online_control_base_setup_x1.ghx
    u10e_setup_x1.3dm

Setup with two robots:

    ur_online_control_base_setup_x2.ghx
    u10e_setup_x2.3dm

Copy the rh and ghx files into your own project folder, use and modify it. Voilà!


![`grasshopper playground`](ghcomp/images/gui_example.png)

