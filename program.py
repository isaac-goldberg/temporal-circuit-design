from classes import *
import asyncio
            
async def main():
    entry = Entry()
    event1, event2 = entry.init_events(1, 2)
        
    gate = Max(event1, event2)
    gateout = gate.out_wire()
    
    add = AddConstant(gateout, 1.5)
    addout = add.out_wire()
    Exit(addout)
    
    try:
        await entry.start()
    except ExitProgram:
        print("Program terminated")
            
asyncio.run(main())
