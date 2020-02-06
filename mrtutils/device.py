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

class DevConfig:
    def __init__(self, node):
        self.field = 0
        self.val = 0 
        self.desc = ""
        self.regVals = []

        self.name = list(node.keys())[0]
        configItem = list(node.values())[0]
        if 'desc' in configItem:
            self.desc = configItem['desc']
        
        if 'registers' in configItem:
            for regNode in configItem['registers']:
                self.regVals.append(regNode)
        if 'regs' in configItem:
            for regNode in configItem['regs']:
                self.regVals.append(regNode)
    
    def getDesc(self,regVal, spacing =0):
        ret =""
        regName = list(regVal.keys())[0]
        regItem = list(regVal.values())[0]
        if type(regItem) is dict:
            if 'desc' in regItem:
                return "/* "+regItem['desc']+" */"
            else:
                ret+="/*"
                for key,value in regItem.items():
                    ret+= " "+key+": "+ str(value) +" ,"
                ret+=",*/"
                ret = ret.replace(",,", "")
        else:
            ret=""

        spaces = spacing - len(ret)
        ret+= (" " * spaces)
        
        return ret


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

    def getFieldValMacro(self, spacing = 0):
        ret = self.field.reg.device.prefix.upper() +"_"+self.field.reg.name.upper()+"_"+self.field.name.upper() +"_" + self.name.upper()
        if spacing > 0:
            spaces = spacing - len(ret)
            ret = ret + (" " * spaces)
        return ret
    
    def getFieldValMaskMacro(self, spacing = 0):
        ret = self.field.reg.device.prefix.upper() +"_"+self.field.reg.name.upper()+"_"+self.field.name.upper() +"_" + self.name.upper() + "_MASK"
        if spacing > 0:
            spaces = spacing - len(ret)
            ret = ret + (" " * spaces)
        return ret
    
    def getOffSetValue(self):
        return val << self.field.offset
 
