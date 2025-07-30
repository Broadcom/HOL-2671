#!/usr/bin/env python
# version 1.1 03-February 2023
# Huge thanks to HOL Captain Nick Robbins for developing this tool.

import os
import pathlib
import FreeSimpleGUI as sg
import argparse
import base64
import subprocess
import sys
sys.path.append('/hol')
sys.path.append('/home/holuser/py312venv/lib')
#import ansible_runner


base_env = os.environ.copy()
base_env['http_proxy'] = "http://proxy:3128"
base_env['https_proxy'] = "http://proxy:3128"
base_env['no_proxy'] = "localhost,127.0.0.0/8,::1,vcf.sddc.lab,10.0.0.87,10.0.1.87,10.0.0.0/8,avicon-01a,avicon-01b,172.16.0.0/16"
base_env['HTTP_PROXY'] = "http://proxy:3128"
base_env['HTTPS_PROXY'] = "http://proxy:3128"
base_env['NO_PROXY'] = "localhost,127.0.0.0/8,::1,vcf.sddc.lab,10.0.0.87,10.0.1.87,10.0.0.0/8,avicon-01a,avicon-01b,172.16.0.0/16"

parser = argparse.ArgumentParser(description="Hands-on Labs Module Switcher")

# parser.add_argument('--sku',action="store", dest="sku")
parser.add_argument('--dir', action="store", dest="workdir",
                    help="Working directory, optional, will use current working directory if not specified")

args = parser.parse_args()
scriptfolder = 'module-scripts'

if args.workdir is None:
    args.workdir = os.getcwd()


skupath = os.path.join(args.workdir, 'skulist.txt')
script_path = os.path.join(args.workdir, scriptfolder)
icon_path = os.path.join(args.workdir, 'hol-logo.png')

iconb64 = base64.b64encode(open(icon_path, 'rb').read())
panel_name = 'Hands-on Labs Module Switcher'


def sort_and_dedupe_list(the_list):
    """remove duplicates from and sort a list"""
    the_new_list = list(set(the_list))
    the_new_list.sort()
    return the_new_list


class ButtonPanel:
    def __init__(self, module_scripts):
        sg.theme('LightBlue7')
        layout_buttons = []
        # print(rows)
        """
        from https://stackoverflow.com/questions/9671224/split-a-python-list-into-other-sublists-i-e-smaller-lists/9671301
        """
        chunks = [module_scripts[x:x + 4] for x in range(0, len(module_scripts), 4)]
        # print(chunks)
        for the_list in chunks:
            # print(f"this is the list: {the_list}")
            row = []
            for item in the_list:
                # print(f"this is the item: {item}")
                script_str = str(item)
                row.append(sg.Button(script_str.replace(script_path + '/', "").split(".", 1)[0],
                                     size=(20, 1),
                                     key=script_str.replace(script_path + '/', ""),
                                     button_color='dodgerblue4'))
            layout_buttons.append(row)

        modulelayout = [
            [layout_buttons],
            [sg.Text('Script output....', size=(40, 1))],
            [sg.Output(size=(88, 20), font='Courier 10', text_color='black', background_color='white')],
        ]

        window = sg.Window('Select Hands-on Labs Module', modulelayout, icon=iconb64, auto_size_buttons=True)

        while True:
            panelevent, values = window.read()
            if panelevent == 'EXIT' or panelevent == sg.WIN_CLOSED: #  or panelevent is None:  This seems to make the window insta-close after run is over.
                exit(0)
            cmd = ["/home/holuser/py312venv/bin/ansible-playbook",
                "-e ANSIBLE_HOST_KEY_CHECKING=False",
                f"{script_path}/{panelevent}",
                "-v"]

            ##saving for posterity, this also works.  Key to avoiding ansible's double carriage returns is the 
            ## end='' in the print statement.  You can do this with binary strings, or with text strings.
            ##

            # process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            # while True:   # Could be more pythonic with := in Python3.8+
            #     line = process.stdout.readline()
            #     if not line and process.poll() is not None:
            #         break
            #     print(line.decode(), end='', flush=True)
            #     window.refresh()


            with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=base_env) as p:
                for line in p.stdout:
                    print(line.decode(), end='', flush=True)  ## end='' is very important!
                    window.refresh()  ## this is also very important for returning immediate text response.

            # if p.returncode != 0:
            #     raise CalledProcessError(p.returncode, p.args)  


if __name__ == '__main__':
    sg.theme('LightBlue7')
    skulist = open(skupath).readlines()
    layout = [
        [sg.Text('Please Select the Lab', size=(50, 1))],
        [sg.Listbox(values=skulist,
                    key="skulist",
                    size=(50, len(skulist)),
                    text_color='black',
                    background_color='ghost white')],
        [sg.Button('Go to Module Selection', button_color='dodgerblue4')]
    ]
    if len(skulist) > 1:
        win = sg.Window('Hands-on Labs Module Switcher', layout, icon=iconb64)
        event, sku = win.read()
        if event is None:
            exit(1)
        while len(sku['skulist']) == 0:
            event, sku = win.read()
        win.close()
        skuname = (sku['skulist'][0])[4:11]
    else:
        skuname = (skulist[0])[4:11]

    list_of_scripts = []
    if os.path.exists(script_path) and os.path.isdir(script_path):
        list_of_scripts = [p for p in pathlib.Path(script_path).glob(f"{skuname}-module*.yaml") if p.is_file()]

    sorted_list_of_scripts = sort_and_dedupe_list(list_of_scripts)
    ButtonPanel(sorted_list_of_scripts)

