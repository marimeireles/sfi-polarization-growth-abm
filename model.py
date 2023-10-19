import numpy as np

import mesa

class SchellingAgent(mesa.Agent):
    """
    Schelling segregation agent
    """

    def __init__(self, pos, model, agent_type, age=0):
        """
        Create a new Schelling agent.

        Args:
           unique_id: Unique identifier for the agent.
           x, y: Agent initial location.
           agent_type: Indicator for the agent's class.
           age: Agent's age.
        """
        super().__init__(pos, model)
        self.pos = pos
        self.type = agent_type
        self.age = age

    def step(self):
        similar = 0
        for neighbor in self.model.grid.iter_neighbors(self.pos, True):
            # print(f"neighbor.type: {neighbor.type}, self.type: ")
            if neighbor.type == self.type:
                similar += 1

        # If unhappy, move:
        if similar < self.model.homophily:
            self.model.grid.move_to_empty(self)
        else:
            self.model.happy += 1

class EconClassGrid(mesa.space.SingleGrid):
    def __init__(self, width, height, torus, residential, commercial, industrial):
        super().__init__(width, height, torus)
        self.cell_types = np.empty((width, height), dtype=object)
        
        total_cells = width * height
        num_residential = int(total_cells * residential)
        num_commercial = int(total_cells * commercial)
        num_industrial = int(total_cells * industrial)

        # Create a list with the right number of each type
        all_types = ['residential'] * num_residential + ['commercial'] * num_commercial + ['industrial'] * num_industrial

        # Fill in the rest with the last type to make sure the list length is correct
        all_types += ['industrial'] * (total_cells - len(all_types))

        # Shuffle the list to randomize
        np.random.shuffle(all_types)

        # Fill in the grid
        i = 0
        for x in range(width):
            for y in range(height):
                self.cell_types[x, y] = all_types[i]
                i += 1



class Schelling(mesa.Model):
    """
    Model class for the Schelling segregation model.
    """

    def __init__(self, width=20, height=20, density=0.8, minority_pc=0.2, homophily=3, residential=0.4, commercial=0.3, industrial=0.3):
        """ """
        self.width = width
        self.height = height
        self.density = density
        self.minority_pc = minority_pc
        self.homophily = homophily

        self.schedule = mesa.time.RandomActivation(self)
        self.grid = EconClassGrid(width, height, torus=True, residential=residential, commercial=commercial, industrial=industrial)

        self.happy = 0
        self.datacollector = mesa.DataCollector(
            {"happy": "happy"},  # Model-level count of happy agents
            # For testing purposes, agent's individual x and y
            {"x": lambda a: a.pos[0], "y": lambda a: a.pos[1]},
        )

        # Set up agents
        # We use a grid iterator that returns
        # the coordinates of a cell as well as
        # its contents. (coord_iter)
        for cell in self.grid.coord_iter():
            x, y = cell[1]
            if self.random.random() < self.density:
                if self.random.random() < 0.1:  # 10% chance for high class
                    agent_type = 2
                elif self.random.random() < self.minority_pc:
                    agent_type = 1
                else:
                    agent_type = 0
                
                agent = SchellingAgent((x, y), self, agent_type)
                self.grid.place_agent(agent, (x, y))
                self.schedule.add(agent)

    def step(self):
        """
        Run one step of the model. If All agents are happy, halt the model.
        """
        self.happy = 0  # Reset counter of happy agents
        self.schedule.step()
        # collect data
        self.datacollector.collect(self)

        if self.happy == self.schedule.get_agent_count():
            self.running = False
