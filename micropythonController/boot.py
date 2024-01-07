# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
import os, machine
#os.dupterm(None, 1) # disable REPL on UART(0)
import gc
#import webrepl
#webrepl.start()
gc.collect()

# states which team gets a goal; so RED controller needs to be mounted in the black goal
# possible values RED and BLACK
team = 'RED'

# giving every controller a static IP seems to work better when connecting
thisIpAddress = '10.42.0.111'