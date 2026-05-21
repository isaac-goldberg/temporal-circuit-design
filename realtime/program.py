from classes import *
import asyncio

async def main():
    entry = Entry()
    entry.schedule(1)
    entry.schedule(2)
    
    gate = Max(2)
    entry.connect(gate)
    delay = AddConstant(0.5)
    gate.connect(delay)
    
    delay2 = AddConstant(0.5)
    entry.connect(delay2)
    
    mingate = Min()
    delay.connect(mingate)
    delay2.connect(mingate)

    exit = Exit()
    mingate.connect(exit)
    
    try:
        await entry.start()
    except ExitProgram:
        print("Program terminated")
            
asyncio.run(main())
