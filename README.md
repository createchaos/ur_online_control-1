# UR Online Control
### Setup Instructions w/ annotations

1. ###### Compas and Compas_Fab Installation (via Anaconda Terminal); clean install

    ```ruby
    (base)  conda config --add channels conda-forge
    #--add channels         //puts the conda-forge channel at the top of the channels priority list;
    #                       //can also use --prepend; --append adds to bottom of list
    #conda config --show    //will show info about conda config, including existing channels
    (base)  conda remove --name your_env_name --all
    #removes the environment if already exists

    (base)  conda create -n your_env_name python=3.8 compas compas_fab --yes
    #use newest versions instead
    #--yes or -y simply skips confirmation
    (base)  conda activate your_env_name
    (your_env_name) python -m compas_rhino.install
    #from python documentaiton: When called with -m module-name, the given module is located on the Python module path and executed as a script.
    (your_env_name) python -m compas_fab.rhino.install -v 6.0
    ```

2. ###### Verify Installation
    ```ruby
    (your_env_name) python
    >>> import compas_fab
    >>> compas_fab.__version__
    '0.10.1'
    >>> exit()
    ```

3. ###### Iron Python Installation
    Install Ironpython 2.7.9. via this link: https://github.com/IronLanguages/ironpython2/releases/tag/ipy-2.7.9
    > New version of IronPython is out: 2.7.10; probably unnecessary since it only adds .net support
    > For Windows: use the .msi file
    > For Apple: use the .pkg file

4. ###### UR Online Control Installation
    Clone the current version of the ur_online_control repository onto your computer: https://github.com/augmentedfabricationlab/ur_online_control
    > Clone into a git_repositories folder that you have set up, or into your project folder.
    > I recommend having a folder called git_repositories (or similar) somewhere on your hard drive and downloading all git repos to that location:
    Clone using Github Desktop or the terminal:
    instructions 1
    instructions 2: https://git-scm.com/book/en/v2/Git-Basics-Getting-a-Git-Repository

5. ###### Link Directories to Rhino Search Path
    Add the directories for ur_conline_control and IronPython to Rhino: `Rhino >> EditPythonScript >> Tools >> Options >> Add to search path:`
    1. Ironpython install directory, e.g. C:\Program Files\IronPython 2.7\Lib
    2. ur_online_control repository or its parent directory, e.g. C:\Users\YourName\Desktop\git_repositories


---


### ur_online_control_assembly instructions

UR setup example files:
- u10e_setup_x1.3dm
- ur_online_control_assembly.ghx

**Setup / Dependency Install**

In order for them to work you’ll have to install the following:

1. Install ur_online_control and its dependencies, including compas and compas_fab, by following the readme instructions
    > ~~ATTENTION: The compas and compas_fab versions mentioned in the instructions are wrong (old). You will need to install the latest version which you can do by simply not typing a version (example: conda install compas) or using version 0.15.6 for compas and 0.11.0 for compas_fab.~~
    > When you run the compass_rhino and compass_fab.rhino installs (in python), you will need to have the anaconda prompt open as administrator, so it can make changes to your rhino folders.

2. Clone the assembly_information_model repository to your computer, from here: https://github.com/augmentedfabricationlab/assembly_information_model
    > Dependencies (compas) are already installed.

3. Make the assembly_information_model repo accessible from Rhino:
   1. `cd` to the repository directory in the Anaconda prompt
   1. ```
        pip install -r requirements-dev.txt
        invoke add-to-rhino
        pip install your_filepath_to_assembly_information_model
        ```

4. Add the src folders from each of the two repositories to your rhino paths: `Rhino >> Command:EditPythonScript >> Tools >> Options >> Module Search Paths >> Add to search path >> press Ok >> restart Rhino`
    > It doesn’t matter where, this is needed to make sure it remembers the changes in the paths. You can then delete it

---

## Getting started (original)
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
    (your_env_name) conda install compas=0.11.4 compas_fab=0.10.1 --yes
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

You find the `grasshopper playground` in the ghcomp folder:

Setup with one robot:

    ur_online_control_base_setup_x1.ghx
    u10e_setup_x1.3dm

Setup with two robots:

    ur_online_control_base_setup_x2.ghx
    u10e_setup_x2.3dm

Copy the .3dm and .ghx files of your choice into your own project folder, use and modify it. Voilà!


![`grasshopper playground`](ghcomp/images/gui_example.PNG)
