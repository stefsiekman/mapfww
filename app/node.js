import {samePositions} from './util.js';
import {PriorityQueue} from './priority-queue.js';

export class Node {

  constructor(grid, positions, moves, cost, taken_edges, parent = undefined) {
    this.grid = grid;
    this.positions = positions;
    this.moves = moves;
    this.cost = cost;
    this.taken_egdes = taken_edges;
    this.parent = parent;

    // Make node standard
    if (!this.moves.includes(undefined)) {
      this.moves = Array(this.positions.length).fill(undefined);
      this.positions = moves;
      this.taken_egdes = [];
    }

    this.post_moves = this.moves.map(
        (e, i) => e !== undefined ? e : this.positions[i]);

    // Sum the heuristic values of the agents
    this.heuristic = this.post_moves.map((e, i) => this.grid.heuristic(i, e)).
        reduce((a, b) => a + b);
  }

  get f() {
    return this.cost + this.heuristic;
  }

  get isStandard() {
    return this.moves.every((move) => move === undefined);
  }

  get allAgentsAtGoal() {
    return this.positions.every(
        (position, agent) => samePositions(position, this.grid.goals[agent]));
  }

  generateEdge(from, to) {
    const fromIndex = from[0] + from[1] * this.grid.w;
    const toIndex = to[0] + to[1] * this.grid.w;

    return [Math.min(fromIndex, toIndex), Math.max(fromIndex, toIndex)];
  }

  isEdgeTaken(from, to) {
    const testEdge = this.generateEdge(from, to);
    return this.taken_egdes.some((edge) => samePositions(edge, testEdge));
  }

  expand() {
    console.assert(this.moves.includes(undefined),
        'Node converted to standard before expansion');

    const agent = this.moves.indexOf(undefined);
    const position = this.positions[agent];

    const new_nodes = [];

    for (const neighbour of this.grid.validNeighbours(position)) {
      // Check if cell is occupied by moved agent
      if (this.moves.some((move) => samePositions(move, neighbour))) {
        continue;
      }

      // Check for crossing edges
      if (this.isEdgeTaken(position, neighbour)) {
        continue;
      }

      const new_moves = this.moves.slice();
      new_moves[agent] = neighbour;
      const new_taken_edges = this.taken_egdes.slice();
      new_taken_edges.push(this.generateEdge(position, neighbour));

      new_nodes.push(
          new Node(this.grid, this.positions, new_moves, this.cost + 1,
              new_taken_edges, this));
    }

    return new_nodes;
  }

}