class RegField:
    def __init__(self, node):
        self.reg = 0
        self.mask = 0XFFFFFFFF
        self.desc = ""
        self.vals = []
        self.valDict = {}
        self.isFlag = False
        self.bitCount = 0
        self.startBit =0

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
        
        self.bitCount = self.getSize()
        self.offset = self.getOffset()
        self.startBit = self.bitCount + self.offset

    def getSize(self):
        count = 0
        n = self.mask
        while (n): 
            count += n & 1
            n >>= 1
        return count 

    def getOffset(self):
        check = self.mask
        count = 0
        while not check & 1:
            check = check >> 1
            count+=1
    
        return count
    
    def addVal(self, fieldVal):
        fieldVal.field = self
        self.vals.append(fieldVal)
        self.valDict[fieldVal.name] = fieldVal

    def getFieldMaskMacro(self, spacing = 0):
        ret = self.reg.device.prefix.upper() +"_"+self.reg.name.upper()+"_"+self.name.upper() +"_FIELD_MASK"

        if spacing > 0:
            spaces = spacing - len(ret)
            ret = ret + (" " * spaces)
        return ret
    
    def getFieldOffsetkMacro(self, spacing = 0):
        ret = self.reg.device.prefix.upper() +"_"+self.reg.name.upper()+"_"+self.name.upper() +"_FIELD_OFFSET"

        if spacing > 0:
            spaces = spacing - len(ret)
            ret = ret + (" " * spaces)
        return ret

    def getFieldFlagMacro(self, spacing = 0):
        ret = self.reg.device.prefix.upper() +"_"+ self.reg.name.upper()+"_"+self.name.upper()

        if spacing > 0:
            spaces = spacing - len(ret)
            ret = ret + (" " * spaces)
        return ret

    def getToolTip(self):
        message = ""

        for val in self.vals:
            if self.bitCount > 4 :
                message +="\n\tx" + format(val.val, '02x') +" = " + val.desc
            else:
                message +="\n\tb" + format(val.val, '0'+str(self.bitCount)+'b') +" = " + val.desc
        
        return self.desc, message

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
        self.fieldDict = {}
        self.flags = []
        self.size = 1
        self.device = 0
        self.hasFlags = False
        self.hasFields = False
        self.configs = {}
    
    def addField(self, field):
        field.reg = self
        if field.isFlag:
            self.hasFlags = True
        else:
            self.hasFields = True

        self.fieldDict[field.name] = field
        self.fields.append(field)
    
    def formatHex(self, val):
        return self.device.formatHex(val, self.size)

    def printAddr(self):
        val = "{0:#0{1}X}".format(self.addr,(self.device.addrSize *2) + 2)
        val = val.replace("X","x")
        return val
    
    def getNextfieldByStartBit(self, startBit):

        found = False
        for field in self.fields:
            if field.startBit == startBit:
                return field , field.bitCount
        
        search = startBit
        while search >= 0:
            search = search -1 
            for field in self.fields:
                if field.startBit == search:
                    return False , startBit - search
        
        return False, startBit

    
    
    def printFieldMap(self):
        ret =""
        i = self.size * 8
        # while i > 0:
        #     field , nextStart = self.getNextfieldByStartBit(i)
        #     if field:
        #         ret = ret+"<td class=\"field\" colspan=\""+str(field.bitCount)+"\">" +field.name+"</td>\n"
        #         i = i - field.bitCount
        #     else :
        #         ret = ret+"<td class=\"empty\" colspan=\""+ str(i - nextStart)+"\"></td>\n"
        #         i = nextStart
        
        return ret
    
    def printRegMap(self, width):
        ret =""
        lines = int(self.size * 8 / width)
        bit = self.size * 8
        fieldlen =0
        contlen =0
        remaining =0
        
        ret+="<tr>"
        ret+="<th rowspan=\""+ str(lines)+"\">"+self.name+"</th><th rowspan=\""+ str(lines)+"\">"+self.perm.upper()+"</th>\n"
        while bit > 0:
            contlen = 0
            field , fieldlen = self.getNextfieldByStartBit(bit)

            remaining = bit % width
            if remaining == 0:
                remaining = width
            if fieldlen >  remaining: #dont let it run over row
                contlen  =  fieldlen - remaining
                fieldlen -= contlen

            if field:
                tt_lbl , tt_msg = field.getToolTip()
                divField = "\n<div class=\"field\" style=\"margin-right:-"+ str(((fieldlen-1) * 100)) +"%\" >\n<a data-tt data-tt-lbl=\""+tt_lbl+"\" data-tt-msg=\""+tt_msg+"\">" +field.name+"</a></div>"
                ret += "\n<td id=\"" +self.name + "_bit_" + str(bit-1) +"\" class=\"bit first\" >"+ divField+"</td>"
                for b in range(1,fieldlen):
                    ret+= "<td id=\"" + self.name + "_bit_" + str(bit - (b+1))+"\" class=\"bit\"></td>"

                if contlen > 0:
                    divField = "<div class=\"field\" style=\"margin-right:-"+ str(((contlen-1) * 100)) +"%\" ><a data-tt data-tt-lbl=\""+tt_lbl+"\" data-tt-msg=\""+tt_msg+"\">" +field.name+"</a></div>"
                    ret += "\n<td id=\"" +self.name + "_bit_" + str(bit) +"\" class=\"bit first\" >"+ divField+"</td>"
                    for b in range(1,contlen):
                        ret+= "<td id=\"" + self.name + "_bit_" + str(bit - (fieldlen + b+1))+"\" class=\"bit\"></td>"
            else :
                ret += "<td class=\"empty\" colspan=\""+ str(fieldlen)+"\">.</td>"
                if contlen > 0:
                    ret += "</tr>\n<tr><td class=\"empty\" colspan=\""+ str(contlen )+"\">.</td>"
            
            bit -= (fieldlen + contlen)

            if( bit > 0) and (bit % width == 0):
                ret+="</tr>\n<tr>"
            elif bit == 0:
                ret+="</tr>\n"
        
        return ret
    
    def getAddrMacro(self, spacing = 0):
        ret = self.device.prefix.upper() +"_REG_"+self.name.upper()+"_ADDR"
        if spacing > 0:
            spaces = spacing - len(ret)
            ret = ret + (" " * spaces)
        return ret 
    
    def getDefaultMacro(self, spacing = 0):
        ret = self.device.prefix.upper() +"_"+self.name.upper()+"_DEFAULT"
        if spacing > 0:
            spaces = spacing - len(ret)
            ret = ret + (" " * spaces)
        return ret



