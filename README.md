# UR Online Control

## Iron Python Installation

Install Ironpython 2.7.9. via following this [link](https://github.com/IronLanguages/ironpython2/releases/tag/ipy-2.7.9)

## Compas Fab Installation

Use the `afab19` environment and update it as follows:

    (base)  conda activate afab19
    (afab19) conda install compas=0.11 compas_fab=0.9 --yes
    (afab19) python -m compas_rhino.install
    (afab19) python -m compas_fab.rhino.install -v 6.0

### Installation Problems

If you run into problems, please remove and reinstall your `afab19` environment as follows:
    
    (base)  conda config --add channels conda-forge
    (base)  conda remove --name afab19 --all
    (base)  create -n urfab python=3.6 compas=0.11 compas_fab=0.9 matplotlib=3.0 --yes
    (base)  conda activate urfab

## Jupyter Notebooks Installation

Some examples will also use Jupyter Notebooks, which needs to be installed **in the same environment**:

    (afab19) conda install jupyter rise pythreejs jupyter_contrib_nbextensions jupyter_nbextensions_configurator --yes

## Verify Installation

    (afab19) python
    >>> import compas_fab
    >>> compas_fab.__version__
    '0.9.0'
    >>> exit()

## Additonal Python 2.7 Environment Installation

Create a Python 2.7 `uronl` environment as follows:
    
    (base)  conda create -n uronl python=2.7.16
    (base)  conda activate uronl

## UR Online Control Installation

First, clone the current version of the [ur_online_control repository](https://github.com/augmentedfabricationlab/ur_online_control) 
into your project folder.

Then, add the following two directories to the Python Path in Rhino via >> EditPythonScript >> Tools >> Options >> Add to search path:

1. Ironpython Path, e.g., C:\Program Files\IronPython 2.7\Lib
2. Parent folder or ur_online_control repository, e.g., C:\Users\yourname\workspace\projects

## Example files

You find the `grasshopper playground` in the ghcomp folder:

    ur_online_control.ghx
    ur10e_setup.3dm

Copy these two files into your own project folder and use and modify it.

![`grasshopper playground`](ghcomp/images/ghcomp_interface.jpg)

