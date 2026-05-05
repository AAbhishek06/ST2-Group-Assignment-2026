DSA Explorer and Visualiser App

Overview
This project is an interactive visual tool built with pygame. It helps users learn data structures and algorithms through animations and user interaction.

The app includes three main phases. Each phase focuses on a different concept and provides visual demonstrations.

Features

Phase 1. Data Structures

Stack operations. Push and pop
Queue operations. Enqueue and dequeue
Linked list editor. Insert, delete, reverse
Binary search tree. Insert and traversals

Phase 2. Algorithms

Sorting visualisations. Bubble sort, selection sort, merge sort
Graph traversal. BFS and DFS
Heap operations. Insert and extract

Phase 3. Puzzle Challenges

Pathfinding using Dijkstra or A star
Event queue simulation using priority queue
Dynamic programming grid path visualisation

Project Structure

menu.py
Entry point and handles navigation between modules
configure.py
Stores global constants like colors and screen size
utilities.py
Shared helper functions
Phase_1
Data structure implementations and visualisations
Phase_2
Algorithm visualisations
Phase_3
Puzzle based implementations

How to Run

Install dependencies
pip install pygame
Run the application
python main.py
Use mouse clicks to navigate between modules

Controls

Mouse click to interact with buttons
On screen instructions guide actions inside each module

Requirements

Python 3.x
pygame

Design Approach

Modular design
Each concept implemented in a separate file
Reusable utilities across modules
Consistent UI elements and layout

Testing

Basic manual testing was performed:

Verified each module loads correctly
Checked algorithm execution
Confirmed navigation returns to menu

Future Improvements

Add more algorithms
Improve animations
Add speed controls
Add automated unit tests
