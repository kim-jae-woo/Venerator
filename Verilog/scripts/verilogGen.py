#!/usr/bin/env python3.8

## type         : module, TB
## reset type	: P/N
## bus type     : AHB/APB

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

config_path = "./../config/module/"
reg_path = "./../config/reg/"
output_path = "./build/"

###################################
# get file list
###################################

cfg_list = []
cfg_list = os.listdir(config_path)
print("Configuration Files List {}\n".format(cfg_list))

regList = []
regList = os.listdir(reg_path)
print("Register Files List {}\n".format(regList))

###################################
# Generate description
###################################

def genDes():
    ctime = datetime.now().strftime("%Y%m%d")
    f.write("/*********************************************************\n")
    f.write("\n")
    f.write("   Company     : {}\n".format(cfg.company))
    f.write("\n")
    f.write("   Project     : {}\n".format(cfg.project))
    f.write("\n")
    f.write("   Module      : {}.{}\n".format(cfg.name, cfg.extension))
    f.write("\n")
    f.write("   Designer    : {}\n".format(cfg.designer))
    f.write("\n")
    f.write("   E-mail      : {}\n".format(cfg.email))
    f.write("\n")
    f.write("   Date        : %s\n" %ctime)
    f.write("\n")
    f.write("   Description : {}\n\n".format(cfg.description))
    f.write("*********************************************************/\n")

###################################
# Generate define
###################################

def genDefine():
    f.write("\n")
    for define in cfg.defines:
        f.write("{}\n".format(define.content))
    f.write("\n")

###################################
# Generate Clock
###################################

def genClock():
    f.write("\n")
    if cfg.sort == "tb":
        f.write("//==========================================\n")
        f.write("// Get Clock\n")
        f.write("//==========================================\n")
        f.write("\n")
        for clk in cfg.clocks:
            f.write("\talways (#1/{})\t{} = ~{};\n".format(clk.period, clk.name, clk.name))
    else:
        for clk in cfg.clocks:
            if clk.bit == "1":
                f.write("\t{}\t\t\t\t\t{},\n".format(clk.dir, clk.name))
            else:
                f.write("\t{}\t\t[{}:0]\t\t{},\n".format(clk.dir, int(clk.bit)-1, clk.name))

def genRegClockReset():
    f.write("\n")
    for regLists in regList:
        regName = "{}{}".format(reg_path, regLists)
        with open(regName) as ff:
            regs = munchify(json.load(ff))
            if not ff:
                print("Configulation Files didn't exsist\n")
                continue
            else:
                f.write("\tinput\t\t\t\t\t{},\n".format(regs.clock))
                f.write("\tinput\t\t\t\t\t{},\n".format(regs.reset))

###################################
# Generate Reset
###################################

def genReset():
    f.write("\n")
    if cfg.sort == "tb":
        f.write("//==========================================\n")
        f.write("// Get Reset\n")
        f.write("//==========================================\n")
        f.write("\n")
        for rst in cfg.resets:
            f.write("\tinitial begin\n")
            if rst.type == 'high':
                f.write("\t\t{} = 1;\n".format(rst.name))
                f.write("\t\t#{}\n\t{} = 0;\n".format(rst.time, rst.name))
            else:
                f.write("\t\t{} = 0;\n".format(rst.name))
                f.write("\t\t#{}\n\t{} = 1;\n".format(rst.time, rst.name))
            f.write("\tend\n\n")
    else:
        for rst in cfg.resets:
            if rst.bit == "1":
                f.write("\t{}\t\t\t\t\t{},\n".format(rst.dir, rst.name))
            else:
                f.write("\t{}\t[{}:0]\t\t\t{},\n".format(int(rst.dir, rst.bit)-1, rst.name))

def genRegReset():
    f.write("\n")
    for regLists in regList:
        regName = "{}{}".format(reg_path, regLists)
        with open(regName) as ff:
            regs = munchify(json.load(ff))
            if not ff:
                print("Configulation Files didn't exsist\n")
                continue
            else:
                f.write("\tinput\t\t\t\t\t{},\n".format(regs.reset))
###################################
# Generate AHB
###################################

