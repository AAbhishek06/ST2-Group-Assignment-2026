# benchmark.py
import os
import sys
import time
import heapq

# Path is for:
# main project folder / Testing / benchmark.py
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from Phase_1.bst import BinarySearchTree
from Phase_1.linked_list import SingleLinkedList
from Phase_1.stack_queue import StackQueueVisualiser

from Phase_2.sorting import SortingVisualiser
from Phase_2.heap import HeapVisualiser
from Phase_2.graph import GraphVisualizer

from Phase_3.pathfinding import PathfindingVisualiser
from Phase_3.event_queue import Event
from Phase_3.dynamic import DynamicProgrammingVisualiser


def time_function(name, function):
    start_time = time.perf_counter()
    function()
    end_time = time.perf_counter()

    duration = end_time - start_time
    print(f"{name:<50} {duration:.6f} seconds")

# Phase 1 Benchmarks

def benchmark_stack_queue():
    visualiser = StackQueueVisualiser()

    for i in range(1000):
        visualiser.input_text = str(i)
        visualiser.add_to_stack()

    for _ in range(1000):
        visualiser.remove_from_stack()

    for i in range(1000):
        visualiser.input_text = str(i)
        visualiser.add_to_queue()

    for _ in range(1000):
        visualiser.remove_from_queue()


def benchmark_linked_list():
    linked_list = SingleLinkedList()

    for i in range(1000):
        linked_list.insert_at_index(i, i)

    linked_list.search(999)
    linked_list.reverse()
    linked_list.delete_value(500)


def benchmark_bst():
    tree = BinarySearchTree()

    # Use 500 values to avoid deep recursive insertion issues.
    for i in range(500):
        tree.insert(i)

    tree.inorder()
    tree.preorder()
    tree.postorder()


# -------------------------
# Phase 2 Benchmarks
# -------------------------

def benchmark_sorting():
    values = list(range(200, 0, -1))

    bubble = SortingVisualiser()
    bubble.numbers = values.copy()
    bubble.build_bubble_steps()

    selection = SortingVisualiser()
    selection.numbers = values.copy()
    selection.build_selection_steps()

    merge = SortingVisualiser()
    merge.numbers = values.copy()
    merge.build_merge_steps()


def benchmark_heap():
    heap_visualiser = HeapVisualiser()

    for i in range(300, 0, -1):
        heap_visualiser.input_text = str(i)
        heap_visualiser.insert_value()

        while heap_visualiser.animating:
            heap_visualiser.update_animation()

    while heap_visualiser.heap:
        heap_visualiser.extract_min()

        while heap_visualiser.animating:
            heap_visualiser.update_animation()


def benchmark_graph():
    graph = GraphVisualizer()
    graph.set_start("A")

    # Supports the original graph.py version.
    if hasattr(graph, "start_bfs"):
        graph.start_bfs()

        while graph.queue:
            graph.step()

        graph.set_start("A")
        graph.start_dfs()

        while graph.stack:
            graph.step()

    # Supports the upgraded graph.py version.
    elif hasattr(graph, "choose_bfs"):
        graph.choose_bfs()

        while graph.queue:
            graph.step()

        graph.set_start("A")
        graph.choose_dfs()

        while graph.stack:
            graph.step()


# -------------------------
# Phase 3 Benchmarks
# -------------------------

def benchmark_pathfinding():
    visualiser = PathfindingVisualiser()

    visualiser.start = (0, 0)
    visualiser.end = (24, 24)

    visualiser.run_pathfinding()


def benchmark_event_queue():
    heap = []

    for i in range(1000):
        event = Event(f"E{i}", i % 10, time.time())
        heapq.heappush(heap, event)

    while heap:
        heapq.heappop(heap)


def benchmark_dynamic_programming():
    visualiser = DynamicProgrammingVisualiser()

    visualiser.start = (0, 0)
    visualiser.end = (24, 24)

    visualiser.run_dp()


if __name__ == "__main__":
    print("DSA Explorer and Visualiser Benchmark Results")
    print("=" * 65)

    print("\nPhase 1: Data Structure Playground")
    print("-" * 65)
    time_function("Stack and Queue operations", benchmark_stack_queue)
    time_function("Linked List insert/search/reverse/delete", benchmark_linked_list)
    time_function("BST insert and traversals", benchmark_bst)

    print("\nPhase 2: Algorithm Visualiser")
    print("-" * 65)
    time_function("Sorting step generation", benchmark_sorting)
    time_function("Heap insert and extract", benchmark_heap)
    time_function("Graph BFS and DFS traversal", benchmark_graph)

    print("\nPhase 3: Puzzle Challenges")
    print("-" * 65)
    time_function("Pathfinding grid search", benchmark_pathfinding)
    time_function("Event Queue priority processing", benchmark_event_queue)
    time_function("Dynamic Programming grid calculation", benchmark_dynamic_programming)

    print("\nBenchmarking complete.")
