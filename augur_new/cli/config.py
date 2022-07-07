#SPDX-License-Identifier: MIT
"""
Augur library script for generating a config file
"""

import os
import click
import json
import logging
from pathlib import Path

from augur.config import default_config, ENVVAR_PREFIX, CONFIG_HOME
from augur.cli import initialize_logging
from augur.logging import ROOT_AUGUR_DIRECTORY

from db.models import Config
from tasks.task_session import TaskSession
from db_config import AugurConfig

logger = logging.getLogger(__name__)
ENVVAR_PREFIX = "AUGUR_"

@click.group('config', short_help='Generate an augur.config.json')
def cli():
    pass

@cli.command('create-default')
def create_default():

    config =get_config()

    session = TaskSession(logger, config)

    config = AugurConfig(session)

    if not config.empty():

        print("Warning this will override your current config")
        response = str(input("Would you like to continue: [y/N]: ")).lower()

        if response != "y" and response != "yes":
            print("Did not recieve yes or y exiting...")
            return


        config.clear()

    config.create_default_config()        

@cli.command('load')
@click.option('--file', required=True)
def load_config(file):

    print("WARNING: This will override your current config")
    response = str(input("Would you like to continue: [y/N]: ")).lower()

    if response != "y" and response != "yes":
        print("Did not recieve yes or y exiting...")
        return

    config = get_config()

    session = TaskSession(logger, config)

    config = AugurConfig(session)

    file_data = config.load_config_file(file)

    config.clear()
    
    config.load_config_from_dict(file_data)
    
@cli.command('add-section')
@click.option('--section-name', required=True)
@click.option('--file', required=True)
def add_section(section_name, file):

    config =get_config()

    session = TaskSession(logger, config)

    config = AugurConfig(session)

    if config.is_section_in_config(section_name):

        print(f"Warning there is already a {section_name} section in the config and it will be replaced")
        response = str(input("Would you like to continue: [y/N]: ")).lower()

        if response != "y" and response != "yes":
            print("Did not recieve yes or y exiting...")
            return

    config.remove_section(section_name)
            
    with open(file, 'r') as f:
        section_data = json.load(f)

    config.add_section_from_json(section_name, section_data)


@cli.command('set')
@click.option('--section', required=True)
@click.option('--setting', required=True)
@click.option('--value', required=True)
@click.option('--data-type', required=True)
def config_set(section, setting, value, data_type):

    config = get_config()

    session = TaskSession(logger, config)

    config = AugurConfig(session)

    if data_type not in config.accepted_types:
        print(f"Error invalid type for config. Please use one of these types: {config.accepted_types}")
        return

    
    setting = {
        "section_name": section,
        "setting_name": setting, 
        "value": value,
        "type": data_type
    }

    config.add_or_update_settings([setting])
        
        

@cli.command('get')
@click.option('--section', required=True)
@click.option('--setting')
def config_get(section, setting):

    config = get_config()

    session = TaskSession(logger, config)

    config = AugurConfig(session)

    if setting:
        config_value = config.get_value(section_name=section, setting_name=setting)

        if config_value is not None:
            print(f"======================\n{setting}: {config_value}\n======================")
        else:
            print(f"Error unable to find '{setting}' in the '{section}' section of the config")
               
    else:
        section_data = config.get_section(section_name=section)
        
        if section_data:
            print(f"======================\n{section}\n====")
            section_data_keys = list(section_data.keys())
            for key in section_data_keys:
                print(f"{key}: {section_data[key]}")

            print("======================")

        else:
            print(f"Error: {section} section not found in config")

@cli.command('clear')
def clear_config():

    config = get_config()

    session = TaskSession(logger, config)

    config = AugurConfig(session)

    if not config.empty():

        print("Warning this delete the current config")
        response = str(input("Would you like to continue: [y/N]: ")).lower()

        if response != "y" and response != "yes":
            print("Did not recieve yes or y exiting...")
            return

    config.clear()

    print("Config cleared")

def get_config():

    current_dir = os.getcwd()

    root_augur_dir = ''.join(current_dir.partition("augur/")[:2])

    config_path = root_augur_dir + '/augur_new/augur.config.json'

    with open(config_path, 'r') as f:
        config = json.load(f)

    return config
