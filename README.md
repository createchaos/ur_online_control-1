


<!-- TABLE OF CONTENTS -->
## Table of Contents

* [About the Project](#About)
* [Setup](#Setup)
* [Usage](#usage)
* [WIP](#WIP)




<!-- ABOUT THE PROJECT -->
## UR Remote Control w/Speckle <a name="About"></a>

We use the ur_online_control libary with Speckle to control UR3 robotic manipulators.
We also use the assembly_information_model library to send more complicated sets of geometry/commands for the robot, as a Compas network class object (Python).



<!-- GETTING STARTED -->
## Setup
To get a local copy up and running follow these simple steps.

### Prerequisites
* Anaconda (and Python)
* Rhino 6 and Grasshopper
* Compas and Compas_Fab

### Installation
1. From Github get:
   - ur_online_control
   - assembly_information_model
2. Install [Speckle](https://github.com/speckleworks/SpeckleInstaller/releases/tag/1.8.31)
    - restart rhino and grasshopper after installing plugin
    -
<!-- USAGE EXAMPLES -->
## Usage
Example files are in the [Rhino](/rhino) folder of this repo. Load the UR3_ECL_setup.3dm file to visualize our robot cell setup in the ECL.

### Speckle
Log into Speckle via Default Authentification method
username: ianting@princeton.edu
password: arc311_f2020
The speckle components have been already set up in the grasshopper files, you just need

### UR Simple Commands
Use the [ur_simple_speckle.gh](/rhino) file
This sends ur_script commands as strings through Speckle

### UR Assemblies
Use the [ur_assemply_speckle.gh](/rhino) file
This sends an assembly information model through json. The movement planes in this datastructure are interpreted as movement frames for the robot.

<!-- WIP -->
# WIP

### Setup Instructions w/ annotations

###### 1. Compas and Compas_Fab Installation (via Anaconda Terminal); clean install

#### Run Anaconda prompt as admin

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

###### 2. Verify Installation
    ```ruby
    (your_env_name) python
    >>> import compas_fab
    >>> compas_fab.__version__
    '0.10.1'
    >>> exit()
    ```

###### 3. Iron Python Installation
    Install Ironpython 2.7.9. via this link: https://github.com/IronLanguages/ironpython2/releases/tag/ipy-2.7.9
    > New version of IronPython is out: 2.7.10; probably unnecessary since it only adds .net support
    > For Windows: use the .msi file
    > For Apple: use the .pkg file

###### 4. UR Online Control Installation
    Clone the current version of the ur_online_control repository onto your computer: https://github.com/augmentedfabricationlab/ur_online_control
    > Clone into a git_repositories folder that you have set up, or into your project folder.
    > I recommend having a folder called git_repositories (or similar) somewhere on your hard drive and downloading all git repos to that location:
    Clone using Github Desktop or the terminal:
    instructions 1
    instructions 2: https://git-scm.com/book/en/v2/Git-Basics-Getting-a-Git-Repository

###### 5. Link Directories to Rhino Search Path
    Add the directories for ur_conline_control and IronPython to Rhino: `Rhino >> EditPythonScript >> Tools >> Options >> Add to search path:`
    1. Ironpython install directory, e.g. C:\Program Files\IronPython 2.7\Lib
    2. ur_online_control repository or its parent directory, e.g. C:\Users\YourName\Desktop\git_repositories

###### 6. Test w/ robots:
Files are in the rhino folder of ur_online_control repo

Rhino File: ExampleRobotSimple.3dm

Grasshopper File: ExampleRobotSimple.gh
- verify which UR3 has which ip
  - toolbox one is 192.168.10.10
- set the robot ip in the grasshopper script
- choose ip for server (pc) and set it as the computer's ipv4 ip under network adapter properties
- port for the robot is preset: 30002
- port for server (pc) is set to: 30003

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
