import os
import yaml
from app.app import app

print(app.static_folder.lower())
config = os.path.join(os.path.dirname(os.path.realpath(__file__)), "appconfigs/lims_user_config")
config_options = yaml.safe_load(open(config, "r"))
DEBUG = False
ENV = config_options['env']
if ENV == 'local' or ENV == 'dev':
    DEBUG = True
elif ENV == 'prod':
    DEBUG = False

"""
Run this file to start the application when running locally. In production we will use nginx and uwsgi.
"""
# dev, this is how python runs the app
if __name__ == "__main__":
    app.run(debug=DEBUG, threaded=True)
