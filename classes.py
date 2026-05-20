import asyncio
import time

circuit_start = 0

class ExitProgram(Exception):
    pass

class Event:
    def __init__(self, delay: float, *output_gates):
        self.outputs = list(output_gates)
        self.delay = delay
    
    def __str__(self):
        return f"Event arriving in {self.delay}"
        
    def add_outputs(self, *output_gates):
        self.outputs.extend(output_gates)
    
    async def propagate(self):
        await asyncio.sleep(self.delay)
        for gate in self.outputs:
            await gate.propagate(self)
            
class Gate:
    def __init__(self, *input_events: Event):
        for in_event in input_events:
            self.init_input(in_event)
        
        self.inputs = list(input_events)
        self.outputs: list[Event] = []
        self.high = False
        
    def init_input(self, event: Event):
        event.add_outputs(self)
    
    def out_events(self, *delays: float):
        outs = []
        for delay in delays:
            out = Event(delay)
            self.outputs.append(out)
            outs.append(out)
            
        if len(outs) == 1:
            return outs[0]
        return tuple(outs)
    
    def add_inputs(self, *events: Event):
        for event in events:
            self.init_input(event)
        self.inputs.extend(events)
    
    def add_outputs(self, *events: Event):
        self.outputs.extend(events)
        
    async def final_propagate(self):
        for output in self.outputs:
            await output.propagate()
            
class Min(Gate):
    def __init__(self, *input_events):
        super().__init__(*input_events)
    
    async def propagate(self, _):
        if self.high:
            return
        self.high = True
        await self.final_propagate()
            
class Max(Gate):
    def __init__(self, *input_events: Event):
        super().__init__(*input_events)
    
    async def propagate(self, input):
        self.inputs.remove(input)
        if len(self.inputs) == 0:
            await self.final_propagate()
            
class Exit(Gate):
    def __init__(self, *input_events):
        super().__init__(*input_events)
    
    def out_events():
        print("cannot output from an exit gate")
        raise ExitProgram()
    
    async def propagate(_self, _):
        print(f"time elapsed: {time.time() - circuit_start}")
        raise ExitProgram()

class Entry(Gate):
    def __init__(self, *input_events: Event):
        super().__init__(*input_events)
    
    async def start(self):
        global circuit_start
        circuit_start = time.time()
        tasks = [asyncio.create_task(output.propagate()) for output in self.outputs]
        await asyncio.gather(*tasks)
        