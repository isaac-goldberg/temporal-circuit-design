from classes import *
import asyncio
            
async def main():
    entry = Entry()
    event1, event2 = entry.out_events(1, 2)
        
    gate = Max(event1, event2)
    out = gate.out_events(0)
    
    Exit(out)
    
    try:
        await entry.start()
    except ExitProgram:
        print("Program terminated")
            
asyncio.run(main())
