from flask import request, Response, session
from . import blueprint

# load config
config = None;
with open("./config.yaml", 'r') as cfg:
    config = yaml.load(cfg);
tmp_dir = str(config.get("app", "tmp_dir"));
