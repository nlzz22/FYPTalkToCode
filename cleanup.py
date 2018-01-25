import psutil

PROCNAME = "pythonw.exe"

for proc in psutil.process_iter():
    if proc.name() == PROCNAME:
        if proc.cpu_percent(interval=0.1) > 20:
            proc.terminate()
            print ("Terminated the following process:")
            print(proc)
            print "\n"

print ("Cleanup is complete.")
        