class Device:
    def __init__(self, name):
        self.name = name
        self.prefix = ""
        self.bus = "I2C"
        self.i2c_addr = 0
        self.addrSize =1
        self.aiMask = 0 #auto incrment mask 
        self.regs = {}
        self.datasheet =""
        self.desc=""
        self.digikey_pn =""
        self.smallestReg = 4 
        self.configs = {}

    def addReg(self, reg):
        reg.device = self
        if reg.size < self.smallestReg:
            self.smallestReg = reg.size

        self.regs[reg.name] = reg
    
    def addConfig(self,config):
        self.configs[config.name] = config

    def getConfigLine(self,configReg,spacing =0, macro = False):
        ret = ""
        regName = list(configReg.keys())[0]
        regItem = list(configReg.values())[0]

        if regName in self.regs:
            curReg = self.regs[regName]
            if(macro):
                ret = self.prefix.lower() + "_write_reg( (dev), &(dev)->"
            else:
                ret = self.prefix.lower() + "_write_reg( dev, &dev->"
            ret+= "m"+ self.camelCase(regName) + ", "
            if type( regItem) is dict:
                val =0
                for key,value in regItem.items():
                    if key in curReg.fieldDict:
                        curField = curReg.fieldDict[key]
                        if type(value) is str:
                            if value in curField.valDict:
                                val = val | (curField.valDict[value].val << curField.offset) & curField.mask
                        else:
                            val = val | (value << curField.offset) & curField.mask
                
                ret+= self.formatHex(val, curReg.size)
            else: 
                ret+= self.formatHex(regItem, curReg.size)

            ret+=");"
        spaces = spacing - len(ret)
        ret+= (" "*spaces)
        return ret

    def getConfigRegVal(self,configReg):
        
        regName = list(configReg.keys())[0]
        regItem = list(configReg.values())[0]
        val = 0
        if regName in self.regs:
            curReg = self.regs[regName]
            if type( regItem) is dict:
                val =0
                for key,value in regItem.items():
                    if key in curReg.fieldDict:
                        curField = curReg.fieldDict[key]
                        if type(value) is str:
                            if value in curField.valDict:
                                val = val | (curField.valDict[value].val << curField.offset) & curField.mask
                        else:
                            val = val | (value << curField.offset) & curField.mask
                
            else: 
                val = regItem

        return regName, val
        

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
        
        if 'digikey_pn' in objDevice:
            self.digikey_pn = objDevice['digikey_pn']

        if 'mfg_pn' in objDevice:
            self.mfg_pn = objDevice['mfg_pn']
        
        if 'desc' in objDevice:
            self.desc = objDevice['desc']
        
        if 'description' in objDevice:
            self.desc = objDevice['description']
        
        if 'i2c_addr' in objDevice:
            self.i2c_addr = objDevice['i2c_addr']

        if 'datasheet' in objDevice:
            self.datasheet = objDevice['datasheet']
        
        if 'addr_size' in objDevice:
            self.addr_size = objDevice['addr_size']
        
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
        
        if 'configs' in objDevice:
            for configNode in objDevice['configs']:
                configItem = DevConfig(configNode)
                self.addConfig(configItem)
        
        if 'configurations' in objDevice:
            for configNode in objDevice['configurations']:
                configItem = DevConfig(configNode)
                self.addConfig(configItem)
               

        print("Parsed device: " + self.name )
        print( "registers: " + str(len(self.regs)))




        



        