# hotel-website

## Requirements
* [Python 3.9](https://www.python.org/downloads/)

## Python Requirements
Before trying to install the python requirements, read the readme for mysqlclient, as the steps before installing via pip differ depending on which OS you use. https://pypi.org/project/mysqlclient/.

There are no instructions for Windows, but this stack overflow thread seems to explain the process: https://stackoverflow.com/questions/26866147/mysql-python-install-error-cannot-open-include-file-config-win-h. I don't use Windows for development, so I can't verify that this solution works, apologies.

Install these using pip. The command `python -m pip install -r requirements.txt` should work, but please do ensure you're using the python executable that you want to eventually run the website with.
* [Flask 2.0](https://pypi.org/project/Flask/)
* [mysqlclient](https://pypi.org/project/mysqlclient/)
* [flask_login](https://pypi.org/project/Flask-Login/)
* [flask_wtf](https://pypi.org/project/Flask-WTF/)
* [wtforms_components](https://pypi.org/project/WTForms-Components/)
* [flask_sqlalchemy](https://pypi.org/project/Flask-SQLAlchemy/)
* [flask_admin](https://pypi.org/project/Flask-Admin/)

## Config and running flask
Now that all the requirements are installed, create your database. Then make a copy of the file `config.json.example` renaming it to `config.json`. It resides in the `instance` directory. Edit the example database uri provided with the correct information to connect to your database. See: https://docs.sqlalchemy.org/en/14/core/engines.html#mysql for the documentation on this.

This project is set up to use the [flask cli](https://flask.palletsprojects.com/en/2.0.x/cli/). You will need to set the `FLASK_APP` environment variable to `run.py`, and the `FLASK_ENV` environment variable to `development` before proceeding for any commands beginning with `flask` to run.

To create the tables of the database, you will need to run the command: `flask createdb`.

To populate the database, run the command: `flask filldb`.

Now you can run the website with the command: `flask run`.