""" Author:  Raghav Banka Proect: road_map
"""

from __future__ import annotations
from typing import Any, Optional
import networkx as nx
from plotly.graph_objs import Scatter, Figure

DEPTH = 50
LINE_COLOUR = 'rgb(239, 83, 80)'
VERTEX_BORDER_COLOUR = 'rgb(50, 50, 50)'
COLOUR = 'rgb(89, 205, 105)'


class _Vertex:
    """A vertex in a graph.

    Instance Attributes:
        - item: The data stored in this vertex.
        - neighbours: The vertices that are adjacent to this vertex.
    """
    item: Any
    neighbours: set[_Vertex]

    def __init__(self, item: Any, neighbours: set[_Vertex]) -> None:
        """Initialize a new vertex with the given item and neighbours."""
        self.item = item
        self.neighbours = neighbours

    def check_connected(self, target_item: Any, visited: set[_Vertex], depth: int = 0) -> bool:
        """Return whether this vertex is connected to a vertex corresponding to the target_item,
        WITHOUT using any of the vertices in visited.

        Preconditions:
            - self not in visited
        """
        if depth > 20:
            return False
        if self.item == target_item:
            # Our base case: the target_item is the current vertex
            return True
        else:
            visited.add(self)  # Add self to the list of visited vertices
            for u in self.neighbours:
                if u not in visited:  # Only recurse on vertices that haven't been visited
                    if u.check_connected(target_item, visited, depth + 1):
                        return True

            return False

    def check_connected_path(self, target_item: Any, visited: list, path: list, final_path: list,
                             depth: int, max_depth: int = 20) -> Optional[list]:
        """Return all paths between self and a vertex corresponding to the target_item,
        WITHOUT using any of the vertices in visited.

        Preconditions:
            - self not in visited
        """
        visited.append(self.item)
        path.append(self.item)
        if depth <= max_depth:
            if self.item == target_item and path not in final_path:
                if len(final_path) != 0:
                    count = 0
                    half = len(path) // 3
                    last = final_path[len(final_path) - 1]
                    for i in range(0, min(len(path), len(last))):
                        if last[i] == path[i]:
                            count += 1
                    if count < (len(path) - half):
                        final_path.append(list(path))
                else:
                    final_path.append(list(path))
            for i in self.neighbours:
                if i.item not in visited:
                    i.check_connected_path(target_item, visited, path, final_path, depth + 1)
        path.pop()
        visited.pop()
        if not path:
            return final_path

    def check_connected_distance(self, target_item: Any, visited: set[_Vertex], d: int) -> bool:
        """Return whether this vertex is connected to a vertex corresponding to the target_item,
        WITHOUT using any of the vertices in visited, by a path of length <= d.

        Preconditions:
            - self not in visited
            - d >= 0
        """
        if self.item == target_item and d >= 0:
            return True
        elif d < 0:
            return False
        else:
            new_visited = visited.union({self})
            return any(u.check_connected_distance(target_item, new_visited, d - 1)
                       for u in self.neighbours if u not in new_visited)

    def add_nodes(self, graph_nx: nx.Graph, visited: set, n: int = 0) -> None:
        """ Add vertices to graph"""
        if n == DEPTH:
            return
        visited.add(self)
        for u in self.neighbours:
            if u not in visited:
                graph_nx.add_node(u.item)
                u.add_nodes(graph_nx, visited, n + 1)


