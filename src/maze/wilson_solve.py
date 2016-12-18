import random
from lzw import *
from maze import *


width = 101
height = 81
maze = Maze(width, height)
root = (margin, margin)
maze.stream += maze.encode_frame(wall_color=0)
maze.stream += pad_delay_frame(delay=100, trans_index=3)

tree = set([root])
maze.mark_cell(root, intree)

for cell in maze.cells:
    if cell not in tree:
        path = [cell]
        maze.mark_cell(cell, inpath)

        current_cell = cell
        # start a loop erased random walk at current_cell
        while current_cell not in tree:
            next_cell = random.choice(maze.get_neighbors(current_cell))
            if next_cell in path:
                # so we have found a loop in the path, erase it!
                index = path.index(next_cell)
                maze.mark_path(path[index:], iswall)
                maze.mark_cell(path[index], inpath)
                path = path[:index+1]
            else:
                # add this cell to path and continue the walk from it
                path.append(next_cell)
                maze.mark_cell(next_cell, inpath)
                maze.mark_wall(current_cell, next_cell, inpath)

            current_cell = next_cell

            if maze.num_changes >= speed:
                maze.stream += (graphics_control_block(delay=2, trans_index=3)
                               + maze.encode_frame(wall_color=0, tree_color=1, path_color=2))

        # once the random walk hits the tree, add the path to the tree
        # and continue the loop at any new cell that is not in the tree
        tree = tree.union(path)
        maze.mark_path(path, intree)


if maze.num_changes > 0:
        maze.stream += (graphics_control_block(delay=2, trans_index=3)
                        + maze.encode_frame(wall_color=0, tree_color=1, path_color=2))

maze.stream += pad_delay_frame(delay=500, trans_index=3)


start = (margin, margin)
end = (width - 1 - margin, height - 1 - margin)
stack = [(root, root)]
visited = set([start])
where = dict()
maze.mark_cell(start, painted)

while stack:
    current, last = stack.pop()
    where[current] = last
    maze.mark_wall(current, last, painted)

    if current == end:
        break
    else:
        maze.mark_cell(current, painted)
        for next_cell in maze.get_neighbors(current):
            if (next_cell not in visited) and (not maze.check_wall(current, next_cell)):
                stack.append((next_cell, current))
                visited.add(next_cell)

    if maze.num_changes >= speed:
        maze.stream += (graphics_control_block(delay=5, trans_index=0)
                        + maze.encode_frame(wall_color=0, tree_color=0, path_color=0, paint_color=3))

if maze.num_changes > 0:
    maze.stream += (graphics_control_block(delay=5, trans_index=0)
                    + maze.encode_frame(wall_color=0, tree_color=0, path_color=0, paint_color=3))

# now add the frame that shows the path !
# but we have to retrieve the path first:
path = [end]
tmp = end
while tmp != start:
    tmp = where[tmp]
    path.append(tmp)

maze.mark_path(path, inpath)
maze.stream += (graphics_control_block(delay=5, trans_index=0)
                + maze.encode_frame(wall_color=0, tree_color=0, path_color=2, paint_color=3))

# delay the frame to show the path clearly
maze.stream += pad_delay_frame(1000, trans_index=0)
maze.write_to_gif('wilson_solve.gif')

