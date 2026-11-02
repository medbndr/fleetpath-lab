# Design notes

## Architecture

Breadth-first search over (cell, tick) states gives shortest arrival time for each robot under existing reservations. Vertex reservations forbid shared cells; reverse edge reservations forbid swaps. Final cells remain occupied.

## Tradeoffs

Worst-case per robot: O(width × height × horizon) time and memory, plus goal-tail checks. Priorities trade completeness for a simple predictable planner.

## Understanding and extending the project

1. Explain why ordinary shortest paths can still collide.
2. Reverse robot priority and compare makespan.
3. Add A* with an admissible Manhattan heuristic; preserve the tests.

## Engineering provenance

This repository was prepared with AI-assisted implementation and documentation.
Review the code, run the tests, and make your own extensions before describing
particular design decisions as your independent work. No production deployment,
client usage, or historical development activity is claimed.
