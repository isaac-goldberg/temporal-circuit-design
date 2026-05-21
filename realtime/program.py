from classes import *
import asyncio
            
async def main():
    entry = Entry()
    entry.schedule(1)
    entry.schedule(2)
        
    gate = Min()
    entry.connect(gate)
    
    delay = AddConstant(0.5)
    gate.connect(delay)

    exit = Exit()
    delay.connect(exit)
    
    try:
        await entry.start()
    except ExitProgram:
        print("Program terminated")
            
asyncio.run(main())
