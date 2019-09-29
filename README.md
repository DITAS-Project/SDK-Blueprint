# DITAS SDK-BluePrint Generator

This is the DITAS SDK CLI to generate a BluePrint starting from VDC and DALs repositories.

### Requirements

- git CLI installed on your system
- A github account with read/write access to DITAS projects
- A personal access token for git CLI: refer to the official 
[guide](https://help.github.com/en/articles/creating-a-personal-access-token-for-the-command-line)
- Create a file `github_access.json` (a file with this name will be ignored by git, because of the related entry in the 
`.gitignore` file) in the main folder with the following structure
```
{
	"access_token": "{your access token}"
}
```

- Install the SDK-BluePrint with the command

`sh install.sh`


### CLI usage
Running the command `sh sdk-bp.sh -h` it is shown the helper of the CLI
```
usage: main.py [-h] {create,update,repo-init,std-metrics} ...

DITAS SDK-Blueprint Generator.

positional arguments:
  {create,update,repo-init,std-metrics}
                        Sub-command to create or update a blueprint, or to
                        setup a new repository
    create              Generate a new blueprint. An already existing
                        blueprint is overwritten.
    update              Update an existing blueprint. Only the parts specified
                        in the configuration files of the repositories will be
                        overwritten.
    repo-init           Create a new GitHub repository with the default
                        structure.
    std-metrics         Create a json file for each API method with the
                        default data metrics. The path is specified by the
                        attribute "data-management" of the VDC configuration
                        file.

optional arguments:
  -h, --help            show this help message and exit
```
Ideally, each VDC and DAL should have a dedicated repository with a configuration file (`bp_gen_vdc.cfg` and `bp_gen_dal.cfg` respectively). Each file contains the information required by the SDK to properly generate a BluePrint.

Each URL can be either SSH or HTTPS, this choice will determine the way the SDK authenticates the user to the corresponding repositories.
Using HTTPS, the CLI prompts GitHub username and password for cloning and pushing.

### Examples

For testing purposes, the [IDEKO use case](https://github.com/DITAS-Project/ideko-use-case/) has been cloned [here](https://github.com/caloc/ideko-copy). Both VDC and DAL configuration files have been added since this repository contains both modules.

##### Create command

`python main.py create git@github.com:caloc/ideko-copy.git`

Since no DAL_URL has been provided, the SDK assumes that the provided VDC_URL contains both of them. So it looks for both VDC and DAL configuration files. This command will generate a brand new BluePrint and store it at the location defined in the section "blueprint" of `bp_gen_vdc.cfg`

##### Update command

`sh sdk-bp.sh create git@github.com:caloc/ideko-copy.git`

The same assumption described in the previous section applies.
The update command locates the existing blueprint defined in the section "blueprint" of `bp_gen_vdc.cfg` and modifies only those sections affected by the information provided in the configuration file.
Other blueprint sections, including those that have been filled manually, are not modified.

##### Repo-init command

`sh sdk-bp.sh repo-init VDC newvdcname`

This command will create a new VDC repository into the DITAS-Project GitHub organization and initializes it with the standard [VDC template](https://github.com/DITAS-Project/SDK-Blueprint/tree/master/vdc_template).

##### Std-metrics command

`sh sdk-bp.sh std-metrics GIT_URL`

This command will create a JSON file for each API method in the path set by the
attribute "data-management" in the configuration file. The file contains all the
Data Quality, QoS, Security and Privacy metrics that can be computed.
The administrator should edit these files and remove those metrics which are not
consistent with the specific method. Then the create or update command can be
launched.

### Scenarios

##### Brand new project

The administrator wants to create a new repository for either a VDC or DAL.
1. To create one with the standard DITAS structure, the command to run is
`repo-init`.

2. Once the developers had implemented enough, in order to generate a blueprint
the file `bp_gen_vdc.cfg`/`bp_gen_dal.cfg` has to be filled.

3. One can specify the Data Quality, QoS, Security and Privacy metrics of the
API methods to compute by running the `std-metrics` command.

4. The blueprint can be generated
  - from scratch (and replacing an existing one, if the file indicated by the attribute `blueprint` in the configuration file already exists) with the command `create`

  - or by updating an existing one, specified by the attribute `blueprint` in the configuration file, with the command `update`. This command edit only the
  sections that are mentioned in the configuration file.

##### BP generation of existing VDC/DAL

Refer to points 2, 3 and 4 of the "Brand new project scenario".


##### TODO

Refer to [TODO file](https://github.com/DITAS-Project/SDK-Blueprint/blob/master/TODO.md)
