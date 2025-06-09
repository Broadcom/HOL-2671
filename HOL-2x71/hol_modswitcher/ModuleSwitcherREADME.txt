version 1.2 03-February 2023

                     README for LMC Module Switcher

In order to remove module dependencies, the ModuleSwitcher provides a way
for attendees to automate the completion of dependencies by calling your
scripts. Thank you to Hands-on Labs Captain Nick Robbins who designed and
implemented this essential tool for us.

                      Initialize the environment

Enter your lab SKUs and titles in the example skulist.txt file.
Should anything change after replication, the Core Team can update.

To get you started, the createshells.sh script will create placeholders for 
your moduleswitcher scripts based on the skulist.txt. It will create placeholder
scripts for 8 modules per lab SKU in the module-scripts folder. You can delete 
the scripts you do not need. You can edit the createshells.sh script to change
the number of placeholder scripts it creates.

Run the createlaunch.sh script to add the Module Switcher desktop launcher
shortcut to the LMC desktop.

                       Start the Module Switcher

Double click on the Module Switcher shortcut on the desktop. If you have multiple
lab skus in the skulist.txt, you will see an initial panel to select the sku and
then the second panel that shows a button for each module. Pressing the button
starts the associated script.

If you have only a single lab SKU, then only the menu to choose the module will
be shown.

                     Develop the Module Switcher Scripts

Using command line, API, Ansible, PowerShell or any tool you choose, complete
the module switcher script to complete the dependcies for the chosen module.

                     Edit the Module Switcher using Python

If needed or desired, the module switcher can directly run a different script or
Python Ansible as an example. The Module Switcher code is in the main_ui.py file.


