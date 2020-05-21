from flask_migrate import Migrate, MigrateCommand
from app import app
from dbmodels.dbmodels import db
from flask_script import Manager

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

"""
To manage changes to DB once database is initialize and is in use. To upgrade database with changes in db Models,
-- First make changes in dbmodels.py
-- After changes are made, run following commands from project directory:
    $ python manager.py db init
    $ python manager.py db migrate
    $ python manager.py db upgrade
    $ python manager.py db --help 
"""

if __name__ == '__main__':
    manager.run()