def genAHB():
    for ahb in cfg.AHBs:
        f.write("\n")
        if ahb.type == "":
            continue
        elif ahb.type == "master":
            f.write("\tinput\t\t\t\t\thready{},\n".format(ahb.name))
            f.write("\tinput\t\t\t\t\thresp{},\n".format(ahb.name))
            f.write("\tinput\t\t[{}:0]\t\thrdata{},\n".format(int(ahb.data)-1, ahb.name))
            f.write("\toutput\t{}\t\t\t\thsel{},\n".format(ahb.hsel, ahb.name))
            f.write("\toutput\t{}\t[{}:0]\t\thaddr{},\n".format(ahb.haddr, int(ahb.address)-1, ahb.name))
            f.write("\toutput\t{}\t\t\t\thwrite{},\n".format(ahb.hwrite, ahb.name))
            f.write("\toutput\t{}\t[2:0]\t\thsize{},\n".format(ahb.hsize, ahb.name))
            f.write("\toutput\t{}\t[2:0]\t\thburst{},\n".format(ahb.hburst, ahb.name))
            f.write("\toutput\t{}\t[3:0]\t\thprot{},\n".format(ahb.hprot, ahb.name))
            f.write("\toutput\t{}\t[1:0]\t\thtrans{},\n".format(ahb.htrans, ahb.name))
            f.write("\toutput\t{}\t\t\t\thmastlock{},\n".format(ahb.hmastlock, ahb.name))
            f.write("\toutput\t{}\t[{}:0]\t\thwdata{},\n".format(ahb.hwdata, int(ahb.data)-1, ahb.name))
        else:
            f.write("\tinput\t\t\t\t\thsel{},\n".format(ahb.name))
            f.write("\tinput\t\t[{}:0]\t\thaddr{},\n".format(int(ahb.address)-1, ahb.name))
            f.write("\tinput\t\t\t\t\thwrite{},\n".format(ahb.name))
            f.write("\tinput\t\t[2:0]\t\thsize{},\n".format(ahb.name))
            f.write("\tinput\t\t[2:0]\t\thburst{},\n".format(ahb.name))
            f.write("\tinput\t\t[3:0]\t\thprot{},\n".format(ahb.name))
            f.write("\tinput\t\t[1:0]\t\thtrans{},\n".format(ahb.name))
            f.write("\tinput\t\t\t\t\thmastlock{},\n".format(ahb.name))
            f.write("\tinput\t\t\t\t\thready{},\n".format(ahb.name))
            f.write("\tinput\t\t[{}:0]\t\thwdata{},\n".format(int(ahb.data)-1, ahb.name))
            f.write("\toutput\t{}\t\t\t\threadyout{},\n".format(ahb.hreadyout, ahb.name))
            f.write("\toutput\t{}\t[{}:0]\t\thrdata{},\n".format(ahb.hrdata, int(ahb.data)-1, ahb.name))
            f.write("\toutput\t{}\t\t\t\thresp{},\n".format(ahb.hresp, ahb.name))

###################################
# Generate APB
###################################

def genAPB():
    for apb in cfg.APBs:
        f.write("\n")
        if apb.type == "":
            continue
        elif apb.type == "master":
            f.write("\toutput\t{}\t\t\t\tpsel{},\n".format(apb.psel, apb.name))
            f.write("\toutput\t{}\t\t\t\tpenalbe{},\n".format(apb.penable, apb.name))
            f.write("\toutput\t{}\t\t\t\tpwrite{},\n".format(apb.pwrite, apb.name))
            if apb.version == "4":
                f.write("\toutput\t{}\t[3:0]\t\tpstrb{},\n".format(apb.pstrb, apb.name))
            f.write("\toutput\t{}\t[{}:0]\t\tpaddr{},\n".format(apb.paddr, int(apb.address) - 1, apb.name))
            f.write("\toutput\t{}\t[31:0]\t\tpwdata{},\n".format(apb.pwdata, apb.name))
            f.write("\tinput\t\t[31:0]\t\tprdata{},\n".format(apb.name))
            f.write("\tinput\t\t\t\t\tpready{},\n".format(apb.name))
            f.write("\tinput\t\t\t\t\tpslverr{},\n".format(apb.name))
        else:
            f.write("\tinput\t\t\t\t\tpsel{},\n".format(apb.name))
            f.write("\tinput\t\t\t\t\tpenalbe{},\n".format(apb.name))
            f.write("\tinput\t\t\t\t\tpwrite{},\n".format(apb.name))
            if apb.version == "4":
                f.write("\tinput\t\t[3:0]\t\tpstrb{},\n".format(apb.name))
            f.write("\tinput\t\t[{}:0]\t\tpaddr{},\n".format(int(apb.address)-1, apb.name))
            f.write("\tinput\t\t[31:0]\t\tpwdata{},\n".format(apb.name))
            f.write("\toutput\t{}\t[31:0]\t\tprdata{},\n".format(apb.prdata, apb.name))
            f.write("\toutput\t{}\t\t\t\tpready{},\n".format(apb.pready, apb.name))
            f.write("\toutput\t{}\t\t\t\tpslverr{},\n".format(apb.pslverr, apb.name))

