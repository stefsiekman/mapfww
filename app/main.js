import {Window} from './window.js';
import {Grid} from './grid.js';

document.getElementById('example-simple').onclick = () => {
  const grid = new Grid(5, 3);
  grid.addWall(0, 1);
  grid.addWall(4, 1);
  grid.addAgent([0, 0], [0, 2]);
  grid.addAgent([4, 2], [4, 0]);

  new Window(grid, 100);
};

document.getElementById('example-corridor').onclick = () => {
  const grid = new Grid(5, 4);
  grid.addWall(0, 1);
  grid.addWall(1, 1);
  grid.addWall(1, 2);
  grid.addWall(3, 1);
  grid.addWall(4, 1);
  grid.addWall(3, 3);
  grid.addWall(4, 3);
  grid.addAgent([0, 0], [0, 2]);
  grid.addAgent([4, 0], [4, 2]);

  new Window(grid, 100);
};

document.getElementById('example-three').onclick = () => {
  const grid = new Grid(5, 5);
  grid.addWall(0, 2);
  grid.addWall(2, 2);
  grid.addWall(1, 0);
  grid.addWall(3, 0);
  grid.addWall(1, 4);
  grid.addWall(3, 4);
  grid.addAgent([0, 0], [0, 4]);
  grid.addAgent([4, 4], [4, 0]);
  grid.addAgent([2, 4], [2, 0]);

  new Window(grid, 100);
};

document.getElementById('example-narrow-two').onclick = () => {
  const grid = new Grid(3, 5);
  grid.addWall(1, 2);
  grid.addWall(1, 0);
  grid.addWall(2, 2);
  grid.addWall(1, 4);
  grid.addAgent([2, 4], [2, 0]);
  grid.addAgent([0, 4], [0, 0]);

  new Window(grid, 100);
};

document.getElementById('example-narrow').onclick = () => {
  const grid = new Grid(5, 5);
  grid.addWall(0, 2);
  grid.addWall(3, 2);
  grid.addWall(4, 2);
  grid.addWall(1, 0);
  grid.addWall(3, 0);
  grid.addWall(1, 4);
  grid.addWall(3, 4);
  grid.addAgent([0, 0], [0, 4]);
  grid.addAgent([4, 4], [4, 0]);
  grid.addAgent([2, 4], [2, 0]);

  new Window(grid, 100);
};
