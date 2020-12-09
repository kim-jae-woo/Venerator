#!/usr/bin/env python3.8

import sys
import os
import glob     #file serch library
import shutil
import json
import re

from munch import munchify
from datetime import datetime

###################################
# Path Configulation
###################################

modulePath = "./../config/module/"
outputPath = "./build/"

###################################
# get file list
###################################

moduleList = []
regConfiguList = []

moduleList = os.listdir(modulePath)
print("Configuration Files List {}\n".format(moduleList))

###################################
# Generate description
###################################

def genDes(f, jsonMunch):
    ctime = datetime.now().strftime("%Y%m%d")
    f.write("/*********************************************************\n")
    f.write("\n")
    f.write("   Company     : {}\n".format(jsonMunch.company))
    f.write("\n")
    f.write("   Project     : {}\n".format(jsonMunch.project))
    f.write("\n")
    f.write("   Module      : {}.{}\n".format(jsonMunch.name, jsonMunch.extension))
    f.write("\n")
    f.write("   Designer    : {}\n".format(jsonMunch.designer))
    f.write("\n")
    f.write("   E-mail      : {}\n".format(jsonMunch.email))
    f.write("\n")
    f.write("   Date        : %s\n" %ctime)
    f.write("\n")
    f.write("   Description : {}\n\n".format(jsonMunch.description))
    f.write("*********************************************************/\n")

###################################
# Generate define
###################################

def genDefine(f, jsonMunch):
    f.write("\n")
    for define in jsonMunch.defines:
        f.write("{}\n".format(define.content))
    f.write("\n")

###################################
# Generate Clock
###################################

def genClock(f, jsonMunch):
    f.write(jsonMunch.keyword+' '+jsonMunch.name+'(')
    if jsonMunch.sort == "tb":
        f.write(");\n\n")
        f.write("//==========================================\n")
        f.write("// Get Clock\n")
        f.write("//==========================================\n")
        f.write("\n")
        for clk in jsonMunch.clocks:
            f.write("\talways (#1/{})\t{} = ~{};\n".format(clk.period, clk.name, clk.name))
    else:
        f.write("\n")
        for clk in jsonMunch.clocks:
            if clk.bit == "1":
                f.write("\t{}\t\t\t\t\t{},\n".format(clk.dir, clk.name))
            else:
                f.write("\t{}\t\t[{}:0]\t\t{},\n".format(clk.dir, int(clk.bit)-1, clk.name))

###################################
# Generate Reset
###################################

def genReset(f, jsonMunch):
    f.write("\n")
    if jsonMunch.sort == "tb":
        f.write("//==========================================\n")
        f.write("// Get Reset\n")
        f.write("//==========================================\n")
        f.write("\n")
        for rst in jsonMunch.resets:
            f.write("\tinitial begin\n")
            if rst.type == 'high':
                f.write("\t\t{} = 1;\n".format(rst.name))
                f.write("\t\t#{}\n\t\t{} = 0;\n".format(rst.time, rst.name))
            else:
                f.write("\t\t{} = 0;\n".format(rst.name))
                f.write("\t\t#{}\n\t\t{} = 1;\n".format(rst.time, rst.name))
            f.write("\tend\n")
    else:
        for rst in jsonMunch.resets:
            if rst.bit == "1":
                f.write("\t{}\t\t\t\t\t{},\n".format(rst.dir, rst.name))
            else:
                f.write("\t{}\t[{}:0]\t\t\t{},\n".format(int(rst.dir, rst.bit)-1, rst.name))

###################################
# Generate Port
###################################

def genPort(f, jsonMunch, portList, portRegList):
    f.write("\n")
    if jsonMunch.sort != "tb":
        idx = 0
        for port in portList:
            if port.bit == "1":
                if port.reg == "true" and port.dir == "output":
                    f.write("\t{}\treg\t\t\t\t{}".format(port.dir, port.name))
                else:
                    f.write("\t{}\t\t\t\t\t{}".format(port.dir, port.name))
            else:
                if port.reg == "true" and port.dir == "output":
                    f.write("\t{}\treg\t[{}:0]\t\t{}".format(port.dir, int(port.bit)-1, port.name))
                else:
                    f.write("\t{}\t\t[{}:0]\t\t{}".format(port.dir, int(port.bit)-1, port.name))
            if idx == len(portList) - 1:
                if len(portRegList) == 0:
                    f.write("\n\n")
                else:
                    f.write(",\n\n")
            else:
                f.write(",\n")
            idx = idx + 1

        idx = 0
        for reg in portRegList:
            if idx == len(portRegList) - 1 :
                f.write("\toutput\treg\t{}\t\t{}\n".format(reg.bitfiled, reg.name))
            else:
                f.write("\toutput\treg\t{}\t\t{},\n".format(reg.bitfiled, reg.name))
        f.write(");\n")

###################################
# Generate parameter
###################################

