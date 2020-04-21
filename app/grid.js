import {Node} from './node.js';

export class Grid {

  constructor(width, height) {
    this.w = width;
    this.h = height;

    // Grid of booleans for wall present or not [y][x]
    this.walls = this.emptyGrid(false);

    this.agents = 0;
    this.starts = [];
    this.goals = [];
    this.heuristics = [];
  }

  rootNode() {
    return new Node(this, this.starts, Array(this.agents).fill(undefined), 0,
        []);
  }

  emptyGrid(defaultValue) {
    return Array.from(Array(this.h),
        (e, i) => Array(this.w).fill(defaultValue));
  }

  addWall(x, y) {
    console.assert(this.agents === 0, 'Add agents after walls');
    console.assert(!this.walls[y][x], 'Place wall on non-wall');

    this.walls[y][x] = true;
  }

  addAgent(start, goal) {
    this.agents++;
    this.starts.push(start);
    this.goals.push(goal);
    this.heuristics.push(this.backtrackHeuristics(goal));
  }

  validNeighbours(position) {
    const neighbours = [];

    for (let xOffs of [-1, 0, 1]) {
      for (let yOffs of [-1, 0, 1]) {
        // Only non-diagonal
        if (xOffs !== 0 && yOffs !== 0) {
          continue;
        }

        const x = position[0] + xOffs;
        const y = position[1] + yOffs;

        if (x < 0 || x >= this.w) {
          continue;
        }
        if (y < 0 || y >= this.h) {
          continue;
        }

        if (!this.walls[y][x]) {
          neighbours.push([x, y]);
        }
      }
    }

    return neighbours;
  }

  backtrackHeuristics(from_pos) {
    const queue = [];
    const visited = this.emptyGrid(false);
    const heuristics = this.emptyGrid(undefined);

    queue.push([from_pos, 0]);

    while (queue.length > 0) {
      const item = queue.shift();
      const position = item[0];
      const x = position[0];
      const y = position[1];
      const heuristic = item[1];

      visited[y][x] = true;

      // Is this the most efficient path?
      if (heuristics[y][x] !== undefined && heuristic >= heuristics[y][x]) {
        continue;
      }

      heuristics[y][x] = heuristic;

      for (let neighbour of this.validNeighbours(position)) {
        if (!visited[neighbour[1]][neighbour[0]]) {
          queue.push([neighbour, heuristic + 1]);
        }
      }
    }

    return heuristics;
  }

  heuristic(agent, position) {
    return this.heuristics[agent][position[1]][position[0]];
  }

}