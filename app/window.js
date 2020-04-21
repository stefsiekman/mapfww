const COLORS = ['red', 'blue', 'green'];

export class Window {

  constructor(grid) {
    this.grid = grid;

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

    this.ctx.beginPath();
    this.ctx.moveTo(xp + 125, yp + 75);
    this.ctx.lineTo(xp + 75, yp + 125);
    this.ctx.stroke();
  }

  renderNode(node) {
    for (const agent of node.positions) {
      this.ctx.beginPath();
      this.ctx.arc(agent[0] * 200 + 100, agent[1] * 200 + 100, 50, 0,
          2 * Math.PI);
      this.ctx.fillStyle = 'red';
      this.ctx.fill();
    }
  }

  solve() {
    this.renderNode(this.grid.rootNode());
  }

}

