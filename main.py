from datetime import datetime 
from functools import reduce
import re



def main():
    # Loop responsible for overall control of menu
    while loop_menu() != None:
        pause()
    print("Thank you for using my program!")

# Main menu options and logic for program continuation
def loop_menu():
    choice = menu_choice()
    if(choice == "1"):
        vehicle_menu()
        return True
    if(choice == "2"):
        review_menu()
        return True
    if(choice == "3"):
        report_menu()
        return True
    if(choice == "4"):
        return None
    else:
        show_invalid(choice)
        return loop_menu()

def menu_choice():
    print("1. Car Management")
    print("2. Review Menu")
    print("3. Reports Menu")
    print("4. Exit")
    return input("\nPlease enter your choice: ")


def vehicle_menu():
    # bag is a dictionary of available
    # functions created in the use_vehicle function
    # this abstracts away the logic for handling 
    # maintenance of vehicles. Similar logic is used
    # for reviews and reports
    vehicle_bag = use_vehcile()

    choice = display_vehicle_menu()

    if(choice == "1"):
        vehicle_bag["add_vehicle"]()
        return vehicle_menu()
    if(choice == "2"):
        vehicle_bag["edit_vehicle"]()
        return vehicle_menu()
    if(choice == "3"):
        vehicle_bag["delete_vehicle"]()
        return vehicle_menu()
    if(choice == "4"):
        print("Taking you back to main menu!")
    else:
        show_invalid(choice)
        return vehicle_menu()



def display_vehicle_menu():
    print("1. Add Vehicle")
    print("2. Edit a Vehicle")
    print("3. Delete a Vehicle")
    print("4. Exit Vehicle Menu")
    return input("\nPlease enter your choice: ")

def review_menu():
    review_bag = use_reviews()

    choice = display_review_menu()

    if(choice == "1"):
        review_bag["add_review"]()
        return review_menu()
    if(choice == "2"):
        return print("Taking you back to main menu!")
    else:
        show_invalid(choice)
        return review_menu()

def display_review_menu():
    print("1. Add a review")
    print("2. Return to main menu")
    return input("\nPlease enter your choice: ")

def report_menu():
    choice = display_report_menu()

    reports = use_reports()

    if(choice == "1"):
        reports["year_statistics"]()
        return report_menu()
    if(choice == "2"):
        reports["vehicle_statistics"]()
        return report_menu()
    if(choice == "3"):
        reports["view_reviews"]()
        return report_menu()
    if(choice == "4"):
        return print("Returning you to main menu")
    else:
        print("Please choose a valid menu option")
        return report_menu()
    

def display_report_menu():
    print("1. Year Statistics")
    print("2. Vehicle Statistics")
    print("3. All Reviews")
    print('4. Exit Report Menu')
    return input("\nPlease enter your choice: ")

