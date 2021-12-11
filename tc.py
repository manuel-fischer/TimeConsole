from datetime import datetime
import time
import threading
import os, sys
import subprocess
import atexit


if os.name == "nt":
    from msvcrt import getch, getche
    scp = subprocess.check_output("chcp", shell=True)
    cp = int("".join(chr(c) for c in scp if chr(c) in "0123456789"))
    os.system("chcp 65001 > nul") # utf-8
    @atexit.register
    def atexit_codepage():
        os.system(f"chcp {cp} > nul")
    
else:
    from getch import getch, getche

def second_time():
    return datetime.now().replace(microsecond=0)


def timestamp():
    return int(time.time())


l = threading.Lock()
l.acquire()
stop = False


clock_prompt = ""
ls = ""
rs = ""
sp = 0

lpr = ""


def print_prompt():
    global sp, lpr
    #t = second_time().time()#.isoformat()
    t = datetime.now()

    dele = sp*' ' + (sp+len(rs))*'\b'
    pm = clock_prompt.format(t)
    pr = f"\r{pm}{ls}{rs}{dele}"
    if pr != lpr:
        print(end=pr, flush=True)
        sp = 0
        lpr = pr

    
def clock_thread():
    while not stop:
        with l:
            if stop: break
            print_prompt()
        time.sleep(0.01)

def trydecode(b):
    try:
        return b.decode()
    except UnicodeDecodeError:
        return '?' #repr(b)[2:-1]

def reprdecode(b):
    return repr(b)[2:-1]


def clock_input(prompt = ""):
    global ls, rs, sp, lpr, clock_prompt
    ls = rs = ""
    sp = 0
    lpr = ""
    clock_prompt = prompt
    print_prompt()
    l.release()
    try:
        while (c := getch()) != b'\r':
            with l:
                if c == b'\xe0':
                    cont = True
                    match getch():
                        case b'K': ls, rs = ls[:-1], ls[-1:]+rs # <-
                        case b'M': ls, rs = ls+rs[:1], rs[1:] # ->
                        case b'G': ls, rs = "", ls+rs # HOME
                        case b'O': ls, rs = ls+rs, "" # END
                        case b'S': rs = rs[1:]; sp += 1 # DEL
                        case k: c = ("^"+reprdecode(k)).encode(); cont = False

                    if cont: continue


                if c[0] & 0x80:
                    width = 0
                    m = 0x40
                    while c[0] & m:
                        m >>= 1
                        width += 1
                    for i in range(width):
                        c += getch()
                
                match c:
                    case b'\x1b':
                        sp += len(ls)+len(rs)
                        ls = rs = ""
                    case b'\x03': raise KeyboardInterrupt
                    #case b'\x04': raise EOFError
                    case b'\b':

                        if not ls[-1:].strip(): #spaces
                            tabpos = max(0, (len(ls)-1)//4*4)
                            
                            if not ls[tabpos:].strip(): # spaces
                                sp += len(ls)-tabpos
                                ls = ls[:tabpos]
                            else:
                                ls2 = ls.rstrip()
                                sp += len(ls) - len(ls2)
                                ls = ls2
                        else:
                            ls = ls[:-1]
                            sp += 1

                    case b'\t':
                        spc = 4-(len(ls)%4)
                        ls += ' ' * spc; sp = max(sp-spc, 0)
                        
                    case cc if cc < b'\x20': # special
                        ls += reprdecode(c); sp -= len(reprdecode(c))

                        
                    #case cc if b'\x7e' < cc < b'\xa0': # special
                    #    s += str(c); sp += len(str(c))
                    
                    case cc if b'\x80' <= cc < b'\xc0': # special  10xx.xxxx
                        ls += reprdecode(c); sp -= len(reprdecode(c))
                        
                    case _:
                        ls += trydecode(c); sp = max(sp-1, 0)
    finally:
        l.acquire()
    print()
    return ls+rs



clock_thrd = threading.Thread(target=clock_thread)
clock_thrd.start()















try:
    while True:
        class prompt:
            def format(time):
                #fmt = [
                #    "%H %M %S",
                #    "%H:%M %S",
                #    "%H %M:%S",
                #    "%H:%M:%S",
                #][int((time.microsecond/1e6)*4)%4]
                
                #fmt = [
                #    "%H %M %S",
                #    "%H.%M %S",
                #    "%H:%M %S",
                #    "%H.%M.%S",
                #    "%H %M:%S",
                #    "%H.%M:%S",
                #    "%H:%M:%S",
                #    "%H.%M.%S",
                #][int((time.microsecond/1e6)*8)%8]
                
                #fmt = [
                #    "x.      %H %M %S> ",
                #    "  .     %H.%M %S> ",
                #    "   .    %H:%M %S> ",
                #    "    .   %H.%M.%S> ",
                #    "     .x %H %M:%S> ",
                #    "    .   %H.%M:%S> ",
                #    "   .    %H:%M:%S> ",
                #    "  .     %H.%M.%S> ",
                #][int((time.microsecond/1e6)*8)%8]

                
                #fmt = [
                #    "%H %M %S>    >>>",
                #    "%H.%M %S>>    >>",
                #    "%H:%M %S>>>    >",
                #    "%H.%M.%S>>>>    ",
                #    "%H %M:%S >>>>   ",
                #    "%H.%M:%S  >>>>  ",
                #    "%H:%M:%S   >>>> ",
                #    "%H.%M.%S    >>>>",
                #][int((time.microsecond/1e6)*8)%8]

                FMT = [
                    "%H %M %S    ",
                    "%H %M  %S   ",
                    "%H %M   %S  ",
                    "%H %M    %S ",
                    "%H  %M   %S ",
                    "%H   %M  %S ",
                    "%H    %M %S ",
                    " %H   %M %S ",
                    "  %H  %M %S ",
                    "   %H %M %S ",

                    "      %M %S ",
                    "      %M %S ",
                    "%H    %M %S ",
                    "%H       %S ",
                    "%H       %S ",
                    "%H %M    %S ",
                    "%H %M       ",
                    "%H %M       ",
                ]
                
                FMT = [
                    "%H %M %S  > ",
                    "   %M       ",
                    "      %S  > ",
                    "          >>",
                    "      %S   >",
                    "   %M %S  >>",
                    "%H    %S  > ",
                    "   %M       ",
                    "%H %M       ",
                    "            ",
                    "%H          ",
                    "%H          ",
                    "            ",
                    "            ",
                    "            ",
                    "            ",
                ]

                fmt = FMT[int((time.microsecond/1e6)*len(FMT))%len(FMT)]

                
                return f"{time:{fmt}}"
            
        r = clock_input("{:%H:%M:%S}> ")
        #r = clock_input(prompt)
        
        print(r)
        

except KeyboardInterrupt:
    pass

finally:
    stop = True
    l.release()
