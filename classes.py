import asyncio
import time

circuit_start = 0

class ExitProgram(Exception):
    pass

class Event:
    def __init__(self, delay: float):
        self.outputs: list[Gate] = []
        self.delay = delay
    
    def __str__(self):
        return f"<Event arriving in {self.delay}>"
        
    def add_outputs(self, *output_gates):
        self.outputs.extend(output_gates)
    
    async def propagate(self):
        await asyncio.sleep(self.delay)
        for gate in self.outputs:
            await gate.propagate(self)
            
"""A wire is just an event with delay 0, used for connecting gates instanteously."""
class Wire(Event):
    def __init__(self):
        super().__init__(0)

"""Base class for all gates."""
class Gate:
    def __init__(self, *input_events: Event):
        for in_event in input_events:
            self.init_input(in_event)
        
        self.inputs = list(input_events)
        self.outputs: list[Event] = []
        self.high = False
    
    """Get one output wire from this gate."""
    def out_wire(self):
        wire = Wire()
        self.outputs.append(wire)
        return wire
        
    """Get multiple (identical) output wires from this gate. Returns a tuple."""
    def out_wires(self, count: int):
        wires = []
        for _ in range(count):
            out = Wire()
            self.outputs.append(out)
            wires.append(out)
        if count == 1:
            return wires[0]
        return tuple(wires)
        
    def init_input(self, event: Event):
        event.add_outputs(self)
    
    def add_inputs(self, *events: Event):
        for event in events:
            self.init_input(event)
        self.inputs.extend(events)
    
    def add_outputs(self, *events: Event):
        self.outputs.extend(events)
        
    async def final_propagate(self):
        self.high = True
        for output in self.outputs:
            await output.propagate()
            
class Min(Gate):
    """The Min gate takes any number of inputs. It outputs once any input goes high."""
    
    def __init__(self, *input_events):
        super().__init__(*input_events)
    
    async def propagate(self, _):
        if self.high:
            return
        await self.final_propagate()
            
class Max(Gate):
    """The Max gate takes any number of inputs. It outputs once all inputs are high."""
    
    def __init__(self, *input_events: Event):
        super().__init__(*input_events)
    
    async def propagate(self, input):
        self.inputs.remove(input)
        if len(self.inputs) == 0:
            await self.final_propagate()
            
class AddConstant(Gate):
    """The AddConstant gate takes exactly one input event T and a constant K, and outputs at time T + K."""
    
    def __init__(self, input_event: Event, K: float):
        self.K = K
        super().__init__(input_event)
        
    async def propagate(self, _):
        await asyncio.sleep(self.K)
        await self.final_propagate()
        
class Inhibit(Gate):
    """The Inhibit gate takes exactly two inputs: Td (data) and Tc (control), and outputs at time Td if and only if Td < Tc."""

    def __init__(self, Td: Event, Tc: Event):
        self.td = Td
        self.tc = Tc
        self.tc_arrived = False
        
    async def propagate(self, event: Event):
        if self.tc_arrived or self.high:
            return
        
        if event == self.tc:
            self.tc_arrived = True
        elif event == self.td:
            self.final_propagate()
        else:
            print("error: tried to propagate inhibit gate from an event that isn't the Td or Tc for this gate")
            
class Exit(Gate):
    def __init__(self, *input_events):
        super().__init__(*input_events)
    
    def out_wire():
        print("cannot output from an exit gate")
        raise ExitProgram()
    
    async def propagate(_self, _):
        print(f"time elapsed: {time.time() - circuit_start}")
        raise ExitProgram()

class Entry(Gate):
    def __init__(self, *input_events: Event):
        super().__init__(*input_events)
        
    def init_events(self, *delays: float):
        events = []
        for delay in delays:
            out = Event(delay)
            self.outputs.append(out)
            events.append(out)
            
        if len(events) == 1:
            return events[0]
        return tuple(events)
    
    async def start(self):
        global circuit_start
        circuit_start = time.time()
        tasks = [asyncio.create_task(output.propagate()) for output in self.outputs]
        await asyncio.gather(*tasks)
        