# Responsible for containing all vehicle logic,
# including schema, persistence, and mutation logic
def use_vehcile():
    schema = {
        "name": {
            "from_file": lambda x: x,
            "col": 0,
        },
        "type": {
            "from_file": lambda x: x,
            "col": 1,
        },
        "manufacture_year": {
            "from_file": lambda x: int(x),
            "col": 2,
        },
        "price": {
            "from_file": lambda x: float(x),
            "col": 3,
        }
    }

    # reliance on generic utility functions such as this can be found throughout program
    vehicles = read_file("cars", schema)

    # VALIDATION FUNCTIONS
    # These functions are used to validate
    # the users input for both creation and mutation
    # for all fields of the schema
    def validate_name(name):
        if(len(name) <= 1):
            return validate_name(input("Please enter a name of at least one character: "))
        if(len(list(filter(lambda vehicle: vehicle[0] == name, vehicles))) > 0):
            return validate_name(input("Please enter a name that is not already taken: "))
        return name
    
    schema["name"]["validate"] = validate_name

    
    def validate_type(type):
        car_types = ["sedan", "hatchback", "suv", "truck", "van", "convertible"]

        pattern = r"(?i)\b(" + '|'.join(car_types) + r")\b"

        if (re.search(pattern, type) == None):
            return(validate_type(input(f"Please enter one of the following types: {', '.join(car_types)}: ")))

        return type
    
    schema["type"]["validate"] = validate_type

    
    def validate_man_year(year):
        try:
            num = int(year)
            if not (2010 <= num <= 2020):
                return validate_man_year(input("Please enter a year between 2010 and 2020: "))
            return num
        except ValueError:
            return validate_man_year(input("Please enter a valid number: "))
        
    schema["manufacture_year"]["validate"] = validate_man_year
    
        
    def validate_price(price):
        try:
            num = float(price)
            if not (0 < num):
                return validate_price(input("Please enter a price greater than $0.00: "))
            return num
        except ValueError:
            return validate_price(input("Please enter a valid price: "))
        
    schema["price"]["validate"] = validate_price

    def find_vehicle(search_val = None):
        display_items(vehicles, schema)
        if(search_val == None):
            search_val = input("Insert the name of the vehicle you are searching for: ")

        found_vehicle = find_item(search_val, schema, vehicles)
        if(found_vehicle == None and input(f"Vehicle with name: {search_val} not found, continue? (y/n): ") == "y"):
            return find_vehicle()
        return found_vehicle
        

    def add_vehicle():
        vehicle = []
        display_items(vehicles, schema)
        for name, field in schema.items():
            # Verifies input entered in validation function defined in schema
            vehicle.append(field["validate"](input(f"Please enter a value for {name}: ")))
        
        vehicles.append(vehicle)

        write_file("cars", vehicles)

    def edit_vehicle():
        found_vehicle = find_vehicle()
        
        if(found_vehicle == None): 
            return
        
        new_vehicle = []
        for name, field in schema.items():
            # Verifies input entered in validation function defined in schema
            if(input(f"{name}: {found_vehicle[schema[name]['col']]}\nEnter 'y' to edit: ").lower() == "y"):
                new_vehicle.append(field["validate"](input(f"Please enter a value for {name}: ")))
            else:
                new_vehicle.append(found_vehicle[schema[name]['col']])
        
        vehicles.remove(found_vehicle)
        vehicles.append(new_vehicle)
        write_file("cars", vehicles)

    def delete_vehicle():
        found_vehicle = find_vehicle()

        if(found_vehicle == None):
            return None
        
        print(f"\nWould you like to remove this vehicle?\n\n{prep_display_item(found_vehicle, schema)}\n")
        if(input("(Please enter y/n): ").lower() == "y"):
            print("\nRemoving vehicle...")
            pause()
            vehicles.remove(found_vehicle)
            write_file("cars", vehicles)


    # Expose vehcile API functions
    return {
        "vehicles": vehicles,
        "schema": schema,
        "add_vehicle": add_vehicle,
        "edit_vehicle": edit_vehicle,
        "delete_vehicle": delete_vehicle,
        "find_vehicle": find_vehicle
    }

