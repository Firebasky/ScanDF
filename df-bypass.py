# -*- coding: utf-8 -*
# /usr/bin/python3
# @Author:Firebasky
'''
扫描思路
1.获得全部可以利用的函数
2.匹配漏网之鱼
3.根据感觉判断是不是uaf
4.判断fpm利用 ban了putenv
5.判断putenv利用hook so
'''

import argparse
import requests
import re

parser = argparse.ArgumentParser()
parser.add_argument("-u", help="phpinfo URL: eg. https://example.com/phpinfo.php")
parser.add_argument("-f", help="phpinfo localfile path: eg. dir/phpinfo")

args = parser.parse_args()

class colors:
    reset='\033[0m'
    red='\033[31m'
    green='\033[32m'
    orange='\033[33m'
    blue='\033[34m'

print(colors.green + """
 ____                  ____  _____ 
/ ___|  ___ __ _ _ __ |  _ \|  ___|
\___ \ / __/ _` | '_ \| | | | |_   
 ___) | (_| (_| | | | | |_| |  _|  
|____/ \___\__,_|_| |_|____/|_|    
""" + "\n\t\t\t\t" + colors.blue + "authors: " + colors.orange + "Firebasky" + "\n" + colors.reset)

def Get_phpinfo(args):
    if (args.u):
        url = args.u
        phpinfo = requests.get(url).text  # 获得phpinfo信息
        return phpinfo
    elif (args.f):
        phpinfofile = args.f
        phpinfo = open(phpinfofile, 'r').read()  # 获得phpinfo信息
        return phpinfo
    else:
        print(parser.print_help())
        exit()

dis_fun = []
phpinfo = Get_phpinfo(args)

dis_fun = phpinfo.split('disable_functions</td><td class="v">')[1].split("</")[0].split(',')[:-1]

phpversion = re.findall("<title>PHP (.*) - phpinfo\(\)</title>",phpinfo)

serverapi = re.findall("<tr><td class=\"e\">Server API </td><td class=\"v\">(.*) </td></tr>",phpinfo)

lwzy = ['system', 'shell_exec', 'exec', 'passthru', 'popen', 'proc_open', 'pcntl_exec', 'dl']

#我们能够的函数
dangerous_functions = ['pfsockopen','fsockopen','stream_socket_client','stream_socket_client','pcntl_alarm','pcntl_fork','pcntl_waitpid','pcntl_wait','pcntl_wifexited','pcntl_wifstopped','pcntl_wifsignaled','pcntl_wifcontinued','pcntl_wexitstatus','pcntl_wtermsig','pcntl_wstopsig','pcntl_signal','pcntl_signal_get_handler','pcntl_signal_dispatch','pcntl_get_last_error','pcntl_strerror','pcntl_sigprocmask','pcntl_sigwaitinfo','pcntl_sigtimedwait','pcntl_exec','pcntl_getpriority','pcntl_setpriority','pcntl_async_signals','error_log','system','exec','shell_exec','popen','proc_open','passthru','link','symlink','syslog','mail']

def Get_Dafun(dangerous_functions):#通过匹配ini获得扩展的危险函数然后利用
    modules = []
    if("mbstring.ini" in phpinfo):#安装的mbstring模块
        modules += ['mbstring']
        dangerous_functions += ['mb_send_mail']

    if("imap.ini" in phpinfo):#安装的imap扩展
        modules += ['imap']
        dangerous_functions += ['imap_open','imap_mail']

    if("libvirt-php.ini" in phpinfo):#安装的libvert扩展
        modules += ['libvert']
        dangerous_functions += ['libvirt_connect']

    if("gnupg.ini" in phpinfo):#安装的gnupg模块
        modules += ['gnupg']
        dangerous_functions += ['gnupg_init']

    return dangerous_functions

def Scan_Fun(dangerous_functions):
    exploitable_functions = []
    for i in dangerous_functions:
        if i not in dis_fun:
            exploitable_functions.append(i)#筛选过滤
    if len(exploitable_functions)==0:
        print('\nThe disable_functions I don\'t know')
    else:
        print('\nThis functions can used:')
        print(','.join(exploitable_functions))

#1.漏网之鱼,可以直接执行命令
def Get_LWZY(lwzy):
    exploitable_functions = []
    for i in lwzy:
        if i not in dis_fun:
            exploitable_functions.append(i)#筛选过滤
    if len(exploitable_functions)==0:
        print('\nNot easy!!')
        Get_uaf()
    else:
        print(colors.red+'\nnice,can exec!!! use below function'+colors.red)
        print(','.join(exploitable_functions))

#2.php>7 一般是uaf
def Get_uaf():
    if(int(phpversion[0].split(".")[0])>=7):
        print("mayby have uaf,yijian uaf used\n")
        Get_fpm()
    else:
        Get_fpm()

#3.fpm利用 过滤了函数,使用其他函数实现功能
def Get_fpm():
    if ("FPM/FastCGI" in serverapi[0]):
        print(colors.orange+"Maybe fpm can exploit,This functions pfsockopen,stream_socket_sendto,stream_socket_client,fsockopen can also to exploit FPM,maybe modify yijian source code！！！"+colors.orange)
    else:
        Get_putenv(dis_fun)

#4.putenv-LD_PRELOAD
def Get_putenv(dis_fun):
    if("putenv" not in dis_fun):
        print(colors.blue+"Almost use putenv-LD_PRELOAD to hook\n"+colors.blue)
    if ("imagick.ini" in phpinfo):
        print(colors.blue+'\nPHP-imagick module is present. It can be exploited using LD_PRELOAD method\n'+colors.blue)
    else:
        print("mayby this is 0day!!\n maybe use extend's function to trigger putenv, can use putenv-ld_preload.py to fuzz")

Scan_Fun(Get_Dafun(dangerous_functions))
Get_LWZY(lwzy)

# print(serverapi[0])