In this repository scripts should be created which allow to automatically determine characteristical evidences (the characteristical changes in the filesystem) which a (arbitrary) program p produces.
Execution-order:
1. Generate evidence: ge.py
2. Prepare evidence: pe.py
3. Merge evidence: me.py
4. Characteristic evidence: ce.py

ge.py uses the VMWare virtual machines and VBoxManage.exe to execute p in a given vm. Furthermore an other vm will be used to calculate the difference in the file-system with [idifference2](https://github.com/simsong/dfxml/blob/master/python/idifference2.py). This process will be looped and takes some time.
Then the other scripts will be executed to analyse the idiff-files, extract/merge the evidences and calculates the characteristic evidences.