import os, datetime, logging, yaml, pytz
from logging.handlers import RotatingFileHandler

from flask import Flask
from routes import *

if __name__ == '__main__':
    # load config
    config = None;
    with open("./config.yaml", 'r') as cfg:
        config = yaml.load(cfg);
    # create tmp and log dirs if they do not exist
    tmp_dir = str(config.get("app", "tmp_dir"));
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir);
    log_dir = str(config.get("app", "log_dir"));
    if not os.path.exists(log_dir):
        os.makedirs(log_dir);

    # starting flask
    print ' * Configuring Flask';

    # initialize app
    # http://blog.luisrei.com/articles/flaskrest.html
    app = Flask(__name__);
    # register routes Blueprint
    app.register_blueprint(blueprint); # retrieve and register routes from __init__py in routes dir
    
    # if debug=True -> it will print out possible Python errors on the web page
    app_debug = str(config.get("app", "debug"));
    app_host = str(config.get("app", "host"));
    app_port = int(config.get("app", "port"));
    if app_debug.lower().strip() == "true":
        app_debug = True;
    else:
        app_debug = False;
    # if the service is in production [debug=False]
    if not app_debug:
        # create log directory
        main_log_dir = config.get("app", "log_dir");
        # log dir name: (year)(month)(day)(hour)(minute)(second)
        #timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S');
        timestamp = datetime.datetime.now(tz=pytz.utc).isoformat();
        current_log_dir = os.path.join(main_log_dir, timestamp);
        if not os.path.exists(current_log_dir):
            os.makedirs(current_log_dir);
        # init log handler
        log_file_path = os.path.join(current_log_dir, 'app.log');
        log_max_bytes = int(config.get("app", "log_max_bytes"));
        log_backup_count = int(config.get("app", "log_backup_count"));
        log_handler = RotatingFileHandler(log_file_path, maxBytes=log_max_bytes, backupCount=log_backup_count);
        log_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'));
        log_handler.setLevel(logging.INFO);
        app.logger.addHandler(log_handler);
        app.logger.setLevel(logging.INFO);
        app.logger.info(application() + ' ['+release()+'] startup');
    # start Flask
    app.secret_key = os.urandom(16);
    app.run(debug=app_debug, host=app_host, port=app_port, threaded=True);
    