def genParam(f, jsonMunch):
    f.write("//==========================================\n")
    f.write("// Parameters\n")
    f.write("//==========================================\n\n")
    for param in jsonMunch.parameters:
        if param.name == "":
            continue
        else:
            f.write("\tlocalparam {} = {};\n".format(param.name, param.value))

###################################
# Generate signals
###################################

def genSignal(f, jsonMunch, regList):
    f.write("\n")
    f.write("//==========================================\n")
    f.write("// Signals\n")
    f.write("//==========================================\n\n")
    for signal in jsonMunch.signals:
        if signal.name == "":
            continue
        else:
            if signal.bit == "1":
                f.write("\t{}\t\t\t\t\t\t{};\n".format(signal.type, signal.name))
            else:
                f.write("\t{}\t\t[{}:0]\t\t{};\n".format(signal.type, int(signal.bit)-1, signal.name))

    f.write("\n")
    for reg in regList:
        f.write("\treg\t\t{}\t\t{};\n".format(reg.bitfiled, reg.name))
    f.write("\n")

###################################
# Generate force
###################################

def genForce(f, jsonMunch):
    if jsonMunch.forces != "":
        f.write("\n")
        f.write("//==========================================\n")
        f.write("// Forces\n")
        f.write("//==========================================\n\n")
        for force in jsonMunch.forces:
            if force.path != "":
                f.write("\tinitial #{} force {} = {};\n".format(force.time, force.path, force.value))

###################################
# Generate Registers
###################################

def genReg(f, module, jsonMunch):
    if module.regconfig != "":
        f.write("//==========================================\n")
        f.write("// Registers\n")
        f.write("//==========================================\n")
        for reg in jsonMunch.registers:
            if jsonMunch.active == "high":
                f.write("\n\talways @(posedge {} or posedge {})\n".format(jsonMunch.clock, jsonMunch.reset))
                f.write("\t\tif({})\n".format(jsonMunch.reset))
                f.write("\t\t\t{} <= {};\n".format(reg.name, reg.default))
                f.write("\t\telse if(apb_wr && paddr == {})\n".format(reg.offset))
                f.write("\t\t\t{} <= PWDATA{};\n".format(reg.name, reg.bitfiled))
            else:
                f.write("\n\talways @(posedge {} or negedge {})\n".format(jsonMunch.clock, jsonMunch.reset))
                f.write("\t\tif(!{})\n".format(jsonMunch.reset))
                f.write("\t\t\t{} <= {};\n".format(reg.name, reg.default))
                f.write("\t\telse if(apb_wr && paddr == {})\n".format(reg.offset))
                f.write("\t\t\t{} <= PWDATA{};\n".format(reg.name, reg.bitfiled))

###################################
# Generate wave dump
###################################

def genWave(f, jsonMunch):
    for wave in jsonMunch.waves:
        if wave.tool =="":
            continue
        elif wave.tool == "vcs":
            f.write("\n")
            f.write("//==========================================\n")
            f.write("// Dump\n")
            f.write("//==========================================\n\n")
            f.write("\tinitial begin\n")
            f.write("\t\t$fsdbDumpfile('"'{}.fsdb'"');\n".format(jsonMunch.name))
            f.write("\t\t$fsdbDumpvars;\n")
            f.write("\tend\n")
        elif wave.tool == "nc":
            f.write("\n")
            f.write("//==========================================\n")
            f.write("// Dump\n")
            f.write("//==========================================\n\n")
            f.write("\tinitial begin\n")
            f.write("\t\t$shm_open('"'{}.shm'"');\n".format(jsonMunch.name))
            f.write("\t\t$shm_probe({},{});\n".format(jsonMunch.name, wave.option))
            f.write("\tend\n")

###################################
# get file list
###################################

for modules in moduleList:
    if modulePath+modules == "":
        continue
    else:
        with open(modulePath+modules) as f:
            moduleMunch = munchify(json.load(f))
        print("Generating "+modulePath+modules)

        portList = []
        for port in moduleMunch.ports:
            portList.append(port)

        if moduleMunch.regconfig != "":
            print("Generating register "+ moduleMunch.regconfig)
            with open(moduleMunch.regconfig) as regf:
                portRegisterList = []
                registerList = []
                regMunch = munchify(json.load(regf))
                for reg in regMunch.registers:
                    if reg.output == "yes":
                        portRegisterList.append(reg)
                    else:
                        registerList.append(reg)

    genf=open(outputPath+moduleMunch.name+'.'+moduleMunch.extension, 'w')
    genDes(genf, moduleMunch)
    genDefine(genf, moduleMunch)
    genClock(genf, moduleMunch)
    genReset(genf, moduleMunch)
    genPort(genf, moduleMunch, portList, portRegisterList)
    genParam(genf, moduleMunch)
    genSignal(genf, moduleMunch, registerList)
    genReg(genf, moduleMunch, regMunch)
    genForce(genf, moduleMunch)
    genWave(genf, moduleMunch)
    genf.write("\nend{}\n".format(moduleMunch.keyword))

    del portList[:]
    del portRegisterList[:]
    del registerList[:]

    regf.close()
    genf.close()
    f.close()

