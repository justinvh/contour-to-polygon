"""
Solves for a polygon that wraps a contour in pixel-space
"""
import numpy as np
import pprint
import logging

from collections import defaultdict, Counter


logger = logging.getLogger(__name__)


class ContourToPolygon:
    def __init__(self, contour):
        self.contour = contour 
        self.edges = {}
        self.polygon = []
        self.contour_to_edges()
        self.edges_to_polygon()

    @classmethod
    def from_filename(cls, filename):
        """
        Reads an input file where '#' denotes an occupied cell.
        Starts from (1, 1) as convention of OpenCV (no borders)
        """
        contour = []
        with open(filename) as fd:
            data = fd.read()
            for y, line in enumerate(data.splitlines(), start=1):
                for x, ch in enumerate(line, start=1):
                    if ch == '#':
                        contour.append((x, y))
        return ContourToPolygon(contour)

    def make_key(self, *args):
        """
        Stable ordering of integer nodes for a unique key in traversals
        """
        return '-'.join(str(x) for x in sorted(args))

    def make_edge(self, node1, node2):
        """
        Marks an edge occupied
        """
        key = self.make_key(node1, node2)
        self.edges[key] = True

    def contour_to_edges(self):
        """
        Takes an input contour and forms the edges that make up each cell
        """
        for x, y in self.contour:
            # Nodes
            tl = (x - 1, y - 1)
            tr = (x + 0, y - 1)
            br = (x + 0, y + 0)
            bl = (x - 1, y + 0)

            # Edges
            self.make_edge(tl, tr)
            self.make_edge(tr, br)
            self.make_edge(br, bl)
            self.make_edge(bl, tl)

    def edges_to_polygon(self):
        """
        Turns the edges into one polygon that wrap around the exterior
        """
        # TODO(jvh): Pick exterior corner
        # Setup the initial conditions
        x, y = self.contour[0]
        curr = (x + 0, y - 1)
        prev = (x - 1, y - 1)
        key = self.make_key(prev, curr)

        # Simple function to see if an edge exists
        def edge_exists(ref, dx, dy):
            x, y = ref
            x += dx
            y += dy
            key = self.make_key((x, y), ref)
            return key in self.edges

        seen = set()
        self.polygon.append(prev)
        while True:
            # If we've seen the current edge, then we're done
            key = self.make_key(prev, curr)
            if key in seen:
                break
        
            # Mark the edge as seen and add to the polygon
            self.polygon.append(curr)
            seen.add(key)
            
            # Which directions can we go from our current spot
            right = edge_exists(curr, 1, 0)
            left = edge_exists(curr, -1, 0)
            up = edge_exists(curr, 0, -1)
            down = edge_exists(curr, 0, 1)

            # Determine where we're from and we're we going
            cx, cy = curr
            px, py = prev 

            # Are we moving in a vertical direction or horizontal
            horizontal = py == cy
            vertical = px == cx

            # Constrain movement to prevent walking backwards
            if horizontal:
                if px < cx:
                    left = False
                else:
                    right = False

            # Constrain movement to prevent walking backwards
            elif vertical:
                if py > cy:
                    down = False
                else:
                    up = False

            prev = curr

            # Always ensure right hand traversals by creating a state-machine
            # TODO(jvh): If there is a way to resolve ambiguous edges (T-shape)
            # during graph creation, that would be great.

            """
            1 |2 |3 |4
             #|  |# |#
            # |##|# | #
            """

            x, y = curr

            # 1, 2, 3
            if horizontal:
                if down and up and right:
                    y -= 1
                elif down and up and left:
                    y += 1
                elif down and right:
                    x += 1
                elif up and left:
                    x -= 1
                elif up:
                    y -= 1
                elif down:
                    y += 1

            # 4, 3, 2
            elif vertical:
                if down and left and right:
                    x += 1
                elif up and left and right:
                    x -= 1
                elif down and left:
                    y += 1
                elif up and right:
                    y -= 1
                elif left:
                    x -= 1
                elif right: 
                    x += 1

            curr = x, y


if __name__ == '__main__':
    import sys
    c2p = ContourToPolygon.from_filename(sys.argv[1])
    print(c2p.polygon)

