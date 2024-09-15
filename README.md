# Budget manager

Users may follow their spending habbits, create budgets and view their assets. The goal of this project is to be a virtual checkbook.

### This application or it's author WILL NOT
- use the information against the users, for example to advertise to them or sell the data to any advertisers.
- control users' assets.
- manage the finances for the user.
- provide any kind of financial guidance for the users.

## Features
- [ ] Graphs.
  - [ ] Asset value graphs.
  - [ ] Spendings graphs.
  - [ ] Projected value graphs.
- [ ] Users may add their receipts to the system.
  - [ ] Each receipt can be broken down line-by-line, product-by-product.
  - [ ] Each line item may have their sales and one-off markdowns added for more insights.
  - [ ] Each line item may be linked to another when comparing vendors.
- [ ] Users may add assets and keep track of them.
  - [ ] Users may view their assets and add new ones as they wish.
    - [ ] Each asset has it's own history associated with it.
      - [ ] Users may view and interact with said history.
  - [ ] Users may delete their assets and the associated history.
- [ ] Users may create groups.
  - [ ] Users may review expenses in their own groups.
  - [ ] Users may add expenses in their own groups (depending on their rights in the group).
  - [ ] Users may mark their contributions towards expenses in their own groups.
  - [ ] Users may create one-off groups for event and such.

## Setup guide
### Server
The setup for the server can be done by following the part 1 of the Tsoha material or by follwing these steps:
- Install `python3` onto your system. If you only have one version of python installed you can verify the version by running command `python --version` otherwise try `python3 --version` instead. Note that on some platforms `pip` is not bundled with `python` or isn't setup in the path, but it should still work in the virtual environment we are about to setup. If you encounter any problems regarding the `flask.sh` -script, first try installing `pip` on your machine.
  > You should already have these installed if you are using Cubbli.
- Setup your virtual environment by running `python -m venv venv` or `python3 -m venv venv` if `python` returned anything else than `3.x.y`. This will create a folder called `venv` in the current working directory so make sure you are inside the project folder.
- Once the virtual environment is ready to be run. Run the following command `source venv/bin/activate`. Now you are in the environment (this is noted by `(venv)` in the terminal window).
- In the virtual environment install all the requirements by running `pip install -r ./requirements.txt` and the server with `flask --app src/main.py run`
- To stop the server press `CTRL+C` and run command `deactivate` to exit the virtual environment.

### Database
- TBD

## Usage guide
- TBD
