from flask import Flask
import logging
import os
import json

app = Flask(__name__)

def load_config(config_path: str):

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"The config file {config_path} does not exist.")

    with open(config_path, 'r') as f:
        config = json.load(f)
    return config

# Load the config file
config = load_config('config.json')
app.config.update(config) # Pass the config to the Flask app





@app.route('/')
def index():
    return f"Debug mode is {'on' if app.config['DEBUG'] else 'off'}"

if __name__ == '__main__':
    app.run()


