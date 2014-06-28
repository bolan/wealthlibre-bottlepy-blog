# Change working directory so relative paths (and template lookup) work again

import os, sys
sys.path = ['/PATH/OF/YOUR/WEBSITE'] + sys.path
os.chdir(os.path.dirname(__file__))

import bottle

import mycode # This loads your application

application = bottle.default_app()