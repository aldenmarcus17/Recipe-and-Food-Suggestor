"""Main Method"""
from proj2functions import *

if __name__ == '__main__':
    print("Saving Starving Students || Loading")
    choices = ["1) Enter ingredients you already have", "2) Find common ingredients based on filters",
               "3) Find ingredient pairings", "4) Show visualisation of recipes", "5) Quit"]
    end = False
    main_graph = load_graph('food copy.csv', 'ingredients copy.csv',
                            'ingredient_prices.csv')
    all_ingredients = get_food('ingredients copy.csv')

    while not end:
        print("===================================")
        print("Welcome to the directory, what would you like to do?")
        for action in choices:
            print("-", action)

        choice = input("\nSelect from the following (enter a number): ").lower().strip()
        while choice not in ["1", "2", "3", "4", "5"]:
            print("===================================")
            print("Invalid entry, try again")
            print("===================================")
            print("Welcome to the directory, what would you like to do?")
            for action in choices:
                print("-", action)
            choice = input("\nSelect from the following (enter a number): ").lower().strip()

        if choice == "1":
            option_1(main_graph)
        elif choice == "2":
            option_2(main_graph)
        elif choice == "3":
            option_3(main_graph)
        elif choice == "4":
            option_4(main_graph)
        else:
            end = True
