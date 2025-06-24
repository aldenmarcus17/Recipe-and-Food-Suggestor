"""The helper functions for project 2"""
from __future__ import annotations
import csv
from dataclasses import dataclass
from typing import Any, Optional
import networkx as nx
import pandas as pd
import os
import doctest


class Recipe:
    """A class representing a recipe. This class is used to store and manage information about a recipe

    Instance Attributes:
        - title: The title of the recipe.
        - title_lower: The title of the recipe in lower case.
        - full_ingredients: A list of ingredients used in the recipe (in the original, uncleaned format).
        - instructions: A string containing the recipe's cooking instructions.
        - image_name: The name of the image file representing the recipe.
        - cleaned_ingredients: A list of ingredients that have been processed or cleaned (e.g., for easier matching).
        - price: A float representing the total price of the ingredients in the recipe

    Representation Invariants:
        - self.title != ""
        - self.title_lower != ""
        - self.full_ingredients != []
        - self.instructions != ""
        - self.image != ""
        - self.cleaned_ingredients != []
    """
    title: str
    full_ingredients: list
    instructions: str
    image_name: str
    cleaned_ingredients: list
    price: float

    def __init__(self, cleaned_recipe: list) -> None:
        """Initialize a Recipe object with the given cleaned recipe data."""
        self.title = cleaned_recipe[0]
        self.full_ingredients = cleaned_recipe[1]
        self.instructions = cleaned_recipe[2]
        self.image_name = cleaned_recipe[3]
        self.cleaned_ingredients = cleaned_recipe[5]
        self.price = cleaned_recipe[6]


