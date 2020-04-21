import {PriorityQueue} from './priority-queue.js';
import {samePositions} from './util.js';

const COLORS = ['red', 'blue', 'green'];

export class Window {

  constructor(grid) {
    this.grid = grid;
    this.slider = document.getElementById('speed-slider');

    this.canvas = document.getElementById('canvas');
    this.canvas.style.width = `${this.grid.w}00px`;
    this.canvas.style.height = `${this.grid.h}00px`;
    this.canvas.width = this.grid.w * 200;
    this.canvas.height = this.grid.h * 200;
    this.ctx = this.canvas.getContext('2d');

    this.render();

    document.getElementById('btn-solve').onclick = function() {
      this.solve();
    }.bind(this);
  }

  render() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    this.renderGrid();
  }

  renderGrid() {
    for (let y = 0; y < this.grid.h; y++) {
      for (let x = 0; x < this.grid.w; x++) {
        this.ctx.fillStyle = this.grid.walls[y][x] ? 'black' : 'white';
        this.ctx.fillRect(x * 200, y * 200, 200, 200);
      }
    }

    for (let agent = 0; agent < this.grid.agents; agent++) {
      const start = this.grid.starts[agent];
      this.renderStart(agent, start[0], start[1]);
      const goal = this.grid.goals[agent];
      this.renderGoal(agent, goal[0], goal[1]);
    }
  }

  renderStart(agent, x, y) {
    const xp = x * 200;
    const yp = y * 200;

    this.ctx.fillStyle = COLORS[agent];

    for (const xOffs of [25, 175]) {
      for (const yOffs of [25, 175]) {
        this.ctx.beginPath();
        this.ctx.arc(xp + xOffs, yp + yOffs, 10, 0, 6.3);
        this.ctx.fill();
        this.ctx.closePath();
      }
    }
  }

  renderGoal(agent, x, y) {
    const xp = x * 200;
    const yp = y * 200;

    this.ctx.strokeStyle = COLORS[agent];
    this.ctx.lineWidth = 10;
    this.ctx.lineCap = 'round';

    this.ctx.beginPath();
    this.ctx.moveTo(xp + 75, yp + 75);
    this.ctx.lineTo(xp + 125, yp + 125);
    this.ctx.stroke();
    this.ctx.closePath();

    this.ctx.beginPath();
    this.ctx.moveTo(xp + 125, yp + 75);
    this.ctx.lineTo(xp + 75, yp + 125);
    this.ctx.stroke();
    this.ctx.closePath();
  }

  renderNode(node) {
    for (let i = 0; i < this.grid.agents; i++) {
      const agent = node.positions[i];
      this.ctx.beginPath();
      this.ctx.arc(agent[0] * 200 + 100, agent[1] * 200 + 100, 50, 0,
          2 * Math.PI);
      this.ctx.fillStyle = COLORS[i];
      this.ctx.fill();
      this.ctx.closePath();
    }

    this.renderParentNode(node.parent, node, true);
  }

  trailGridPosition(agent, position) {
    const angle = Math.PI / this.grid.agents * 2 * agent - Math.PI / 4;
    return [
      position[0] * 200 + 100 + Math.cos(angle) * 25,
      position[1] * 200 + 100 + Math.sin(angle) * 25,
    ];
  }

  renderParentNode(parent, child, first = false) {
    if (parent === undefined) {
      return;
    }

    if (!parent.isStandard) {
      this.renderParentNode(parent.parent, child, first);
      return;
    }

    for (let i = 0; i < this.grid.agents; i++) {
      const agent = this.trailGridPosition(i, parent.positions[i]);
      const agent_child = this.trailGridPosition(i, child.positions[i]);

      if (!first && samePositions(agent, agent_child)) {
        this.ctx.beginPath();
        this.ctx.arc(agent[0], agent[1], 25, 0, 6.3);
        this.ctx.fillStyle = COLORS[i];
        this.ctx.fill();
        this.ctx.closePath();
      } else {
        this.ctx.beginPath();
        this.ctx.moveTo(agent[0], agent[1]);
        this.ctx.lineTo(agent_child[0], agent_child[1]);
        this.ctx.lineWidth = 20;
        this.ctx.lineCap = 'round';
        this.ctx.strokeStyle = COLORS[i];
        this.ctx.stroke();
        this.ctx.closePath();
      }
    }

    this.renderParentNode(parent.parent, parent);
  }

  solve() {
    this.queue = new PriorityQueue((a, b) => a.f < b.f);
    this.queue.enqueue(this.grid.rootNode());
    this.solveNext();
  }

  solveNext() {
    if (this.queue.empty) {
      console.log('No more options, impossible to solve');
      return;
    }

    const node = this.queue.dequeue();
    this.render();
    this.renderNode(node);

    if (node.allAgentsAtGoal) {
      console.log('Done');

      let cnode = node;
      while (cnode !== undefined) {
        if (cnode.isStandard) {
          console.log(cnode.positions);
        }
        cnode = cnode.parent;
      }

      return;
    }

    node.expand().forEach(function(n) {
      this.queue.enqueue(n);
    }.bind(this));

    setTimeout(function() {
      this.solveNext();
    }.bind(this), this.slider.value);
  }

}

