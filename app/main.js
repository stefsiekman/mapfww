import {Window} from './window.js';
import {Grid} from './grid.js';

const grid = new Grid(5, 3);
grid.addWall(0, 1);
grid.addWall(1, 1);
grid.addWall(3, 1);
grid.addWall(4, 1);
grid.addAgent([0, 0], [0, 2]);
grid.addAgent([4, 2], [4, 0]);

const window = new Window(grid);