from collections import defaultdict

import mesa
from model import Schelling

from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import Choice


def get_happy_agents(model):
    """
    Display a text count of how many happy agents there are.
    """
    return f"Happy agents: {model.happy}"


def get_total_num_employed_agents(model):
    """
    Display a text count of how many employed agents there are.
    """
    employed_count = len(
        [
            agent
            for agent in model.schedule.agents
            if agent.employment_status == "employed"
        ]
    )
    return f"Employed agents: {employed_count}"


def get_total_num_unemployed_agents(model):
    """
    Display a text count of how many unemployed agents there are.
    """
    unemployed_count = len(
        [
            agent
            for agent in model.schedule.agents
            if agent.employment_status == "unemployed"
        ]
    )
    return f"Unemployed agents: {unemployed_count}"


def get_total_num_low_class_agents(model):
    """
    Display a text count of how many low-class agents there are.
    """
    low_class_count = len([agent for agent in model.schedule.agents if agent.type == 0])
    return f"Low-class agents: {low_class_count}"


def get_total_num_mid_class_agents(model):
    """
    Display a text count of how many middle-class agents there are.
    """
    mid_class_count = len([agent for agent in model.schedule.agents if agent.type == 1])
    return f"Middle-class agents: {mid_class_count}"


def get_total_num_high_class_agents(model):
    """
    Display a text count of how many high-class agents there are.
    """
    high_class_count = len(
        [agent for agent in model.schedule.agents if agent.type == 2]
    )
    return f"High-class agents: {high_class_count}"


def schelling_draw(agent):
    """
    Portrayal Method for canvas
    """
    portrayal = {"Filled": "true", "Layer": 0}

    if agent is not None:
        if agent.pos is not None:
            x, y = agent.pos
            cell_type = agent.grid.cell_types[x][y]

            if cell_type == "residential":
                portrayal["label"] = "residential"
                portrayal["Shape"] = "circle"
                portrayal["r"] = 0.5
            elif cell_type == "commercial":
                portrayal["label"] = "commercial"
                portrayal["Shape"] = "rect"
                portrayal["w"] = 1
                portrayal["h"] = 1
            elif cell_type == "industrial":
                portrayal["label"] = "industrial"
                portrayal["Shape"] = "rect"
                portrayal["w"] = 0.5
                portrayal["h"] = 0.1
            portrayal["Layer"] = 1

            if agent.type == 0:
                portrayal["Color"] = "#e45e5e"
            elif agent.type == 1:
                portrayal["Color"] = "#ffc04c"
            elif agent.type == 4:
                portrayal["Color"] = "black"
            else:
                portrayal["Color"] = "#4ca64c"

            if "label" in portrayal:
                portrayal["label"] += f"\nemployment:{agent.employment_status}"
                portrayal["label"] += f"\nage:{agent.age}"
            else:
                portrayal["label"] = "Empty cell"

    return portrayal


canvas_element = mesa.visualization.CanvasGrid(schelling_draw, 20, 20, 500, 500)
happy_chart = mesa.visualization.ChartModule([{"Label": "happy", "Color": "Black"}])

# TODO: make height/width variable
model_params = {
    "grid_init": Choice(
        "Grid Initialization",
        value="Random",
        choices=["Random", "Clustered"],
    ),
    "height": 20,
    "width": 20,
    "density": mesa.visualization.Slider("Agent density", 0.8, 0.1, 1.0, 0.1),
    "chance_high_class": mesa.visualization.Slider(
        "Chance agent is high class", 0.2, 0.00, 1.0, 0.05
    ),
    "chance_middle_class": mesa.visualization.Slider(
        "Chance agent is middle class", 0.4, 0.00, 1.0, 0.05
    ),
    "homophily": mesa.visualization.Slider("Homophily", 3, 0, 8, 1),
    "residential": mesa.visualization.Slider("Fraction residential", 0.4, 0, 1, 0.1),
    "commercial": mesa.visualization.Slider("Fraction commercial", 0.3, 0, 1, 0.1),
    "industrial": mesa.visualization.Slider("Fraction industrial", 0.3, 0, 1, 0.1),
}

server = mesa.visualization.ModularServer(
    Schelling,
    [
        canvas_element,
        get_happy_agents,
        get_total_num_employed_agents,
        get_total_num_unemployed_agents,
        get_total_num_low_class_agents,
        get_total_num_mid_class_agents,
        get_total_num_high_class_agents,
        happy_chart,
    ],
    "Schelling",
    model_params,
)
