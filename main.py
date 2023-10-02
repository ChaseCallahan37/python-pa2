from datetime import datetime 
from operator import itemgetter

# Schemas used for validation and reading in from files


review_schema = {
    "id": {
        "fromFile": lambda x: int(x),
        "col": 0
    },
    "vehicle_name": {
        "fromFile": lambda x: x,
        "col": 1
    },
    "date": {
        "fromFile": lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S"),
        "col": 2
    },
    "rating": {
        "fromFile": lambda x: int(x),
        "col": 3
    },
    "comment": {
        "fromFile": lambda x: x,
        "col": 4
    }
}


vehicles = []
reviews = []


def main():

    while loop_menu() != None:
        pause()
    print("Thank you for using my program!")

def loop_menu():
    choice = menu_choice()
    if(choice == "1"):
        vehicle_menu()
        return True
    if(choice == "2"):
        print("Choice 2")
        return True
    if(choice == "3"):
        print("Choice 3")
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
    [_, add_vehicle, edit_vehicle, delete_vehicle] = use_vehcile()

    choice = display_vehicle_menu()

    if(choice == "1"):
        add_vehicle()
        return vehicle_menu()
    if(choice == "2"):
        edit_vehicle()
        return vehicle_menu()
    if(choice == "3"):
        delete_vehicle()
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

def use_vehcile():
    schema = {
        "name": {
            "fromFile": lambda x: x,
            "col": 0,
        },
        "type": {
            "fromFile": lambda x: x,
            "col": 1,
        },
        "manufactureYear": {
            "fromFile": lambda x: int(x),
            "col": 2,
        },
        "price": {
            "fromFile": lambda x: float(x),
            "col": 3,
        }
    }

    vehicles = read_file("cars", schema)

    def validate_name(name):
        if(len(name) <= 1):
            return validate_name(input("Please enter a name of at least one character: "))
        if(len(list(filter(lambda vehicle: vehicle[0] == name, vehicles))) > 0):
            return validate_name(input("Please enter a name that is not already taken: "))
        return name
    
    schema["name"]["validate"] = validate_name

    
    def validate_type(type):
        return type
    
    schema["type"]["validate"] = validate_type

    
    def validate_man_year(year):
        try:
            return int(year)
        except ValueError:
            return validate_man_year(input("Please enter a valid number: "))
        
    schema["manufactureYear"]["validate"] = validate_man_year
    
        
    def validate_price(price):
        try:
            return float(price)
        except ValueError:
            return validate_price(input("Please enter a valid price: "))
        
    schema["price"]["validate"] = validate_price

    def find_vehicle():
        display_items(vehicles, schema)
        search_val = input("Insert the name of the vehicle you are searching for: ")
        found_vehicle = find_item(search_val, schema, vehicles)
        if(found_vehicle == None and input(f"Vehicle with name: {search_val} not found, continue? (y/n): ") == "y"):
            return find_item()
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
    return [
        vehicles,
        add_vehicle,
        edit_vehicle,
        delete_vehicle
    ]

# FILE HANDLING

def read_file(file_name, schema):
    file = open(file_name + ".txt", "r")
    items = []
    for line in list(map(lambda x: x.strip("\n"), file.readlines())):
        items.append(parse_line(line.split("#"), schema))
    file.close()

    return items

def parse_line(line, schema):
    item = []
    for info in schema.values():
        item.append(info["fromFile"](line[info["col"]]))
    return item

def write_file(file_name, items):
    file = open(file_name + ".txt", "w")

    for item in items:
        # Join each item together in a string seperated by #
        # Also includes EOL character
        file.write("#".join(str(i) for i in item) + "\n")

    file.close()

# Utility
def show_invalid(value):
    print(f"\n{value} is not a valid value here\nPlease press enter....")
    input()
    print("\n")

def pause():
    print("\nPlease press enter to continue...")
    input()
    print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n")

def display_items(items, schema):
    to_print = "\n"
    for item in items:
        to_print = to_print + prep_display_item(item, schema)
        to_print = to_print + "\n"
    print(to_print)

def prep_display_item(item, schema):
    to_print = ""
    for name, field in schema.items():
        to_print = to_print + (f"{name} {item[field['col']]:<15}")
    return to_print

def find_item(search_val, schema, items):
    for field in schema.values():
        for item in items:
            if(item[field["col"]] == search_val):
                return item
    return None

main()