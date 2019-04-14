## Introduction

Caution: The scripts in this repository have no stable-state currently!

In this repository scripts should be created which allow to automatically determine characteristical evidences (the characteristical changes in the filesystem) which a (arbitrary) program/action produces. (The theoretical backgrounds can be found [here](https://pdfs.semanticscholar.org/5c5a/7cc3eada8f528606fc5a15d76063a3d3d530.pdf).)
Execution-order:
1. Generate evidences: ge.py
2. Prepare evidences: pe.py
3. Merge evidences: me.py
4. Characteristic evidences: ce.py

ge.py starts the desired actions in a virtual machine to generate evidences. Furthermore an other vm will be used to calculate the difference in the file-system with [idifference2](https://github.com/simsong/dfxml/blob/master/python/idifference2.py). This process will be looped and takes some time.
Then the other scripts will be executed to analyse the idiff-files, extract/merge the evidences and calculates the characteristic evidences.
This scripts will only analyse which files the desired action created/changes/deletes on the filesystem. This scripts does neither analyse the content of these files nor analyse any other possible evidences of the desired action.
You can easily open, edit and debug this project in Visual Studio Community Edition for example.
To execute this script correctly you need:
- Oracle VirtualBox
- A vm which contains idifference2
- A vm where the desired action(s) can be executed
- Much time
- Much disk space

## Getting started

1. Prepare the vm which contains the os where you want to execute the program/action. This vm is called vm_to_analyse. vm_to_analyse should be suspended initially.
2. Prepare the vm which contains idifference2. This vm is called vm_which_has_idifference. vm_which_has_idifference should be shut down initially.
3. Adjust the paths and names in FileDifferenceForensicEvidence/shared_utilities.py
4. Run "start.py"

## Licence
This project is licenced under the terms of LGPL. This software comes with absolutely no warranty. We do not take over any liability for bugs and flaws. You are not allowed to use the content of this repository if you do not agree to these terms.
If you like this project and it has helped you, please send me a cookie. I would be glad.

## Hints
The scripts are tested with VirtualBox 6.0.4.r128413. For some functions the console-output of vboxmanage will be parsed. So if you use a VirtualBox-version where the console-output of vboxmanage looks different then this scripts may not work correctly.
