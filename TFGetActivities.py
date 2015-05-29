#!/usr/bin/python

import os
import sys
import re
import time
import shutil
import codecs
from PyExcelerator import *

manifestPathTxt = "apkpackagelist.txt"

APK_ACTIVITY_PATH = "apkactivities.txt"
APK_ACTIVITY_EXCEL = 'apkactivities.xls'

pathDict = {}
pkg_list = []
class Package:
    def __init__(self):
        self.name = ''
        self.apkname = ''
        self.path = ''
        self.type = ''
        self.activies = []

def generatePackageInstallationToPathDict():
    f = open(manifestPathTxt, 'r')
    f2 = open("apkpath.txt", 'w')
    while True:
        line = f.readline()
        if not line:
            break
        if line.find('package:') > -1:
            list = line.split('=')
            idx1 = list[1].find('\r\n')
            package = list[1][:idx1]
            idx2 = list[0].find(':') + 1
            path = list[0][idx2:]
            pathDict[package] = path
            f2.write(path)
            f2.write('\n')

def getManifestPathFromPhone():
    command = "adb shell pm list packages -f "
    os.system("%s > %s" % (command, manifestPathTxt)) 

def pushApkPathToPhone():
    command = "adb push apkpath.txt /sdcard/"
    os.system("%s" % (command))

def installApkToPhone():
    command = "adb install -r TFGetActivities.apk"
    os.system("%s" % (command))

def startActivityToRun():
    command = "adb shell am start com.jrdcom.tfgetactivities/.MainActivity"
    os.system("%s" % (command))

def pullActivitesInfoFromPhone():
    command = "adb pull /sdcard/apkactivities.txt"
    os.system("%s" % (command))

def generatePackagesList():
    #change txt to packages list
    if os.path.isfile(APK_ACTIVITY_PATH):
        f = open(APK_ACTIVITY_PATH, 'r')
        pkg = None
        while True:
            line = f.readline()
            if not line:
                break
            if line.find('packageName:') > -1:
                if pkg:
                    pkg_list.append(pkg)
                    pkg = Package()
                else:
                    pkg = Package()

                list = line.split(':')
                pkg.name = list[1]
                pkg.path = list[3]
                pkg.type = getApkType(pkg.name)
                pkg.apkname = list[3][list[3].rfind('/')+1:]
            else:
                pkg.activies.append(line.strip('\n'));

def printToExcel():
     #change packages lsit to excel table
    _wb = Workbook()
    style = setStyles()
    _ws = _wb.add_sheet('APK Activies')

    _ws.write(0, 0, 'Android/OEM', style)
    _ws.write(0, 1, 'APKName', style)
    _ws.write(0, 2, 'PackageName', style)
    _ws.write(0, 3, 'Activity Name List', style)

    count = 1
    for pkg in pkg_list:
        i = count
        _ws.write(i, 0, pkg.type, style)
        _ws.write(i, 1, pkg.apkname, style)
        _ws.write(i, 2, pkg.name, style)

        for activity in pkg.activies:
            j = pkg.activies.index(activity)
            _ws.write(i+j, 3, activity, style)

        count += len(pkg.activies)

    _wb.save(APK_ACTIVITY_EXCEL)
    print "Generate xls table successed!! --> %s" % APK_ACTIVITY_EXCEL

def getApkType(pkg):
    type = ''
    if pkg == 'android':
        type = 'AOSP'
    if pkg.find('com.android') > -1:
        type = 'AOSP'
    elif pkg.find('com.tracfone') > -1:
        type = 'Tracfone'
    elif pkg.find('com.google') > -1:
        type = 'Google'
    else:
        type = 'OEM'

    return type

def setStyles():
    fnt = Font()
    # pt = Pattern()
    # pt.pattern_back_colour = 0x7F
    al = Alignment()
    al.horz = Alignment.HORZ_LEFT
    al.vert = Alignment.VERT_CENTER
    style = XFStyle()
    style.font = fnt
    style.alignment = al
    # style.pattern = pt
    return style

def main():
    getManifestPathFromPhone()
    generatePackageInstallationToPathDict()
    pushApkPathToPhone()
    installApkToPhone()
    startActivityToRun()
    time.sleep(10)
    pullActivitesInfoFromPhone()
    os.system("adb uninstall com.jrdcom.tfgetactivities") 
    os.system("adb shell rm /sdcard/apk*.txt") 
    generatePackagesList()
    printToExcel()

if __name__ == '__main__':
    main()