def get_food(ingredients: str) -> list:
    """Return a list with all possible ingredients from the ingredients file.

    Preconditions:
        - ingredients is a csv file with ingredients inside of it
    """
    foods = []
    with open(ingredients, 'r', encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            foods.append(row[0].lower())

    return foods


def cleancsv(uncleaned: str, ingredients: str, prices: dict) -> list:  # cleans the csv file
    """Return a cleaned and processed list given CSV files. This function extracts and filters recipe data."""

    foods = []
    cleaned_csv = []
    with open(ingredients, 'r', encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            foods.append(row[0].lower())

    with open(uncleaned, 'r', encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            recipeprice = 0
            lst = []
            include = True

            for i in range(1, 6):
                if i == 2:
                    str_list = row[i].strip("[]").split("', ")
                    to_list = [items.strip("'\"") for items in str_list]
                    lst.append(to_list)
                else:
                    lst.append(row[i])
            ingredients = get_ingredients(foods, lst[1])

            for item in ingredients:
                if prices[item] == '':
                    include = False
                    break
                recipeprice += prices[item]

            if include:
                lst.append(ingredients)
                lst.append(round(recipeprice, 2))
                cleaned_csv.append(lst)
    return cleaned_csv


def to_recipe_class(cleaned_csv: list) -> list:  # takes the cleaned_csv and adds each element to the Recipe class
    """Return a list of Recipe objects from cleaned recipe csv"""
    recipes = []
    for i in range(1, len(cleaned_csv)):
        recipe = Recipe(cleaned_csv[i])
        recipes.append(recipe)
    return recipes


def get_ingredients(foods: list, uncleaned_foods: list) -> list:
    """Return a cleaned list of ingredients from a list of unprocessed ingredient descriptions.
    This function takes in food (a list of ingredient names) and uncleaned_foods (a list of uncleaned
    instructions from a recipe). It processes each the words, and returns a cleaned version of ingredients

    >>> foods = ['potato', 'egg', 'salt']
    >>> lst = ['2 large egg whites', '1 pound new potatoes (about 1 inch in diameter)', '2 teaspoons kosher salt']
    >>> get_ingredients(foods, lst)
    ['egg', 'potato', 'salt']
    """
    cleaned_ingredients = []

    for x in uncleaned_foods:
        words = x.split()  # get words into a list
        for f in words:
            cleaned_word = ''.join(c for c in f if c.isalpha())  # make sure its only letters
            if cleaned_word:
                cleaned_word = singularize(cleaned_word)  # make sure it's not empty
                if cleaned_word in foods and cleaned_word not in cleaned_ingredients:
                    cleaned_ingredients.append(cleaned_word)

    return cleaned_ingredients


def singularize(word: str) -> str:
    """Return the singular form of word
    >>> singularize("berries")
    'berry'
    >>> singularize("leaves")
    'leaf'
    >>> singularize("dishes")
    'dish'
    >>> singularize("cars")
    'car'
    """
    if word.endswith("ies"):
        return word[:-3] + "y"  # changes "ies" to "y"
    elif word.endswith("ves"):
        return word[:-3] + "f"  # changes "ves" to "f"
    elif word.endswith("es"):
        return word[:-2]
    elif word.endswith("s") and not (word.endswith("ss") or word.endswith("us") or word.endswith("is")):
        return word[:-1]  # removes the final "s"
    return word


def pricestodict(prices: str) -> dict:
    """takes the ingredient_prices csv and turns it into a dictionary

    Preconditions:
        - prices must be a csv with names of ingredients and it's corresponding price
    """
    foodprices = {}

    with open(prices, 'r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            if row[1] != '':
                foodprices[row[0].lower()] = float(row[1])
            else:
                foodprices[row[0].lower()] = row[1]

    return foodprices


def reviews_to_dict() -> dict[str: float]:
    """Takes the review csv and outputs a dictionary that gives it's average rating score per each recipe"""
    reviewdictlong = {}
    reviews = 'reviews.csv'

    with open(reviews, 'r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            if row[0] not in reviewdictlong:
                reviewdictlong[row[0]] = [float(row[1]), 1]
            else:
                reviewdictlong[row[0]][0] += float(row[1])
                reviewdictlong[row[0]][1] += 1

    reviewdict = {item: reviewdictlong[item][0] / reviewdictlong[item][1] for item in reviewdictlong}
    return reviewdict


class _Vertex:
    """A vertex in a recipe graph, representing either a recipe or an ingredient.

    Each vertex is either a recipe or an ingredient, where:
    - A recipe vertex stores a list of its cleaned ingredients.
    - An ingredient vertex does not store a list of ingredients.

    Instance Attributes:
    - item: The data stored in this vertex, representing a recipe or ingredient.
    - kind: The type of this vertex: 'ingredient' or 'recipe'.
    - details: The recipe object corresponding to this vertex, or None
    - v_cleaned_ingredients: a list containing ingredients of the given recipe.
                             If kind is 'ingredient', this will be None.
    - price: A float representing the price of this vertex
    - neighbours: The vertices that are adjacent to this vertex.

    Representation Invariants:
        - self.item != ""
        - self.kind != ""
        - self.price >= 0.0
        - (self.kind == 'recipe') is (self.details is not None)

    Preconditions:
        - self not in self.neighbours
        - all(self in u.neighbours for u in self.neighbours)
        - kind in {'recipe', 'ingredient'}
    """
    item: str
    kind: str
    details: Optional[Recipe]
    v_cleaned_ingredients: Optional[list[str]]
    price: float
    neighbours: set[_Vertex]

    def __repr__(self):
        """Return a string representation of the _Vertex instance."""
        return f"_Vertex({self.item}, kind={self.kind})"

    def __init__(self, item: str, details: Optional[Recipe],
                 v_cleaned_ingredients: Optional[list[str]], kind: str, price: float) -> None:
        """Initialize a new vertex with the given item, kind, and cleaned ingredients.

        Each vertex is either a recipe or ingredient.

        This vertex is initialized with no neighbours.

        Preconditions:
            - kind in {'recipe', 'ingredient'}
        """
        self.item = item
        self.kind = kind
        self.details = details
        self.v_cleaned_ingredients = v_cleaned_ingredients
        self.price = price
        self.neighbours = set()

    def depth(self) -> int:
        """Returns depth of the vertex

        >>> v1 = _Vertex('v1', None, [], 'ingredient', 0)
        >>> v2 = _Vertex('v2', None, [], 'ingredient', 0)
        >>> v1.neighbours.add(v2)
        >>> v1.depth()
        1
        """
        return len(self.neighbours)

    def similarity(self, other: _Vertex) -> float:
        """Calculates how similar this vertex is to another by comparing the number of shared
        neighbours they have.

        Preconditions:
            - self.kind == 'ingredient' and other.kind == 'ingredient'

        >>> v1 = _Vertex('v1', None, [], 'ingredient', 0)
        >>> v2 = _Vertex('v2', None, [], 'ingredient', 0)
        >>> v3 = _Vertex('v2', None, [], 'ingredient', 0)
        >>> v4 = _Vertex('v2', None, [], 'ingredient', 0)
        >>> v5 = _Vertex('v2', None, [], 'ingredient', 0)
        >>> v1.neighbours.add(v3)
        >>> v1.neighbours.add(v4)
        >>> v1.neighbours.add(v2)
        >>> v2.neighbours.add(v4)
        >>> v1.similarity(v2)
        0.5
        """
        v1set = self.neighbours - {other}
        v2set = other.neighbours - {self}

        unionset = v1set | v2set
        intersectset = v1set & v2set

        if len(unionset) == 0:
            score = 0.0
        else:
            score = round(len(intersectset) / len(unionset), 2)

        return score

    def shared_neighbours(self, other: _Vertex) -> int:
        """Return the number of shared neighbours between self and other.
        >>> v1 = _Vertex('v1', None, [], 'ingredient', 0)
        >>> v2 = _Vertex('v2', None, [], 'ingredient', 0)
        >>> v3 = _Vertex('v2', None, [], 'ingredient', 0)
        >>> v4 = _Vertex('v2', None, [], 'ingredient', 0)
        >>> v5 = _Vertex('v2', None, [], 'ingredient', 0)
        >>> v1.neighbours.add(v3)
        >>> v1.neighbours.add(v4)
        >>> v1.neighbours.add(v2)
        >>> v2.neighbours.add(v4)
        >>> v1.shared_neighbours(v2)
        1
        """
        v1set = self.neighbours - {other}
        v2set = other.neighbours - {self}
        intersectset = v1set & v2set
        return len(intersectset)


class Graph:
    """A graph used to represent a recipes and ingredients network.
    """
    # Private Instance Attributes:
    #     - _vertices:
    #         A collection of the vertices contained in this graph.
    #         Maps item to _Vertex object.
    _vertices: dict[str, _Vertex]

    def __init__(self) -> None:
        """Initialize an empty graph (no vertices or edges)."""
        self._vertices = {}

    def is_empty(self) -> bool:
        """Returns True if this Graph is empty"""
        return not bool(self._vertices)

    def add_vertex(self, recipe: Recipe, prices: dict) -> None:
        """Add a new vertex representing the given recipe and all its ingredients to the graph.

        The new vertices is not adjacent to any other vertices.
        Do nothing if the given ingredient and/or recipe is already in this graph.

        >>> v5 = Recipe(['v5', ['a', 'b '], '...', '...', '', ['a', 'b'], 8.99])
        >>> g = Graph()
        >>> g.add_vertex(v5, {'a': 5, 'b': 3.99})
        >>> g.is_empty()
        False
        """
        for ingredient in recipe.cleaned_ingredients:
            price = float(prices[ingredient])
            if ingredient not in self._vertices:  # adds a vertex for each ingredient in the recipe
                self._vertices[ingredient] = _Vertex(ingredient, details=None, v_cleaned_ingredients=None,
                                                     kind="ingredient", price=price)

        if recipe.title not in self._vertices:  # adds a vertex for the recipe
            self._vertices[recipe.title] = _Vertex(recipe.title, details=recipe,
                                                   v_cleaned_ingredients=recipe.cleaned_ingredients,
                                                   kind="recipe", price=recipe.price)

    def add_edge(self, recipe: str) -> None:
        """Add an edge between the recipe and every ingredient in it.

        Raise a ValueError if recipe or any ingredient do not appear as vertices in this graph.

        Preconditions:
            - self._vertices[recipe].kind == "recipe"
        """
        v1 = self._vertices[recipe]
        if recipe in self._vertices and v1.kind == "recipe":
            for ingredient in v1.v_cleaned_ingredients:  # loop though each ingredient
                v2 = self._vertices[ingredient]
                v1.neighbours.add(v2)
                v2.neighbours.add(v1)
        else:
            raise ValueError("One or both vertices do not exist.")

    def check_exist(self, item: str) -> bool:
        """Check if this item exists inside the graph, return True if it does.

        >>> v5 = Recipe(['wow', ['a', 'b '], '...', '...', '', ['a', 'b'], 8.99])
        >>> v1 = Recipe(['huh', ['b'], '...', '...', '', ['b'], 3.99])
        >>> g = Graph()
        >>> g.add_vertex(v5, {'a': 5, 'b': 3.99})
        >>> g.check_exist('a')
        True
        >>> g.check_exist('huh')
        False
        """
        if item in self._vertices:
            return True
        else:
            return False

    def filter_kind(self, kind: str) -> list:
        """Return a set of all vertices in the graph that match the given kind.

        Preconditions:
            - kind in {'', 'recipe', 'ingredient'}
        """
        filtered = []
        if kind == '':
            for vertex in self._vertices.values():
                filtered.append(vertex)
            return filtered
        for vertex in self._vertices.values():
            if vertex.kind == kind:
                filtered.append(vertex)
        return filtered

    def to_networkx(self, max_vertices: int = 5000) -> nx.Graph:
        """Convert this graph into a networkx Graph.

        max_vertices specifies the maximum number of vertices that can appear in the graph.
        (This is necessary to limit the visualization output for large graphs.)

        Note that this method is provided for you, and you shouldn't change it.
        """
        graph_nx = nx.Graph()
        for v in self._vertices.values():
            graph_nx.add_node(v.item, kind=v.kind)

            for u in v.neighbours:
                if graph_nx.number_of_nodes() < max_vertices:
                    graph_nx.add_node(u.item, kind=u.kind)

                if u.item in graph_nx.nodes:
                    graph_nx.add_edge(v.item, u.item)

            if graph_nx.number_of_nodes() >= max_vertices:
                break

        return graph_nx

    def get_item(self, name: str) -> Any:
        """Gets the vertex object based on the name of the vertex.

        >>> v5 = Recipe(['wow', ['a', 'b '], '...', '...', '', ['a', 'b'], 8.99])
        >>> g = Graph()
        >>> g.add_vertex(v5, {'a': 5, 'b': 3.99})
        >>> g.get_item('wow')
        _Vertex(wow, kind=recipe)
        """
        if name in self._vertices:
            return self._vertices[name]

    def get_most_connected_ingredients(self) -> list[tuple[int, str, float]]:
        """gets the highest depth ingredients. returns a list of tuples, with the score, the name and price.
        returns at most 10 ingredients in a tuple."""
        depth_scores = []
        for item in self._vertices:
            if self._vertices[item].kind == 'ingredient':
                score = self._vertices[item].depth(), item, self._vertices[item].price
                depth_scores.append(score)

        depth_scores.sort(reverse=True)
        depth_scores = depth_scores[:10]
        return depth_scores[:10]

    def filter_recipes(self, limit: int, user_input: list, prices: dict, pricelimit: Optional[float],
                       reviewlimit: Optional[int]) -> Graph:
        """Return a list that contains the best matched recipes based on the users input (that is ingredients that they
        have) and based on the number of recipes wanted. If there are no matches, return a string tell them so.

        Preconditions:
            - user_input != []
            - limit > 0
        >>> prices = pricestodict('ingredient_prices.csv')
        >>> my_graph = load_graph('food_small copy.csv', 'ingredients copy.csv', 'ingredient_prices.csv')
        >>> g1 = my_graph.filter_recipes( 10, ['potato', 'rosemary', 'egg', 'parsley'], prices,  None, None)
        >>> g1.filter_kind('recipe')
        [_Vertex(Crispy Salt and Pepper Potatoes, kind=recipe), _Vertex(Italian Sausage and Bread Stuffing, kind=recipe)]

        >>> g2 = my_graph.filter_recipes( 1, ['dog', 'cat', 'welcent', 'alden'], prices, None, None)
        >>> g2.filter_kind('recipe')
        []
        """
        reviews = reviews_to_dict()
        recipe = self.filter_kind('recipe')

        poss_recipes = {}

        if user_input:
            for i in recipe:
                for item in user_input:
                    if item in [x.item for x in i.neighbours]:
                        if i.item not in poss_recipes:
                            poss_recipes[i.item] = 1
                        else:
                            poss_recipes[i.item] = 1 + poss_recipes[i.item]
        else:
            for i in recipe:
                poss_recipes[i.item] = 1

        sorted_by_values = dict(sorted(poss_recipes.items(), key=lambda thing: thing[1], reverse=True))

        final_recipes = []
        if pricelimit is not None:
            for recipe in sorted_by_values:
                if sorted_by_values[recipe] > 0 and self._vertices[recipe].price <= pricelimit:
                    final_recipes.append(recipe)
        else:
            for recipe in sorted_by_values:
                if sorted_by_values[recipe] > 0:
                    final_recipes.append(recipe)

        if reviewlimit is not None:
            final_recipes = [obj for obj in final_recipes if (obj in reviews) and (reviews[obj] >= reviewlimit)]

        if len(final_recipes) < limit:
            limit = len(final_recipes)

        if not final_recipes:
            return Graph()
        else:
            filtered_graph = Graph()
            for i in range(0, limit):
                curr_vertex = self._vertices[final_recipes[i]]
                filtered_graph.add_vertex(curr_vertex.details, prices)
                filtered_graph.add_edge(curr_vertex.details.title)
            return filtered_graph

    def get_similar(self, ingredient: str) -> list:
        """Gets similar ingredients by using the _Vertex method 'similar.' Returns a list of at
        most, 5 ingredients.
        """
        scores = []
        target = self.get_item(ingredient)
        ingredients = [item.item for item in self.filter_kind('ingredient')]
        ingredients.remove(ingredient)

        for other in ingredients:
            score = target.similarity(self.get_item(other))
            scores.append((score, other))

        scores.sort(reverse=True)

        return scores[:5]


def load_graph(uncleaned: str, ingredients: str, pricefile: str) -> Graph:
    """Load a graph from the given uncleaned recipe csv file and ingredient csv file.

    The recipe graph stores all the information from the datasets as follows:
    - Create one vertex for each recipe and one vertex for each unique ingredient in the datasets.
    - Edges represent ingredient usage in a recipe (i.e., an edge is added between a recipe and all
      the ingredients it contains)
    """
    prices = pricestodict(pricefile)
    cleaned_csv = cleancsv(uncleaned, ingredients, prices)
    recipe_lst = to_recipe_class(cleaned_csv)

    graph = Graph()

    for recipe in recipe_lst:
        graph.add_vertex(recipe, prices)
        graph.add_edge(recipe.title)

    return graph


def get_user_ingredients() -> list:
    """Prompt user to input ingredients they have and want to use. User input stops when 'stop' is inputted.
    Returns list.
    """
    user_input = []
    all_ingredients = get_food('ingredients copy.csv')
    print("===================================")
    print("Enter the ingredients you have and would like to use. Type 'stop' when done:")
    stop = False
    while not stop:
        choice = input("\nYour ingredient: ").lower().strip()
        if choice == 'stop':
            if user_input:
                stop = True
            else:
                print("You have not entered any ingredients. Try again.")
        else:
            if choice not in all_ingredients:
                print("Invalid ingredient, try again")
            else:
                user_input.append(choice)
    return user_input


def get_user_single_ingredient() -> list:
    """Prompt user to input a single ingredient they have, want to use, or want to know more about. Returns
    that ingredient in a list.
    """
    user_input = []
    all_ingredients = get_food('ingredients copy.csv')
    print("===================================")
    print("Enter the ingredient you'd like to know more about:")
    stop = False
    while not stop:
        choice = input("\nYour ingredient: ").lower().strip()
        if choice not in all_ingredients:
            print("Invalid ingredient, try again")
        else:
            user_input.append(choice)
        if user_input:
            stop = True
        else:
            print("You have not entered any ingredients. Try again.")
    return user_input


def get_recipe_limit() -> int:
    """Prompt the user to enter the maximum number of recipes they would like to receive.

    User input must be a valid number greater than 0.
    """
    limit = 0
    print("===================================")
    print("What is the max number of recipes you'd like?")

    while limit < 1:
        limit_input = input("\nEnter a number: ").strip()
        if limit_input.isdigit():
            limit = int(limit_input)
            if limit < 1:
                print("Number must be greater than 0")
        else:
            print("Please enter a valid number.")

    return limit


def get_price_limit() -> Optional[float]:
    """Prompt the user to enter the maximum number of recipes they would like to receive.
    Return None if no price limit is given.
    """
    limit = -1
    print("===================================")
    print("What is the max price you prefer for a recipe?" +
          "(Prices are not given per single serving, but for multiple (5-6))")

    while limit < 0:
        limit_input = input("\nEnter a number or 'None': ").strip()

        if limit_input.lower() == 'none':
            return None

        try:
            limit = float(limit_input)
            if limit < 0:
                print("Number must be greater than 0")
        except ValueError:
            print("Invalid response. Please enter a valid number.")

    return limit


def get_review_limit() -> Optional[int]:
    """Prompt the user to enter the minimum score/rating they want for their recipes.
    Return None if no review limit is given.
    """
    limit = 0
    print("===================================")
    print("What is the minimum rating you'd like (1-5, no decimals)? Enter 'None' to see recipes regardless of rating.")

    while limit < 1 or limit > 5:
        limit_input = input("\nEnter a number or 'None': ").strip()
        if limit_input.isdigit():
            limit = int(limit_input)
            if limit < 1:
                print("Number must be greater than 0")
            if limit > 5:
                print("Number must be less than or equal to 5")
        elif limit_input.lower() == 'none':
            return None
        else:
            print("Invalid response.")

    return limit


def get_recipe(main_graph: Graph) -> Recipe:
    """Gets user input on what recipe they want. Shows the recipes in groups of 10
    for easier viewing. Returns a Recipe object."""
    recipes = main_graph.filter_kind('recipe')
    reviews = reviews_to_dict()
    commands = {'prev', 'next'}
    numrecipes = len(recipes)
    cutoff = 10
    done = False

    while not done:
        print("===================================")
        print("What recipe would like like the full details for?")
        for recipe in recipes[cutoff - 10: cutoff]:
            if recipe.item in reviews:
                print("- " + recipe.item + " || Est. Price: $" + str(recipe.price) + " || Rating: "
                      + str(reviews[recipe.item]))
            else:
                print("- " + recipe.item + " || Est. Price: $" + str(recipe.price) + " || No Reviews Yet")

        user_choice = input("\nEnter name of recipe (exact), prev, or next: ")

        options = [recipe.item for recipe in recipes[cutoff - 10:cutoff]]

        if user_choice not in options and user_choice not in commands:
            print("===================================")
            print("Invalid choice, try again")
        elif (user_choice == 'prev' and cutoff == 10) or (user_choice == 'next' and cutoff + 10 > numrecipes):
            print("===================================")
            print("Invalid choice, try again")
        elif user_choice == 'prev':
            cutoff -= 10
        elif user_choice == 'next':
            cutoff += 10
        else:
            choice = main_graph.get_item(user_choice).details
            return choice


def rate_recipe(recipe: Recipe) -> None:
    """Prompts the user to rate the given Recipe and then saves it into reviews.csv"""
    print("===================================")
    print("Would you like to rate this recipe? Enter 'yes' or anything else to cancel:")
    user_choice = input("\nEnter response: ").lower()

    csv_file = "reviews.csv"

    if user_choice == "yes":
        recipe_name = recipe.title
        while True:
            try:
                print("===================================")
                rating = int(input("Rate the recipe (1-5): "))
                if 1 <= rating <= 5:
                    break
                else:
                    print("Please enter a number between 1 and 5.")
            except ValueError:
                print("Invalid input. Enter a number between 1 and 5.")

        print("===================================")
        review = input("Write your review: ")
        new_entry = pd.DataFrame([[recipe_name, rating, review]], columns=["Recipe", "Rating", "Review"])

        if os.path.exists(csv_file):
            new_entry.to_csv(csv_file, mode='a', header=False, index=False)
        else:
            new_entry.to_csv(csv_file, mode='w', header=True, index=False)

        print("Your review has been saved!")


def find_pairings(sub_graph: Graph, ingredient: str) -> None:
    """Print popular pairings. Calls a graph function to find ingredients with similar neighbours."""
    similar = sub_graph.get_similar(ingredient)
    print("===================================")
    print("The ingredients that appear the most with " + ingredient + " are:")
    for item in similar:
        recipesshared = sub_graph.get_item(item[1]).shared_neighbours(sub_graph.get_item(ingredient))
        print("- " + item[1] + " || Similarity score: " + str(item[0]) + " || Shares " + str(recipesshared) +
              " recipes || " + "~$" + str(sub_graph.get_item(item[1]).price))

    print("===================================")
    input("Press enter to continue...")


def option_1(main_graph: Graph) -> None:
    """Does option 1, that being 'enter ingredients you already have'."""
    prices = pricestodict('ingredient_prices.csv')
    user_ingredients = get_user_ingredients()
    user_limit = get_recipe_limit()
    price_limit = get_price_limit()
    review_limit = get_review_limit()
    user_recipes = main_graph.filter_recipes(user_limit, user_ingredients, prices, price_limit, review_limit)

    if user_recipes.is_empty():
        print("===================================")
        print("No recipes found, please give different preferences.")

    else:
        choice = get_recipe(user_recipes)
        print("===================================")
        print(choice.title)
        print()
        print("Ingredients:")
        for ingredient in choice.full_ingredients:
            print("- " + ingredient)
        print()
        print(choice.instructions)
        print()
        rate_recipe(choice)


def option_2(main_graph: Graph) -> None:
    """Does option 2 in the main, which lets the user input an ingredient and then outputs the most connected
    ingredients associated"""
    prices = pricestodict('ingredient_prices.csv')
    price_limit = get_price_limit()
    review_limit = get_review_limit()
    user_recipes = main_graph.filter_recipes(14000, [], prices, price_limit, review_limit)
    lst = user_recipes.get_most_connected_ingredients()
    print("===================================")
    print("Here are the the most common ingredients for recipes within your price range and rating range:")
    if not lst:
        print("There were no matches based on your ingredient and filtrations.")
        return

    for item in lst:
        print("- " + "Number of recpies it's connected to: " + str(item[0]) + " || " + "Ingredient: " +
              str(item[1]) + " || " + "Price: ~$" + str(item[2]))


def option_3(main_graph: Graph) -> None:
    """Does option 3 in the main, which finds popular ingredient pairings"""
    prices = pricestodict('ingredient_prices.csv')
    user_ingredients = get_user_single_ingredient()
    recipe_limit = 14000
    user_recipes = main_graph.filter_recipes(recipe_limit, user_ingredients, prices, None, None)
    find_pairings(user_recipes, user_ingredients[0])


def option_4(main_graph: Graph) -> None:
    """Does option 4 in the main, which asks for filters than provides a visualizaiton"""
    prices = pricestodict('ingredient_prices.csv')
    user_ingredients = get_user_ingredients()
    user_limit = get_recipe_limit()
    price_limit = get_price_limit()
    user_recipes = main_graph.filter_recipes(user_limit, user_ingredients, prices, price_limit, None)

    if user_recipes.is_empty():
        print("===================================")
        print("No recipes found with your filters. Please try again.")
    else:
        from proj2visualisation import visualize_graph
        print("Loading...")
        visualize_graph(user_recipes, highlight_ingredients=user_ingredients)
        print("Graph completed!")

if __name__ == "__main__":
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['R1705', 'E9998', 'E9999']})
    doctest.testmod(verbose=True)
