"""CSC111 Winter 2025 Exercise 3-4 (Graphs Visualization)

Module Description
==================

This module contains some Python functions that you can use to visualize the graphs
you're working with on this assignment. You should not modify anything in this file.
It will not be submitted for grading.

Disclaimer: we didn't have time to make this file fully PythonTA-compliant!

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students
taking CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright for CSC111 materials,
please consult our Course Syllabus.

This file is Copyright (c) 2025 Mario Badr, David Liu, and Isaac Waller.
"""
# import os
import networkx as nx
from plotly.graph_objs import Scatter, Figure

import proj2functions

# Colours to use when visualizing different clusters.
COLOUR_SCHEME = [
    '#2E91E5', '#E15F99', '#1CA71C', '#FB0D0D', '#DA16FF', '#222A2A', '#B68100',
    '#750D86', '#EB663B', '#511CFB', '#00A08B', '#FB00D1', '#FC0080', '#B2828D',
    '#6C7C32', '#778AAE', '#862A16', '#A777F1', '#620042', '#1616A7', '#DA60CA',
    '#6C4516', '#0D2A63', '#AF0038'
]

LINE_COLOUR = 'rgb(210,210,210)'
VERTEX_BORDER_COLOUR = 'rgb(50, 50, 50)'
RECIPE_COLOUR = 'rgb(89, 205, 105)'
HIGHLIGHT_COLOUR = 'rgb(255, 215, 0)'
INGREDIENT_COLOUR = 'rgb(105, 89, 205)'
PICKED_INGREDIENT_COLOUR = 'rgb(255, 215, 0)'


def visualize_graph(graph: proj2functions.Graph,
                    layout: str = 'spring_layout',
                    max_vertices: int = 5000,
                    output_file: str = '',
                    highlight_ingredients: list[str] = None) -> None:
    """Visualize the given graph using Plotly and NetworkX."""
    graph_nx = graph.to_networkx(max_vertices)

    # Prepare node data
    for node in graph_nx.nodes:
        vertex = graph.get_item(node)
        if vertex:
            graph_nx.nodes[node]['price'] = vertex.price
            if vertex.kind == 'recipe':
                ingredients = vertex.v_cleaned_ingredients
                graph_nx.nodes[node]['ingredients'] = ", ".join(ingredients) if ingredients else 'N/A'
            else:
                graph_nx.nodes[node]['ingredients'] = 'N/A'
        else:
            graph_nx.nodes[node]['price'] = 'N/A'
            graph_nx.nodes[node]['ingredients'] = 'N/A'

    pos = getattr(nx, layout)(graph_nx)

    # Prepare data for plotting
    x_values = [pos[k][0] for k in graph_nx.nodes]
    y_values = [pos[k][1] for k in graph_nx.nodes]
    kinds = [graph_nx.nodes[k]['kind'] for k in graph_nx.nodes]

    colours = [
        PICKED_INGREDIENT_COLOUR if (kind == 'ingredient' and highlight_ingredients and n in highlight_ingredients)
        else (RECIPE_COLOUR if kind == 'recipe' else INGREDIENT_COLOUR)
        for n, kind in zip(graph_nx.nodes, kinds)
    ]

    x_edges = []
    y_edges = []
    for edge in graph_nx.edges:
        x_edges += [pos[edge[0]][0], pos[edge[1]][0], None]
        y_edges += [pos[edge[0]][1], pos[edge[1]][1], None]

    trace3 = Scatter(x=x_edges,
                     y=y_edges,
                     mode='lines',
                     name='edges',
                     line={"color": LINE_COLOUR, "width": 1},
                     hoverinfo='none',
                     )

    trace4 = Scatter(x=x_values,
                     y=y_values,
                     mode='markers',
                     name='nodes',
                     marker={"symbol": 'circle-dot', "size": [20 if kind == 'recipe' else 5 for kind in kinds],
                             "color": colours, "line": {"color": VERTEX_BORDER_COLOUR, "width": 0.5}},
                     text=[f"{k}<br>Price: ${round(graph_nx.nodes[k].get('price', 0), 2):.2f}<br>"
                           f"Ingredients: {graph_nx.nodes[k].get('ingredients', 'N/A')}"
                           for k in graph_nx.nodes],
                     hovertemplate='%{text}',
                     hoverlabel={'namelength': 0}
                     )

    fig = Figure(data=[trace3, trace4])
    fig.update_layout(
        title="Saving Starving Students!",
        showlegend=True,
        legend={"title": 'Node Types', "itemsizing": 'constant', "font": {"size": 12}, "x": 0.01, "y": 0.99},
        legend_traceorder='normal',
    )

    trace_recipe = Scatter(
        x=[None], y=[None], mode='markers', name='Recipes',
        marker={"color": RECIPE_COLOUR, "size": 10, "symbol": 'circle-dot'}
    )

    trace_ingredient = Scatter(
        x=[None], y=[None], mode='markers', name='Ingredients',
        marker={"color": INGREDIENT_COLOUR, "size": 10, "symbol": 'circle-dot'}
    )

    trace_picked_ingredient = Scatter(
        x=[None], y=[None], mode='markers', name='Picked Ingredients',
        marker={"color": PICKED_INGREDIENT_COLOUR, "size": 10, "symbol": 'circle-dot'}
    )

    fig.add_trace(trace_recipe)
    fig.add_trace(trace_ingredient)
    fig.add_trace(trace_picked_ingredient)

    fig.update_xaxes(showgrid=False, zeroline=False, visible=False)
    fig.update_yaxes(showgrid=False, zeroline=False, visible=False)

    if output_file == '':
        fig.show()
    else:
        fig.write_image(output_file)

