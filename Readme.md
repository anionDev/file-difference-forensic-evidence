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
-Oracle VirtualBox
-A vm which contains idifference2
-A vm where the desired action(s) can be executed
-Much time
-Much disk space
Before executing the scripts you must probably adjust the variables in the configuration (in scripts/Utilities.py).

If you like this project and it has helped you, please send me a cookie. I would be glad.
