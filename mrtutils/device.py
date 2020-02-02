#!/usr/bin/env python3
#
#@file device.py
#@brief device descripto
#@author Jason Berger
#@date 02/19/2019
#

import sys
import os
import yaml


sizeDict = {
    "uint8" : 1,
    "int8" : 1,
    "char" : 1,
    "uint16" : 2,
    "int16" : 2,
    "uint32" : 4,
    "int32" : 4,
    "int64" : 8,
    "uint64" : 8,
    "int" : 4,
    "string" : 16,
}

args = None
parser = None


class FieldVal:
    def __init__(self, node):
        self.field = 0
        self.val = 0 
        self.desc = ""

        self.name = list(node.keys())[0]
        valItem = list(node.values())[0]
        if 'val' in valItem:
            self.val = valItem['val']
        if 'desc' in valItem:
            self.desc = valItem['desc']
        if 'name' in valItem:
            self.desc = valItem['name']

 
class RegField:
    def __init__(self, node):
        self.reg = 0
        self.mask = 0XFFFFFFFF
        self.desc = ""
        self.vals = []
        self.isFlag = False

        self.name = list(node.keys())[0]
        fieldItem = list(node.values())[0]

        if 'mask' in fieldItem:
            self.mask = fieldItem['mask']
        if 'values' in fieldItem:
            for valNode in fieldItem['values']:
                newVal = FieldVal(valNode)
                self.addVal(newVal)
        if 'vals' in fieldItem:
            for valNode in fieldItem['vals']:
                newVal = FieldVal(valNode)
                self.addVal(newVal)
        if 'desc' in fieldItem:
            self.desc = fieldItem['desc']
        
        if self.getSize() == 1:
            self.isFlag = True

    def getSize(self):
        count = 0
        n = self.mask
        while (n): 
            count += n & 1
            n >>= 1
        return count 

    def offset(self):
        check = self.mask
        count = 0
        while not check & 1:
            check = check >> 1
            count+=1
    
        return count
    
    def addVal(self, fieldVal):
        fieldVal.field = self
        self.vals.append(fieldVal)

class DeviceReg:
    def __init__(self,name):
        self.name = name
        self.addr = 0
        self.type ="uint8_t"
        self.perm = "RW"
        self.desc = ""
        self.default = 0
        self.hasDefault = False
        self.fields = []
        self.flags = []
        self.size = 1
        self.device = 0
        self.hasFlags = False
        self.hasFields = False
    
    def addField(self, field):
        field.reg = self
        if field.isFlag:
            self.hasFlags = True
        else:
            self.hasFields = True
        self.fields.append(field)
    
    def formatHex(self, val):
        return self.device.formatHex(val, self.size)

    def printAddr(self):
        val = "{0:#0{1}X}".format(self.addr,(self.device.addrSize *2) + 2)
        val = val.replace("X","x")
        return val


class Device:
    def __init__(self, name):
        self.name = name
        self.prefix = ""
        self.bus = "I2C"
        self.i2c_addr = 0
        self.addrSize =1
        self.aiMask = 0 #auto incrment mask 
        self.regs = {}

    def addReg(self, reg):
        reg.device = self
        self.regs[reg.name] = reg

    def formatHex(self, val, size):
        val = "{0:#0{1}X}".format(val,(size *2) + 2)
        val = val.replace("X","x")
        return val

    def camelCase(self, text):
        out =""
        cap = True 
        for char in text:
            if char != '_':
                if cap:
                    out+= char.upper()
                else:
                    out+= char.lower()
                cap = False
            else:
                cap = True
            
        return out

    def parseYAML(self,yamlFile):
        data = open(yamlFile)
        objDevice = yaml.load(data , Loader=yaml.FullLoader)

        if 'name' in objDevice:
            self.name = objDevice['name']
        
        if 'prefix' in objDevice:
            self.prefix = objDevice['prefix']
        
        if 'bus' in objDevice:
            self.bus = objDevice['bus']
        
        if 'i2c_addr' in objDevice:
            self.i2c_addr = objDevice['i2c_addr']
        
        if 'ai_mask' in objDevice:
            self.aiMask = objDevice['ai_mask'] #int(objDecive['ai_mask'],0)
        
        if 'registers' in objDevice:
            for regNode in objDevice['registers']:
                newReg = DeviceReg(list(regNode.keys())[0])
                regItem = list(regNode.values())[0]

                if 'addr' in regItem:
                    newReg.addr = regItem['addr'] #int(regItem['addr'],0) 
                if 'type' in regItem:
                    newReg.type = regItem['type']
                    newReg.size = sizeDict[newReg.type.replace("_t","")]
                if 'size' in regItem:
                    newReg.size = regItem['size']
                if 'perm' in regItem:
                    newReg.perm = regItem['perm'].upper()
                if 'desc' in regItem:
                    newReg.desc = regItem['desc']
                if 'name' in regItem:
                    newReg.desc = regItem['name']
                if 'default' in regItem:
                    newReg.default = regItem['default']
                    newReg.hasDefault = True

                self.addReg(newReg)      
        
        if 'fields' in objDevice:
            for propNode in objDevice['fields']:
                regName = list(propNode.keys())[0]
                propItem = list(propNode.values())[0]
                if regName in self.regs:
                    curReg = self.regs[regName]  
                    for fieldNode in propItem:
                        newField = RegField(fieldNode)
                        curReg.addField(newField)

        print("Parsed device: " + self.name )
        print( "registers: " + str(len(self.regs)))




        



        