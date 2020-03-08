[<img src="https://img.shields.io/badge/licence-AGPL--3-blue.png">](http://www.gnu.org/licenses/agpl-3.0-standalone.html)


# Business Process Management odoo app

B.P.M. is an integration between <a href="http://www.odoo.com">odoo</a> (12) and <a href="https://www.processmaker.com/">ProcessMaker</a> (3.2)


## Installation

Install the app syd_process_maker in odoo.

Create a Process Group of type ProcessMaker and add the authentication parameter.

To obtain the ProcessMaker authentication parameter goes on your ProcessMaker installation  http://{pm-server}/sys{workspace}/en/neoclassic/oauth2/applications and create a new application called odoo.

## Configuration

Design a Process in ProcessMaker goes to odoo and click on Update on your ProcessGroup.

Odoo will read all the process that you have made in ProcessMaker.

### Configure Process

You can configure your process activity.
Each activity can be:

#### Manual Activities
The Manual activities will create a note to the user that have to be complete. For manual activities you can user
	Specific User: The user specified
	User of Process Case : The user that you insert in your Launch Process Form
	Dynamic User: User inside a Process Object
	Process Role: User of a specific role (selected based on a Rule)

#### Automated Activities
Activities of this type will execute an odoo Server Action

#### Subprocess Activities
Activities of this type will launch another process

### Configure Process Object
Process Objects are object manipulated inside a process (case). Process Objects can be ProcessMaker variable or odoo specific object.
Each variable create inside ProcessMaker will create automatically a Process Object inside odoo.

In the execution you can manipulate the process object in two way:

#### Dynamic Form
You can create dynamic form linked with a specific manual activity. The user, before completing the note, have to compile the form updating the value of a Process Object

#### Code Context
Inside the context of the code of an Automated activity you will access all the process object through their name.

### Executing Process
You can launch a Process in two ways:

#### Contextual action
Selecting a process (that have the startable flag, selected) you can chose the action Process Start

#### Trigger
You can create a Automated Action Launch a BPM process . In this automated action you will add also the code (with all the process object inside the context) that will be executed after the launch.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

### License
[AGPL3](http://www.gnu.org/licenses/agpl-3.0-standalone.html)
