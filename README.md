# Temporal Logic Circuit Simulation in Python
This repo has two ways to simulate a race logic circuit:

- `/realtime`: events are actually delayed in real time using asyncio and your system clock. Susceptible to jitter, so don't depend on delays that are more precise than the tenths digit.

- `/virtual2`: your program executes instanteously. Gates track the mock signals' cumulative delays through the circuit.

- `/virtual` (deprecated): your program executes instanteously, using a priority queue to ensure that events with different timings are certain to pop in the right order.