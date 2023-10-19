import numpy as np

import mesa


class SchellingAgent(mesa.Agent):
    def __init__(
        self,
        pos,
        model,
        agent_type,
        grid,
        homophily,
        age=0,
        employment_status="employed",
        name=None,
    ):
        super().__init__(pos, model)
        self.pos = pos
        self.type = agent_type  # 0: low class, 1: middle class, 2: high class
        self.age = age
        self.name = name
        self.employment_status = employment_status  # 'employed' or 'unemployed'
        self.happiness_index = 0
        self.steps_unemployed = 0  # To keep track of unemployment duration
        self.grid = grid
        self.homophily = homophily
        self.max_unemployed_period_low_class = 5
        self.max_unemployed_period_middle_class = 10
        self.max_unemployed_period_high_class = 15
        self.probability_fired = 0.053 # Probability of getting fired in NYC 2023

    def calculate_happiness(self):
        self.happiness_index = 0  # Reset happiness index
        x, y = self.pos
        cell_type = self.model.grid.cell_types[x][y]

        # Class conditions
        if self.type == 0:
            for neighbor in self.model.grid.iter_neighbors(self.pos, True):
                self.happiness_index += self.homophily
            if cell_type == ["residential", "commercial"]:
                self.happiness_index += 2
        elif self.type == 1:
            for neighbor in self.model.grid.iter_neighbors(self.pos, True):
                self.happiness_index += self.homophily
            if cell_type == "industry":
                self.happiness_index -= 1
            else:
                self.happiness_index += 2
        elif self.type == 2:  # High class
            for neighbor in self.model.grid.iter_neighbors(self.pos, True):
                if neighbor.type == 2:
                    self.happiness_index += self.homophily
                if neighbor.type == 0:
                    self.happiness_index -= self.homophily
            if cell_type == "industry":
                self.happiness_index -= 5
            elif cell_type == ["residential"]:
                self.happiness_index += 2

        # elif self.employment_status == "unemployed":
        #     self.steps_unemployed += 1
        #     if self.type == 0:  # Low class
        #         if self.steps_unemployed > self.max_unemployed_period_low_class:
        #             self.model.grid.remove_agent(self)
        #             self.model.schedule.remove(self)
        #         else:
        #             if cell_type == "industry":
        #                 self.happiness_index += 10
        #     elif self.type == 1:  # Middle class
        #         if self.steps_unemployed > self.max_unemployed_period_middle_class:
        #             self.type = 0  # Descent to low class
        #     elif self.type == 2:  # High class
        #         if self.steps_unemployed > self.max_unemployed_period_high_class:
        #             self.type = 1  # Descent to middle class

        # Age-based conditions
        # if int(self.age) < 29:
        #     if cell_type == "commerce":
        #         self.happiness_index += 1
        # elif int(self.age) > 29 and self.type == 1:  # Middle class and older than 29
        #     for neighbor in self.model.grid.iter_neighbors(self.pos, True):
        #         if neighbor.type == 2:
        #             self.happiness_index += self.homophily # Bonus for being around higher class
        # elif int(self.age) > 64:
        #     # Doesn't change social class, just looks at neighbors (basic Schelling model)
        #     for neighbor in self.model.grid.iter_neighbors(self.pos, True):
        #         if neighbor.type == self.type:
        #             self.happiness_index += self.homophily

    def step(self):
        self.calculate_happiness()  # Calculate the new happiness index based on various factors

        if self.happiness_index < self.model.happiness_threshold:
            self.model.grid.move_to_empty(self)
        else:
            self.model.happy += 1  # Increment the total number of "happy" agents

        # INTERACT! Turn ON/OFF for employment/unemployment to play a roll
        # if self.employment_status == 'employed':
        #     if self.random.random() < self.probability_fired:
        #         self.employment_status = 'unemployed'
        # else:
        #     # TODO: change this by class
        #     if self.random.random() < 0.30:
        #         self.employment_status = 'employed'



class EconClassGrid(mesa.space.SingleGrid):
    def __init__(self, width, height, torus, residential, commercial, industrial):
        super().__init__(width, height, torus)
        self.cell_types = np.empty((width, height), dtype=object)

        total_cells = width * height
        num_residential = int(total_cells * residential)
        num_commercial = int(total_cells * commercial)
        num_industrial = int(total_cells * industrial)

        # Create a list with the right number of each type
        all_types = (
            ["residential"] * num_residential
            + ["commercial"] * num_commercial
            + ["industrial"] * num_industrial
        )

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

    def __init__(
        self,
        width=20,
        height=20,
        density=0.8,
        chance_high_class=0.2,
        chance_middle_class=0.6,
        homophily=3,
        residential=0.4,
        commercial=0.3,
        industrial=0.3,
        happiness_threshold=10,
    ):
        self.width = width
        self.height = height
        self.density = density
        self.chance_high_class = chance_high_class
        self.chance_middle_class = chance_middle_class
        self.homophily = homophily
        self.happiness_threshold = happiness_threshold

        self.schedule = mesa.time.RandomActivation(self)
        self.grid = EconClassGrid(
            width,
            height,
            torus=True,
            residential=residential,
            commercial=commercial,
            industrial=industrial,
        )

        self.happy = 0
        self.datacollector = mesa.DataCollector(
            {"happy": "happy"},  # Model-level count of happy agents
            # For testing purposes, agent's individual x and y
            {"x": lambda a: a.pos[0], "y": lambda a: a.pos[1]},
        )
        agent_name = 0

        for cell in self.grid.coord_iter():
            x, y = cell[1]

            # assign class
            if self.random.random() < self.density:
                if self.random.random() < self.chance_high_class:
                    agent_type = 2
                else:
                    if self.random.random() < self.chance_middle_class:
                        agent_type = 1
                    else:
                        agent_type = 0

                agent = SchellingAgent(
                    (x, y), self, agent_type, self.grid, homophily=self.homophily, name=agent_name
                )
                agent_name += 1
                self.grid.place_agent(agent, (x, y))
                self.schedule.add(agent)

                # assign age
                # Define the age groups and their corresponding probabilities. Data for NYC 2023
                age_groups = ['24', '34', '44', '54', '59', '64', '74', '84', '85']
                probabilities = [0.0872, 0.2032, 0.1622, 0.1482, 0.0874, 0.0832, 0.1112, 0.0722, 0.0452]

                agent.age = np.random.choice(age_groups, p=probabilities)


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
