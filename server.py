from collections import defaultdict

import mesa
from model import Schelling

from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer




def get_happy_agents(model):
    """
    Display a text count of how many happy agents there are.
    """
    return f"Happy agents: {model.happy}"


def schelling_draw(agent):
    """
    Portrayal Method for canvas
    """
    portrayal = {"Filled": "true", "Layer": 0}

    if agent is not None:
        x, y = agent.pos
        cell_type = agent.grid.cell_types[x][y]

        if cell_type == 'residential':
            portrayal["label"] = "residential"
        elif cell_type == 'commercial':
            portrayal["label"] = "commercial"
        elif cell_type == 'industrial':
            portrayal["label"] = "industrial"
        
        portrayal["Shape"] = "circle"
        portrayal["r"] = 0.5
        portrayal["Layer"] = 1

        if agent.type == 0:
            portrayal["Color"] = "#e45e5e"
        elif agent.type == 1:
            portrayal["Color"] = "#ffc04c"
        else:
            portrayal["Color"] = "#4ca64c"

    return portrayal


canvas_element = mesa.visualization.CanvasGrid(schelling_draw, 20, 20, 500, 500)
happy_chart = mesa.visualization.ChartModule([{"Label": "happy", "Color": "Black"}])

# TODO: make height/width variable
model_params = {
    "height": 20,
    "width": 20,
    "density": mesa.visualization.Slider("Agent density", 0.8, 0.1, 1.0, 0.1),
    "chance_high_class": mesa.visualization.Slider("Chance agent is high class", 0.2, 0.00, 1.0, 0.05),
    "chance_middle_class": mesa.visualization.Slider("Chance agent is middle class", 0.4, 0.00, 1.0, 0.05),
    "homophily": mesa.visualization.Slider("Homophily", 3, 0, 8, 1),
    "residential": mesa.visualization.Slider("Fraction residential", 0.4, 0, 1, 0.1),
    "commercial": mesa.visualization.Slider("Fraction commercial", 0.3, 0, 1, 0.1),
    "industrial": mesa.visualization.Slider("Fraction industrial", 0.3, 0, 1, 0.1)
}

server = mesa.visualization.ModularServer(
    Schelling,
    [canvas_element, get_happy_agents, happy_chart],
    "Schelling",
    model_params,
)
