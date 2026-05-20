import time
import asyncio

circuit_start = 0

class ExitProgram(Exception):
    pass

class Wire:
    def __init__(self, delay: float, *output_gates):
        self.outputs = list(output_gates)
        self.delay = delay
        
    def add_outputs(self, *output_gates):
        self.outputs.extend(output_gates)
    
    async def propagate(self):
        await asyncio.sleep(self.delay)
        for gate in self.outputs:
            await gate.propagate(self)
            
class Gate:
    def __init__(self, *input_wires: Wire):
        for in_wire in input_wires:
            self.init_input(in_wire)
        
        self.inputs = list(input_wires)
        self.outputs: list[Wire] = []
        self.high = False
        
    def init_input(self, wire: Wire):
        wire.add_outputs(self)
        
    def out_wire(self, delay: float):
        out = Wire(delay)
        self.outputs.append(out)
        return out
    
    def add_inputs(self, *wires: Wire):
        for wire in wires:
            self.init_input(wire)
        self.inputs.extend(wires)
    
    def add_outputs(self, *wires: Wire):
        self.outputs.extend(wires)
        
    async def final_propagate(self):
        for output in self.outputs:
            await output.propagate()
            
class Min(Gate):
    def __init__(self, *input_wires):
        super().__init__(*input_wires)
    
    async def propagate(self, _):
        if self.high:
            return
        self.high = True
        await self.final_propagate()
            
class Max(Gate):
    def __init__(self, *input_wires: Wire):
        super().__init__(*input_wires)
    
    async def propagate(self, input):
        self.inputs.remove(input)
        if len(self.inputs) == 0:
            await self.final_propagate()
            
class Exit(Gate):
    def __init__(self, *input_wires):
        super().__init__(*input_wires)
    
    def out_wire():
        print("cannot get output wire from an exit gate")
    
    async def propagate(_self, _):
        print(f"time elapsed: {time.time() - circuit_start}")
        raise ExitProgram()

class Entry:
    def __init__(self, *input_wires: Wire):
        self.outputs = list(input_wires)
        
    def add_outputs(self, *wires: Wire):
        self.outputs.extend(wires)
    
    async def start(self):
        global circuit_start
        circuit_start = time.time()
        tasks = [asyncio.create_task(output.propagate()) for output in self.outputs]
        await asyncio.gather(*tasks)
            
async def main():
    entry = Entry()
        
    wire1 = Wire(1)
    wire2 = Wire(2)
    entry.add_outputs(wire1, wire2)
    
    gate = Min(wire1, wire2)
    out = gate.out_wire(0)
    
    Exit(out)
    
    try:
        await entry.start()
    except ExitProgram:
        print("Program terminated")
            
asyncio.run(main())