###################################
# Generate Port
###################################

def genPort():
    f.write("\n")
    for port in cfg.ports:
        if port.last == "yes":
            if port.bit == "1":
                if port.reg == "true" and port.dir == "output":
                    f.write("\t{}\treg\t\t\t\t{}\n".format(port.dir, port.name))
                else:
                    f.write("\t{}\t\t\t\t\t{}\n".format(port.dir, port.name))
            else:
                if port.reg == "true" and port.dir == "output":
                    f.write("\t{}\treg\t[{}:0]\t\t{}\n".format(port.dir, int(port.bit)-1, port.name))
                else:
                    f.write("\t{}\t\t[{}:0]\t\t{}\n".format(port.dir, int(port.bit)-1, port.name))
        else:
            if port.bit == "1":
                if port.reg == "true" and port.dir == "output":
                    f.write("\t{}\treg\t\t\t\t{},\n".format(port.dir, port.name))
                else:
                    f.write("\t{}\t\t\t\t\t{},\n".format(port.dir, port.name))
            else:
                if port.reg == "true" and port.dir == "output":
                    f.write("\t{}\treg\t[{}:0]\t\t{},\n".format(port.dir, int(port.bit)-1, port.name))
                else:
                    f.write("\t{}\t\t[{}:0]\t\t{},\n".format(port.dir, int(port.bit)-1, port.name))

def genRegPort():
    f.write("\n")
    for regLists in regList:
        regName = "{}{}".format(reg_path, regLists)
        with open(regName) as ff:
            regs = munchify(json.load(ff))
            if not ff:
                print("Configulation Files didn't exsist\n")
                continue
            else:
                for reg in regs.registers:
                    if reg.output == "yes":
                        f.write("\toutput\treg\t{}\t\t{},\n".format(reg.bitfiled, reg.name))
                    else:
                        continue

###################################
# Generate parameter
###################################

def genParam():
    f.write("\n")
    f.write("//==========================================\n")
    f.write("// Parameters\n")
    f.write("//==========================================\n\n")
    for param in cfg.parameters:
        if param.name == "":
            continue
        else:
            f.write("\tlocalparam {} = {};\n".format(param.name, param.value))

###################################
# Generate signals
###################################

def genSignals():
    f.write("\n")
    f.write("//==========================================\n")
    f.write("// Signals\n")
    f.write("//==========================================\n\n")
    for signal in cfg.signals:
        if signal.name == "":
            continue
        else:
            if signal.bit == "1":
                f.write("\t{}\t\t\t\t\t{};\n".format(signal.type, signal.name))
            else:
                f.write("\t{}\t[{}:0]\t\t{};\n".format(signal.type, int(signal.bit)-1, signal.name))

def genRegSignals():
    for regLists in regList:
        regName = "{}{}".format(reg_path, regLists)
        with open(regName) as ff:
            regs = munchify(json.load(ff))
            if not ff:
                print("Configulation Files didn't exsist\n")
                continue
            else:
                for reg in regs.registers:
                    if reg.output == "no":
                        f.write("\treg\t{}\t\t{};\n".format(reg.bitfiled, reg.name))
                    else:
                        continue
###################################
# Generate force
###################################

def genForce():
    f.write("\n")
    f.write("//==========================================\n")
    f.write("// Forces\n")
    f.write("//==========================================\n\n")
    for force in cfg.forces:
        if force.path == "":
            continue
        else:
            f.write("\tinitial force {} = {};\n".format(force.path, force.value))

