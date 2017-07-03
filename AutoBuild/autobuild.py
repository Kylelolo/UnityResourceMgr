#! usr/bin/python #coding=utf-8

'''
自动化打包脚本
'''

import os, sys, platform
import  configfile
import  tail
import  subprocess

#######全局变量

#输入的APK版本号
global ApkVersion
ApkVersion = "2.0.0.0"
#基础资源版本号
global BaseResVersion
BaseResVersion = "1.0.0.0"
#增量资源版本号
global AppendResVersion
AppendResVersion = "1.0.0.0"
#输入平台：0-Windows 1-Android 2-IOS
global BuildPlatform
BuildPlatform = -1
##############

def CheckVersionFormat(version):
    return True

def UserInputVersion():

    global BuildPlatform
    global BaseResVersion
    global AppendResVersion


    while True:
        s = raw_input("请输入打包平台(0-Windows 1-Android 2-IOS)：")
        if (s.isdigit()):
            BuildPlatform = int(s)
            if BuildPlatform in [0, 1, 2]:
                if (IsWindowsPlatform() and (BuildPlatform == 2)):
                    print "Windows平台无法打包IOS"
                else:
                    break

    '''
    while True:
        ApkVersion = raw_input("请输入APK版本号(格式：2.x.x.x)：")
        if CheckVersionFormat(ApkVersion):
            break
    '''
    while True:
        BaseResVersion = raw_input("请输入基础资源版本号(格式：1.x.x.x)：")
        if CheckVersionFormat(BaseResVersion):
            break
    '''
    while True:
        AppendResVersion = raw_input("请输入增量资源版本号(格式：1.x.x.x)：")
        if CheckVersionFormat(AppendResVersion):
            break
    '''
    return

def SaveVersionInfo():
    return

def LoadVersionInfo():

    global BaseResVersion
    global AppendResVersion

    fileName = "%s/buildVersion.cfg" % GetUnityOrgProjPath()
    if (not os.path.exists(fileName)) or (not os.path.isfile(fileName)):
        return
    file = open(fileName, "r");
    if file == None:
        return
    version = file.readline()
    BaseResVersion = version
    AppendResVersion = version

    print "当前资源版本: %s \n" % version
    return

def GetUnityOrgProjPath():
    result = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    return result

def GetUnityProjPath():
    result = GetUnityOrgProjPath() + "/outPath/Proj"
    return result

def IsWindowsPlatform():
    return "Windows" in platform.system()

def IsMacPlatform():
    return "Darwin" in platform.system()

def MonitorLine(txt):
    print txt

def UnityBuildABProj():

    global BuildPlatform

    logFile = "%s/autobuild.txt" % GetUnityProjPath();
    f = open(logFile, "w")
    f.close()

    montior = tail.Tail(logFile)
    montior.register_callback(MonitorLine)

    projPath = GetUnityProjPath()
    if (not os.path.exists(projPath)) or (not os.path.isdir(projPath)):
        if IsMacPlatform():
            cmd = "/Applications/Unity/Unity.app/Contents/MacOS/Unity"
            if not os.path.exists(cmd):
                print "\n未安装Unity, 请下载Unity!!!"
                return False
            print "正在创建工程..."
            cmd = "%s -quit -batchmode -nographics -createProject %s -logFile %s" % (cmd, projPath, logFile)
            process = subprocess.Popen(cmd, shell=True)
            montior.follow(process, 2)
        elif IsWindowsPlatform():
            print "正在创建工程..."
            cmd = "Unity.exe -quit -batchmode -nographics -createProject %s -logFile %s" % (projPath, logFile)
            process = subprocess.Popen(cmd, shell=True)
            montior.follow(process, 2)
        else:
            print "不支持此平台打包"
            return False


    cmd = ""
    if IsMacPlatform():
        cmd = "/Applications/Unity/Unity.app/Contents/MacOS/Unity -quit -batchmode -nographics -projectPath %s -executeMethod %s -logFile " + logFile
    elif IsWindowsPlatform():
        cmd = "Unity.exe -quit -batchmode -nographics -projectPath %s -executeMethod %s -logFile " + logFile
    else:
        print "不支持此平台打包"
        return False

    if not BuildPlatform in [0, 1, 2]:
        return False

    copyCmd = cmd % (GetUnityOrgProjPath(), "AssetBundleBuild.Cmd_Build_Copy")
    print "正在拷贝文件..."

    process = subprocess.Popen(copyCmd, shell=True)
    montior.follow(process, 2)

    func = ""
    if BuildPlatform == 1:
        func = "AssetBundleBuild.Cmd_Build_Android_ABLz4_Append"
    elif BuildPlatform == 2:
        func = "AssetBundleBuild.OnAppendBuildPlatformIOSLz4Md5"
    elif BuildPlatform == 0:
        func = "AssetBundleBuild.Cmd_BuildWin32_Lz4"
    else:
        return False

    cmd = cmd % (GetUnityOrgProjPath(), func)
   # print cmd
    print "开始生成AssetBundle..."

    process = subprocess.Popen(cmd, shell=True)
    montior.follow(process, 2)

    return True

def UnityAndroidProjToApk():
    projPath = GetUnityProjPath()
    # OnAppendBuildPlatformAndroidLz4Md5
    return True

def UnityIOSProjToIPA():
    return

def UnityToExe():
    projPath = GetUnityOrgProjPath()
    if (not os.path.exists(projPath)) or (not os.path.isdir(projPath)):
        print "项目为空"
        return False
    if IsMacPlatform():
        cmd = "/Applications/Unity/Unity.app/Contents/MacOS/Unity"
        if not os.path.exists(cmd):
            print "\n未安装Unity, 请下载Unity!!!"
            return False
        os.system("%s -quit -batchmode -nographics -projectPath %s -executeMethod AssetBundleBuild.Cmd_Win" % (cmd, projPath))
    elif IsWindowsPlatform():
        os.system("Unity.exe -quit -batchmode -nographics -projectPath %s -executeMethod AssetBundleBuild.Cmd_Win" % projPath)
    return True

# 主函数
def Main():

    global BuildPlatform

    if (IsWindowsPlatform()):
        print "打包前请确认设置好Unity.exe环境变量"

    LoadVersionInfo()
    UserInputVersion()
    SaveVersionInfo()
    # Windows平台直接生成EXE
    if BuildPlatform == 0:
        UnityToExe()
    else:
        UnityBuildABProj()
        if BuildPlatform == 1:
            UnityAndroidProjToApk()
        elif BuildPlatform == 2:
            UnityIOSProjToIPA()
    return

##################################### 调用入口 ###################################
if __name__ == '__main__':
    Main()
#################################################################################
