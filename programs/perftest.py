try:
    import op2api as api
except ImportError as e:
    print("API failed to import", e)
    input("Press enter to exit...")
    exit()
global version
version = True
try:
    import op2v
    version = True
except ImportError:
    pass
    version = False
global vers
vers = 0.1
global conf
#def save():
    
    #var = "perf"
    #fn = "perf.ini"
    #if api.os.path.exists(fn):
        #pass
    #else:
        #api.configFile(var, fn)
        #conf = api.ConfigParser()
        #conf.read(fn)
        #conf.add_section("score")
        #conf.set('score', 'tscore', '0')
        #with open(fn, 'w') as config:
            #conf.write(config)

        
#def reset():
    #var = "perf"
    #fn = "perf.ini"
    #conf = api.ConfigParser()
    #conf.read(fn)
    #conf.add_section("score")
    #conf.set('score', 'tscore', '0')
    #with open(fn, 'w') as config:
        #conf.write(config)

    
#def showscor():
   # global scar
    #scar = conf['score']
global total
total = 0
def main():
    api.time.sleep(api.sleep_timeIAppL)
    sleept = api.sleep_timecustom(50, api.cpu_module.cFreq)
    while True:
        api.clear()
        print("Performance Index", vers)
        print("CORE Version")
        api.linebr(20)
        print("1 - Start")
        print("2 - Exit")
        api.linebr(20)
        
        choice = input("> ")
        if choice == "1":
            frequ = api.cpu_module.cFreq
            mem = api.mb_module.mMem
            if api.lega == True:
                total = frequ + mem
                total = total / 2
                total = round(total, 1)
                print()
                api.time.sleep(sleept)
                print("Points:", total)
                if total <= 1000:
                    print("SCORE: 1/10")
                elif total <= 2000:
                    print("SCORE: 1.5/10")
                elif total <= 4000:
                    print("SCORE: 2/10")
                elif total <= 4500:
                    print("SCORE: 2.5/10")
                elif total <= 5000:
                    print("SCORE: 3/10")
                elif total <= 5500:
                    print("SCORE: 3.5/10")
                elif total <= 6000:
                    print("SCORE: 4/10")
                elif total <= 6500:
                    print("SCORE: 4.5/10")
                elif total <= 7000:
                    print("SCORE: 5/10")
                elif total <= 7500:
                    print("SCORE: 6/10")
                elif total <= 8000:
                    print("SCORE: 7/10")
                elif total <= 8500:
                    print("SCORE: 7.5/10")
                elif total <= 9000:
                    print("SCORE: 8/10")
                elif total <= 9500:
                    print("SCORE: 8.5/10")
                elif total <= 10000:
                    print("SCORE: 9/10")
                elif total <= 12000:
                    print("SCORE: 9.5/10")
                else:
                    print("SCORE: 10/10")
            elif op2v.op2VER == "0.5" or op2v.op2VER == "0.5 R2":
                total = frequ + mem
                total = total / 2
                total = round(total, 1)
                print()
                api.time.sleep(sleept)
                print("Points:", total)
                if total <= 1000:
                    print("SCORE: 1/10")
                elif total <= 2000:
                    print("SCORE: 1.5/10")
                elif total <= 4000:
                    print("SCORE: 2/10")
                elif total <= 4500:
                    print("SCORE: 2.5/10")
                elif total <= 5000:
                    print("SCORE: 3/10")
                elif total <= 5500:
                    print("SCORE: 3.5/10")
                elif total <= 6000:
                    print("SCORE: 4/10")
                elif total <= 6500:
                    print("SCORE: 4.5/10")
                elif total <= 7000:
                    print("SCORE: 5/10")
                elif total <= 7500:
                    print("SCORE: 6/10")
                elif total <= 8000:
                    print("SCORE: 7/10")
                elif total <= 8500:
                    print("SCORE: 7.5/10")
                elif total <= 9000:
                    print("SCORE: 8/10")
                elif total <= 9500:
                    print("SCORE: 8.5/10")
                elif total <= 10000:
                    print("SCORE: 9/10")
                elif total <= 12000:
                    print("SCORE: 9.5/10")
                else:
                    print("SCORE: 10/10")
            elif version == False:
                total = frequ + mem
                total = total / 2
                total = round(total, 1)
                print()
                api.time.sleep(sleept)
                print("Points:", total)
                if total <= 1000:
                    print("SCORE: 1/10")
                elif total <= 2000:
                    print("SCORE: 1.5/10")
                elif total <= 4000:
                    print("SCORE: 2/10")
                elif total <= 4500:
                    print("SCORE: 2.5/10")
                elif total <= 5000:
                    print("SCORE: 3/10")
                elif total <= 5500:
                    print("SCORE: 3.5/10")
                elif total <= 6000:
                    print("SCORE: 4/10")
                elif total <= 6500:
                    print("SCORE: 4.5/10")
                elif total <= 7000:
                    print("SCORE: 5/10")
                elif total <= 7500:
                    print("SCORE: 6/10")
                elif total <= 8000:
                    print("SCORE: 7/10")
                elif total <= 8500:
                    print("SCORE: 7.5/10")
                elif total <= 9000:
                    print("SCORE: 8/10")
                elif total <= 9500:
                    print("SCORE: 8.5/10")
                elif total <= 10000:
                    print("SCORE: 9/10")
                elif total <= 12000:
                    print("SCORE: 9.5/10")
                else:
                    print("SCORE: 10/10")
            else:
                spacee = api.hd_module.hddspace
                total = frequ + mem + spacee
                total = total / 3
                total = round(total, 1)
                print()
                api.time.sleep(sleept)
                print("Points:", total)
                if total <= 1000:
                    print("SCORE: 1/10")
                elif total <= 2000:
                    print("SCORE: 1.5/10")
                elif total <= 4000:
                    print("SCORE: 2/10")
                elif total <= 4500:
                    print("SCORE: 2.5/10")
                elif total <= 5000:
                    print("SCORE: 3/10")
                elif total <= 5500:
                    print("SCORE: 3.5/10")
                elif total <= 6000:
                    print("SCORE: 4/10")
                elif total <= 6500:
                    print("SCORE: 4.5/10")
                elif total <= 7000:
                    print("SCORE: 5/10")
                elif total <= 7500:
                    print("SCORE: 6/10")
                elif total <= 8000:
                    print("SCORE: 7/10")
                elif total <= 8500:
                    print("SCORE: 7.5/10")
                elif total <= 9000:
                    print("SCORE: 8/10")
                elif total <= 9500:
                    print("SCORE: 8.5/10")
                elif total <= 10000:
                    print("SCORE: 9/10")
                elif total <= 12000:
                    print("SCORE: 9.5/10")
                else:
                    print("SCORE: 10/10")
            print()
            print("Identified Hardware:")
            print("  Motherboard - "+api.mb_module.mName)
            print("  Physical Memory - "+api.mb_module.mMemS)
            print("  Processor - "+api.cpu_module.cName)
            print("  Processor Speed - "+api.cpu_module.cFreqS+api.cpu_module.cFreqUnit)
            if api.lega == True:
                pass
            elif op2v.op2VER == "0.5" or op2v.op2VER == "0.5 R2":
                pass
            elif version == False:
                pass
            else:
                print("  Hard Disk - "+api.hd_module.hddnameS)
                print("  Hard Disk Storage - "+api.hd_module.hddspaceS)
            print()
            input("Press enter to return...")
        elif choice == "2":
            api.clear()
            return

try:
    import op2api as api
    api.check()
    pass
    if api.apiverI < 0.5:
        print("Cannot load: Too low API version. Expected Version 0.5")
        input("")
        exit()
    elif api.lega == True:
        main()
    elif api.apiverI == 0.5 or api.apiverI > 0.5 and op2v.op2VER == "0.6.1" or op2v.op2VER == "0.6" or op2v.op2VER == "0.6 R2" or op2v.op2VER == "0.5 R2" or op2v.op2VER == "0.5":
        main()
    elif api.apiverI >= 0.5 and op2v.op2VER == "0.6.2" or op2v.op2VERI >= 0.7:
        main()
except ImportError:
    print("API not found/ not working")