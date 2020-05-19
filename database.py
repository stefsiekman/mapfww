import json
import sqlite3
from multiprocessing import Lock

from grid import Grid
from progressive import save_generate_grid


class Database:
    """
    Multiprocessing-safe access to the runs database.
    """

    def __init__(self):
        self.lock = Lock()
        self.conn = sqlite3.connect("runs.sqlite")
        self.conn.executescript(open("db_schema.sql", "r").read())
        self.conn.commit()

    def _get_identifying_id(self, table: str, col: str, value: str) -> id:
        self.lock.acquire()
        computer = self.conn.execute(f"SELECT id FROM {table} WHERE {col}=?",
                                     (value,)).fetchone()
        if computer is not None:
            self.lock.release()
            return computer[0]

        cur = self.conn.cursor()
        cur.execute(f"INSERT INTO {table} ({col}) VALUES (?)", (value,))
        computer_id = cur.lastrowid
        cur.close()
        self.conn.commit()

        self.lock.release()

        return computer_id

    def get_computer_id(self, name: str) -> int:
        return self._get_identifying_id("computers", "name", name)

    def get_version_id(self, hex: str) -> int:
        return self._get_identifying_id("versions", "hex", hex)

    def _create_run(self, data):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO runs "
                    "(version_id, grid_id, computer_id, thread, time_limit) "
                    "VALUES (?,?,?,?,?)", data)
        run_id = cur.lastrowid
        cur.close()
        self.conn.commit()

        return run_id

    def get_grid(self, version_id, computer_id, thread, time_limit, agents,
                 waypoints, size, infill):
        """
        Tries to find an existing grid to test on with the given parameters,
        that this version has not yet ran on. If such version does not exist,
        a new grid will be created.

        Creates a new run entry, of which the ID will be returned.
        """

        self.lock.acquire()

        grid_row = self.conn.execute("SELECT g.id, data FROM grids g "
                                     "LEFT OUTER JOIN runs r "
                                     "ON r.grid_id = g.id AND version_id = ? "
                                     "AND computer_id = ? "
                                     "WHERE "
                                     "(r.grid_id IS NULL OR r.finished = 0)"
                                     "AND g.width=? AND g.height = ? "
                                     "AND g.infill = ? AND g.agents = ? "
                                     "AND g.waypoints = ? "
                                     "LIMIT 1",
                                     (version_id, computer_id, size, size,
                                      infill, agents, waypoints)).fetchone()

        if grid_row is not None:
            # Generate grid instance...
            grid = Grid(size, size)
            grid_data = json.loads(grid_row[1])
            self.lock.release()
            return self._create_run((version_id, grid_row[0], computer_id,
                                     thread, time_limit)), grid_data

        # Create brand new instance
        grid = save_generate_grid(agents, waypoints, size)
        grid_data = {
            "width": grid.w,
            "height": grid.h,
            "starts": grid.starts,
            "goals": grid.goals,
            "waypoints": [list(map.waypoints) for map in grid.waypoints],
            "walls": grid.walls,
        }

        cur = self.conn.cursor()
        cur.execute("INSERT INTO grids "
                    "(width, height, agents, waypoints, infill, data)"
                    " VALUES (?,?,?,?,?,?)", (size, size, agents, waypoints,
                                              infill, json.dumps(grid_data)))
        grid_id = cur.lastrowid
        cur.close()
        self.conn.commit()
        self.lock.release()

        return self._create_run((version_id, grid_id, computer_id,
                                 thread, time_limit)), grid_data

    def complete_run(self, run_id, time):
        self.lock.acquire()
        self.conn.execute("UPDATE runs SET runtime = ?, finished = 1 "
                          "WHERE id = ?",
                          (time, run_id))
        self.conn.commit()
        self.lock.release()

    def grid_info(self, run_id):
        self.lock.acquire()
        row = self.conn.execute("SELECT width, height, agents, waypoints, "
                                "infill FROM grids g "
                                "JOIN runs r ON r.grid_id = g.id "
                                "WHERE r.id = ?", (run_id,))
        self.lock.release()

        width, height, agents, waypoints, infill = row

        return f"Grid({width}x{height} {infill}% {agents}A {waypoints}W)"