###################################
# Generate Registers
###################################

def genReg():
    f.write("//==========================================\n")
    f.write("// Registers\n")
    f.write("//==========================================\n")
    for regLists in regList:
        regName = "{}{}".format(reg_path, regLists)
        with open(regName) as ff:
            regs = munchify(json.load(ff))
            if not ff:
                print("Configulation Files didn't exsist\n")
                continue
            else:
                for reg in regs.registers:
                    if regs.active == "high":
                        f.write("\n\talways @(posedge {} or posedge {})\n".format(regs.clock, regs.reset))
                        f.write("\t\tif({})\n".format(regs.reset))
                        f.write("\t\t\t{} <= {};\n".format(reg.name, reg.default))
                        f.write("\t\telse if(apb_wr && paddr == {})\n".format(reg.offset))
                        f.write("\t\t\t{} <= PWDATA{};\n".format(reg.name, reg.bitfiled))
                    else:
                        f.write("\n\talways @(posedge {} or negedge {})\n".format(regs.clock, regs.reset))
                        f.write("\t\tif(!{})\n".format(regs.reset))
                        f.write("\t\t\t{} <= {};\n".format(reg.name, reg.default))
                        f.write("\t\telse if(apb_wr && paddr == {})\n".format(reg.offset))
                        f.write("\t\t\t{} <= PWDATA{};\n".format(reg.name, reg.bitfiled))

###################################
# Generate submodule
###################################

def genSub():
    for sub in cfg.submodules:
        f_sub = open(sub.path, 'r')
        while True:
            sub_str = f_sub.readline()
            if sub_str.find(');') >= 0:
                if sub_str.find('input') >= 0 or sub_str.find('output') >= 0 or sub_str.find('inout') >= 0:
                    sub_str = re.sub('(\s[a-z])\s', '', sub_str)
                break
            elif sub_str.find('module') >= 0:
                print(sub_str)
            elif sub_str.find('input') >= 0 or sub_str.find('output') >= 0 or sub_str.find('inout') >= 0:
                sub_str = re.sub('input', '', sub_str)
                print(sub_str.lstrip('\d*'))
        f_sub.close()

###################################
# Generate wave dump
###################################

def genDump():
    for wave in cfg.waves:
        if wave.tool =="":
            continue
        elif wave.tool == "vcs":
            f.write("\n")
            f.write("//==========================================\n")
            f.write("// Dump\n")
            f.write("//==========================================\n\n")
            f.write("\tinitial begin\n")
            f.write("\t\t$fsdbDumpfile('"'{}.fsdb'"');\n".format(cfg.name))
            f.write("\t\t$fsdbDumpvars;\n")
            f.write("\tend\n")
        elif wave.tool == "nc":
            f.write("\n")
            f.write("//==========================================\n")
            f.write("// Dump\n")
            f.write("//==========================================\n\n")
            f.write("\tinitial begin\n")
            f.write("\t\t$shm_open('"'{}.shm'"');\n".format(cfg.name))
            f.write("\t\t$shm_probe({},{});\n".format(cfg.name, wave.option))
            f.write("\tend\n")

###################################
# Parameters from json
###################################

for clist in cfg_list:
    with open(config_path+clist) as f:
        cfg = munchify(json.load(f))

    if not f:
        print("Configulation Files didn't exsist\n")
        break
    else:
        f=open(output_path+cfg.name+'.'+cfg.extension, 'w')
        genDes()
        genDefine()
        f.write(cfg.keyword+' '+cfg.name+'(')
        if cfg.sort == "tb":
            f.write(");\n")
            genClock()
            genParam()
            genSignals()
            #genSub()
            genForce()
            genDump()
            f.write("\nend{}\n".format(cfg.keyword))
        elif cfg.sort == "blackbox":
            genClock()
            genReset()
            genAHB()
            genAPB()
            genPort()
            f.write(");\n")
            f.write("\nend{}\n".format(cfg.keyword))
        else:
            genClock()
            genReset()
            genRegClockReset()
            genAHB()
            genAPB()
            genRegPort()
            genPort()
            f.write(");\n")
            genParam()
            genSignals()
            genRegSignals()
            genReg()
            f.write("\nend{}\n".format(cfg.keyword))
f.close()
