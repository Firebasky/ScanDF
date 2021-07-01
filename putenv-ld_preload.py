# -*- coding: utf-8 -*
# @Author:Firebasky
# strace -f php -r "xxx"  2>&1 | grep -E "execve|fork|vfork"
'''
1.获得该函数的参数
2.获得该函数的参数的数据类型
3.去fuzz执行函数看是否有调用外部函数从而hook
'''
import os
import sys
import re

def getAllDefinedFunc():#获取全部函数
    get_defined_function = os.popen("php -r 'print_r(get_defined_functions()['internal']);'").readlines()
    #print get_defined_function
    b = get_defined_function[2:-1]
    b = map(str.strip, b)
    for i in range(len(b)):
        b[i] = re.sub(r'.*> ', '', b[i])
    get_defined_function = b  # all defined PHP functions
    get_defined_function.remove(get_defined_function[0])
    get_defined_function.remove(get_defined_function[0])
    get_defined_function.remove('readline')
    return get_defined_function


def getModuleFunc(phpModuleName,getDefinedFunction):#获取模块函数
    moduleFunc = []
    for func in getDefinedFunction:
        getExtNameCmd = 'php -r "echo (new ReflectionFunction("{}"))->getExtensionName();"'.format(func)
        extName = os.popen(getExtNameCmd).readlines()[0]
        if extName == phpModuleName:
            moduleFunc.append(func)
    return moduleFunc

def fuzzFunc(getDefinedFunction):
    for func in getDefinedFunction:
        maxParaNumCmd = 'php -r "echo (new ReflectionFunction("{}"))->getNumberOfParameters();"'.format(func)
        minParaNumCmd = 'php -r "echo (new ReflectionFunction("{}"))->getNumberOfRequiredParameters();"'.format(func)
        maxParaNum = int(os.popen(maxParaNumCmd).readlines()[0])
        minParaNum = int(os.popen(minParaNumCmd).readlines()[0])
        print(maxParaNum)
        print(minParaNum)
        for paraNum in range(minParaNum,maxParaNum + 1):#获得输入参数的范围
            paraMeters = ['\'1../../../../../../../../../etc/passwd\'' for i in range(paraNum)]#给参数需要字符串
            paraMeters = ','.join(paraMeters)
            newPhpCmd = "php -r \"{}({});\"".format(func,paraMeters)#去添加参数执行
            print(newPhpCmd)
            newFuzzCmd = "strace -f {} 2>&1 | grep -E 'execve|fork|vfork'".format(newPhpCmd)#去执行strace看是否满足条件
            print(newFuzzCmd)
            out = re.findall(r'execve', ''.join(os.popen(newFuzzCmd).readlines()[1:]))
            print(out)
            if len(out) >= 1:
                with open('fuzz-out.txt','a+') as file:
                    file.write(newPhpCmd + "\n")
                break
if __name__ == "__main__":
    if len(sys.argv) > 1:
        phpModuleName = sys.argv[1]
        getDefinedFunction = getAllDefinedFunc()
        moduleFunc = getModuleFunc(phpModuleName,getDefinedFunction)
        if len(moduleFunc) == 0:
            print ('没有找到与指定模块相关的函数，检查名称是否正确')
        else:
            #print moduleFunc
            fuzzFunc(moduleFunc)
    else:
        print ('fuzz all')
        getDefinedFunction = getAllDefinedFunc()
        fuzzFunc(getDefinedFunction)