# Reuse of design from Vehicle
def use_reviews():
    schema = {
        "id": {
            "from_file": lambda x: int(x),
            "col": 0,
        },
        "vehicle_name": {
            "from_file": lambda x: x,
            "col": 1
        },
        "date": {
            "from_file": lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S"),
            "col": 2
        },
        "rating": {
            "from_file": lambda x: int(x),
            "col": 3
        },
        "comment": {
            "from_file": lambda x: x,
            "col": 4
        }
    }

    reviews = read_file("reviews", schema)

    def validate_id(id = None):
        if(id == None):
            id = len(reviews) + 1
        return id
    
    schema["id"]["validate"] = validate_id

    
    def validate_vehicle_name(name = None):
        vehicle_bag = use_vehcile()
        found_vehcile = vehicle_bag["find_vehicle"](name)
        return found_vehcile[vehicle_bag["schema"]["name"]["col"]]
    
    schema["vehicle_name"]["validate"] = validate_vehicle_name

    
    def validate_date(review_date = None):
        if(review_date == None):
            return datetime.now().replace(microsecond=0)
        try:
            return datetime.strptime(review_date, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return validate_date(input("Please enter a valid date: "))
        
    schema["date"]["validate"] = validate_date
    
        
    def validate_rating(rating = None):
        if(rating == None):
            rating = input("Please enter the rating: ")
        try:
            num = int(rating)
            if not (1 <= num <= 5):
                return validate_rating(input("Invalid rating, please enter a number 1 through 5"))
            return num
        except ValueError:
            return validate_rating(input("Please enter a valid number: "))
        
    schema["rating"]["validate"] = validate_rating

    def validate_comment(comment = None):
        if(comment == None):
            comment = input("Please enter your comment: ")
        if not (1 <= len(comment) <= 100):
            return validate_comment(input("You must enter a comment between 1 and 100 characters: "))
        return comment
        
    schema["comment"]["validate"] = validate_comment
        

    def add_review():
        review = []
        display_items(reviews, schema)
        for name, field in schema.items():
            # Verifies input entered in validation function defined in schema
            review.append(field["validate"]())
        
        reviews.append(review)

        write_file("reviews", reviews)


    # Expose review API functions
    return {
        "reviews": reviews,
        "schema": schema,
        "add_review": add_review,
        # edit_vehicle,
        # delete_vehicle
    }

# Reuse of use_vehcile API
def use_reports():

    def year_statistics():
        def get_year():
            year = input("please enter the year you are looking for: ")
            try:
                num = int(year)
                if not (2015 <= num <= 2020):
                    print("Please enter a year between 2015 and 2020")
                    return get_year()
                return num
            except ValueError:
                print("please enter a valid year")
                return get_year()
            
        year = get_year()

        review_bag = use_reviews()

        filtered_reviews = list(filter(lambda x: x[review_bag["schema"]["date"]["col"]].year == year , review_bag["reviews"]))
        ratings = list(map(lambda x: x[review_bag["schema"]["rating"]["col"]], filtered_reviews))

        report = f"there were no ratings for year {year}" 
        
        if not (len(ratings) == 0):
            max_rating = max(ratings)
            min_rating = min(ratings)
            average_rating = (reduce(lambda curr, accum: curr + accum, ratings) / len(ratings))

            report = f"for year {year}, Max: {max_rating} Min: {min_rating} Average: {average_rating}"

        write_file(f"rating_statistics_{year}", [report], delimiter=False)

        print(report)
        pause()
        

    def vehicle_statistics():
        vehicle_bag = use_vehcile()
        review_bag = use_reviews()

        vehicles_names = list(map(lambda x: x[vehicle_bag["schema"]["name"]["col"]] , sorted(vehicle_bag["vehicles"], key=lambda x: x[vehicle_bag["schema"]["name"]["col"]])))

        reviews_by_car = sorted(review_bag["reviews"], key=lambda x: x[review_bag["schema"]["vehicle_name"]["col"]])

        overview_data = list(map(lambda v: [
            v, 
            len(list(filter(lambda r: r[review_bag["schema"]["vehicle_name"]["col"]] == v,reviews_by_car))), 
            "\n".join(list(map(lambda x: x[review_bag["schema"]["comment"]["col"]], list(filter(lambda r: r[review_bag["schema"]["vehicle_name"]["col"]] == v, reviews_by_car)))))
            ] 
            , vehicles_names))
        
        report = "\n\n".join(list(map(lambda x: f"Vehicle: {x[0]} had {x[1]} reviews and they were: {x[2]}", overview_data)))

        write_file("avg_rating_by_car", [report], False)
        print(report)

        pause()

    def view_reviews():

        review_bag = use_reviews()

        positive_words = read_file("positive_word_dictionary")  

        # Creates regex pattern for comparison to comments
        pattern = r"\b(?i)(" + '|'.join(map(re.escape, positive_words)) + r")\b"

        comments = list(map( lambda x: x[review_bag["schema"]["comment"]["col"]], review_bag["reviews"]))

        positive_comments = list(filter(lambda x: re.search(pattern, x), comments))

        report = f"There were a total of {len(positive_comments)} positive comments and they were:\n" + "\n".join(positive_comments)

        write_file("comments_with_positive_words", [report], False)
        print(report)
        
        pause()


    # Expose Report API functions
    return {
        "year_statistics": year_statistics,
        "vehicle_statistics": vehicle_statistics,
        "view_reviews": view_reviews
    }

# FILE HANDLING

# Generic file reading method. flexible for use with
# and without a schema
def read_file(file_name, schema = None):
    file = open(file_name + ".txt", "r")
    items = []
    for line in list(map(lambda x: x.strip("\n"), file.readlines())):
        if(schema == None):
            items.append(line)
            continue

        items.append(parse_line(line.split("#"), schema))
    file.close()

    return items

# Used to parse a line to match a schema specified
def parse_line(line, schema):
    item = []
    for info in schema.values():
        item.append(info["from_file"](line[info["col"]]))
    return item

# Generic write file function, allows for delimiter 
# flag for writing of reports
def write_file(file_name, items, delimiter=True):
    file = open(file_name + ".txt", "w")

    for item in items:
        # Join each item together in a string seperated by #
        # Also includes EOL character
        if not delimiter:
            file.write(item)
            continue
        file.write("#".join(str(i) for i in item) + "\n")

    file.close()

# Generic Utility
def show_invalid(value):
    print(f"\n{value} is not a valid value here\nPlease press enter....")
    input()
    print("\n")

def pause():
    print("\nPlease press enter to continue...")
    input()
    print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n")

# Generic display function to put items in a table
def display_items(items, schema):
    to_print = "\n"
    for item in items:
        to_print = to_print + prep_display_item(item, schema)
        to_print = to_print + "\n"
    print(to_print)

# Preps each line for display based off of schema provided
def prep_display_item(item, schema):
    to_print = ""
    for name, field in schema.items():
        to_print = to_print + (f"{name} {item[field['col']]:<15}")
    return to_print

# Generic find function, searches one layer deep in a list.
# Will search all fields specified in schema paramater
def find_item(search_val, schema, items):
    for field in schema.values():
        for item in items:
            if(item[field["col"]] == search_val):
                return item
    return None

main()