class Graph:
    """A graph.
    """
    # Private Instance Attributes:
    #     - _vertices:
    #         A collection of the vertices contained in this graph.
    #         Maps item to _Vertex object.
    _vertices: dict[Any, _Vertex]

    def __init__(self) -> None:
        """Initialize an empty graph (no vertices or edges)."""
        self._vertices = {}

    def add_vertex(self, item: Any) -> None:
        """Add a vertex with the given item to this graph.

        The new vertex is not adjacent to any other vertices.

        Preconditions:
            - item not in self._vertices
        """
        self._vertices[item] = _Vertex(item, set())

    def add_edge(self, item1: Any, item2: Any) -> None:
        """Add an edge between the two vertices with the given items in this graph.

        Raise a ValueError if item1 or item2 do not appear as vertices in this graph.

        Preconditions:
            - item1 != item2
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            v2 = self._vertices[item2]

            # Add the new edge
            v1.neighbours.add(v2)
            v2.neighbours.add(v1)
        else:
            # We didn't find an existing vertex for both items.
            raise ValueError

    def adjacent(self, item1: Any, item2: Any) -> bool:
        """Return whether item1 and item2 are adjacent vertices in this graph.

        Return False if item1 or item2 do not appear as vertices in this graph.
        """
        if item1 in self._vertices and item2 in self._vertices:
            v2 = self._vertices[item2]
            return any(u.item == item1 for u in v2.neighbours)
        else:
            return False

    def list_neighbours(self, item: Any) -> Optional[list]:
        """ Return the list of nodes adjacent to the input node in this graph

        Return None if item does not appear as vertices in this graph.
        """
        if item in self._vertices:
            v = self._vertices[item]
            return [u.item for u in v.neighbours]
        else:
            return None

    def num_edges(self) -> int:
        """Return the number of edges in this graph."""
        return sum(len(self._vertices[u].neighbours) for u in self._vertices) // 2

    def max_degree(self) -> int:
        """returns the maximum degree of a vertex in the graph (assuming the graph has at least
         one vertex)."""
        return max([len(self._vertices[u].neighbours) for u in self._vertices])

    def connected(self, item1: Any, item2: Any) -> bool:
        """Return whether item1 and item2 are connected vertices in this graph.

        Return False if item1 or item2 do not appear as vertices in this graph.

        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            return v1.check_connected(item2, set())  # Pass in an empty "visited" set
        else:
            return False

    def connected_path(self, item1: Any, item2: Any, max_depth: int = 20) -> Optional[list]:
        """Return a path between item1 and item 2 in this graph.

        The returned list contains the ITEMS along the path.
        Return None if no such path exists.
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            if max_depth <= 20:
                return v1.check_connected_path(item2, [], [], [], 0, max_depth)
            else:
                return v1.check_connected_path(item2, [], [], [], 0)
        return None

    def shortest_path(self, item1: Any, item2: Any) -> Optional[list]:
        """ Return the shortest path between item1 and item2 in this graph

        Return none if no such path exists
        """
        paths = self.connected_path(item1, item2)
        if paths is None or paths == []:
            return None
        min_path = paths[0]
        for item in paths:
            if len(item) < len(min_path):
                min_path = item
        return min_path

    def connected_distance(self, item1: Any, item2: Any, d: int = 20) -> bool:
        """Return whether items1 and item2 are connected by a path of length <= d.

        Preconditions:
            - d >= 0
        """
        if d > 20:
            return False
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            return v1.check_connected_distance(item2, set(), d)
        else:
            return False

    def read_file(self, filename:str) -> None:
        """ Read the text file and converting storing the data in this class"""

        with open(filename) as f:
            content = f.readlines()[3:]
        content = [x.strip() for x in content]
        for item in content[4:]:
            item = item.replace("\n", "")
            a, b = item.split("\t")
            if a not in self._vertices:
                self.add_vertex(a)
            if b not in self._vertices:
                self.add_vertex(b)
            self.add_edge(a, b)

    def to_networkx(self, item: str) -> nx.Graph:
        """Convert this graph into a networkx Graph.

        """
        graph_nx = nx.Graph()
        graph_nx.add_node(self._vertices[item].item)
        self._vertices[item].add_nodes(graph_nx, set())
        for u in graph_nx.nodes:
            for v in self._vertices[u].neighbours:
                if v.item in graph_nx.nodes:
                    graph_nx.add_edge(u, v.item)

        return graph_nx


def visualize_graph(graph_nx: nx.Graph,
                    layout: str = 'spring_layout',
                    output_file: str = '') -> None:
    """Using plotly and networkx to visualize the given graph.
        """

    pos = getattr(nx, layout)(graph_nx)

    x_values = [pos[k][0] for k in graph_nx.nodes]
    y_values = [pos[k][1] for k in graph_nx.nodes]
    labels = list(graph_nx.nodes)

    x_edges = []
    y_edges = []
    for edge in graph_nx.edges:
        x_edges += [pos[edge[0]][0], pos[edge[1]][0], None]
        y_edges += [pos[edge[0]][1], pos[edge[1]][1], None]

    trace3 = Scatter(x=x_edges,
                     y=y_edges,
                     mode='lines',
                     name='edges',
                     line=dict(color=LINE_COLOUR, width=3),
                     hoverinfo='none',
                     )
    trace4 = Scatter(x=x_values,
                     y=y_values,
                     mode='markers',
                     name='nodes',
                     marker=dict(symbol='circle-dot',
                                 size=5,
                                 color=COLOUR,
                                 line=dict(color=VERTEX_BORDER_COLOUR, width=0.5)
                                 ),
                     text=labels,
                     hovertemplate='%{text}',
                     hoverlabel={'namelength': 0}
                     )

    data1 = [trace3, trace4]
    fig = Figure(data=data1)
    fig.update_layout({'showlegend': False})
    fig.update_xaxes(showgrid=False, zeroline=False, visible=False)
    fig.update_yaxes(showgrid=False, zeroline=False, visible=False)

    if output_file == '':
        fig.show()
    else:
        fig.write_image(output_file)


graph_1 = Graph()
graph_1.read_file("roadNet-CA.txt")
graph_2 = Graph()
graph_2.read_file("roadNet-TX.txt")
