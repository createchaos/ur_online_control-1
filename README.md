


<!-- TABLE OF CONTENTS -->
## Table of Contents

* [About the Project](#About)
* [Setup](#Setup)
* [Usage](#Usage)
* [Appendix](#Appendix)




<!-- ABOUT THE PROJECT -->
# UR Remote Control w/Speckle <a name="About"></a>

We use the ur_online_control libary with [Speckle](https://speckle.systems/) to send commands to UR robotic manipulators remotely.
We can also use the [assembly_information_model](https://github.com/createchaos/assembly_information_model) library to send more complicated sets of geometry/commands for the robot, encoded as a Compas network class object in Python.


<!-- GETTING STARTED -->
## Setup

### Prerequisites
We work in Rhino 6 and Grasshopper. Follow the instructions [here](https://github.com/createchaos/create_documentation/blob/master/README.md) to install the following:
* Python 3 via Anaconda
* Compas and Compas_Fab
* [assembly_information_model](https://github.com/createchaos/assembly_information_model) (optional, if you want to use the Assembly datastructure)

### Installation
1. From Github clone:
   - [ur_online_control_speckle](https://github.com/createchaos/assembly_information_model) (this repository)
   - make sure [directories are added to Rhino](###Link_Directories_to_Rhino_Search_Path)
2. Install [Speckle](https://github.com/speckleworks/SpeckleInstaller/releases/tag/1.8.31)
    - restart Rhino and Grasshopper after installing plugin to make sure it loads correctly


<!-- USAGE EXAMPLES -->
## Usage
Example files are in the [Rhino](/rhino) folder of this repo. Load the UR3_ECL_setup.3dm file to visualize the robot cell setup in the ECL.

### Speckle
Log into Speckle via Default Authentication method
* username: ianting@princeton.edu
* password: arc311_f2020
* server: https://hestia.speckle.works/api

The speckle components have been already set up in the grasshopper demo files, but you need to set the above username/password as the default account, and then restart Rhino because the Speckle Grasshopper client checks for the default account when the file loads, so you want to make sure the information is already saved in the system.

### UR Simple Commands
Use the [ur_simple_speckle.gh](/rhino) file
This sends ur_script commands as strings through Speckle

### UR with Assemblies
Use the [ur_assemply_speckle.gh](/rhino) file
This sends an assembly information model in a JSON file. The planes in each "element" in this datastructure are interpreted as movement frames for the robot.


<!-- WIP -->
# Appendix

## Setup Instructions w/ annotations

### Iron Python Installation
Install Ironpython 2.7.9. via this link: https://github.com/IronLanguages/ironpython2/releases/tag/ipy-2.7.9
IronPython is the version of Python used by Grasshopper and Rhino
> New version of IronPython is out: 2.7.10; probably unnecessary since it only adds .net support
> For Windows: use the .msi file
> For Apple: use the .pkg file

### Compas and Compas_Fab Installation (via Anaconda Terminal); clean install

1. Run Anaconda prompt as admin:

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

2. Verify Installation
    ```ruby
    (your_env_name) python
    >>> import compas_fab
    >>> compas_fab.__version__
    '0.10.1'
    >>> exit()
    ```


### ur_online_control Installation
[Clone](https://git-scm.com/book/en/v2/Git-Basics-Getting-a-Git-Repository) the current version of the ur_online_control repository onto your computer: https://github.com/augmentedfabricationlab/ur_online_control
> It is recommended to have a folder called git_repositories (or similar) somewhere on your hard drive and cloning/downloading all git repos to that location.


### assembly_information_model Installation
Clone the assembly_information_model repository to your computer, from here: https://github.com/augmentedfabricationlab/assembly_information_model
> Dependencies (compas, compas_fab, and ur_online_control) should be installed already).

And now make the assembly_information_model repo accessible from Rhino:
1. `cd` to the repository directory in the Anaconda prompt
2. ```
    pip install -r requirements-dev.txt
    invoke add-to-rhino
    pip install your_filepath_to_assembly_information_model
    ```

3. Add the src folders from each of the two repositories to your rhino paths: `Rhino >> Command:EditPythonScript >> Tools >> Options >> Module Search Paths >> Add to search path >> press Ok >> restart Rhino`


### Link Directories to Rhino Search Path
Add the directories for IronPython, ur_online_control, and  to Rhino: `Rhino >> EditPythonScript >> Tools >> Options >> Module Search Paths >> Add to search path >> press Ok >> restart Rhino`
* Ironpython install directory, e.g. C:\Program Files\IronPython 2.7\Lib
* ur_online_control repository src folder or its parent directory, e.g. C:\Users\YourName\Desktop\git_repositories\ur_online_control\src
* assembly_information_model src folder or its parent directory, e.g. C:\Users\YourName\Desktop\git_repositories\assembly_information_model\src

### Test w/ robots:
Files are in the rhino folder of ur_online_control repo

Rhino File: ExampleRobotSimple.3dm

Grasshopper File: ExampleRobotSimple.gh
- verify which UR3 has which ip
  - toolbox one is 192.168.10.10
- set the robot ip in the grasshopper script
- choose ip for server (pc) and set it as the computer's ipv4 ip under network adapter properties
- port for the robot is preset: 30002
- port for server (pc) is set to: 30003
