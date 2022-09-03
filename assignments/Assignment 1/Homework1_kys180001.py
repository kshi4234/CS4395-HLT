import os
import sys
import re
import pickle


# Class defining a person according to the specifications in the homework document
class Person:
    # Initializes all object attributes
    def __init__(self):
        self.last = None
        self.first = None
        self.mi = None
        self.id = None
        self.phone = None

    # This should be the only function that we need to interact with outside of the class
    # ONLY calls other class methods to set all of the attributes necessary
    def set_fields(self, entry, id_dict):
        last, first, mi, my_id, phone = entry
        self.set_last(last)
        self.set_first(first)
        self.set_mi(mi)
        self.set_id(my_id, id_dict)
        self.set_phone(phone)
        return

    # Always sets the first character to uppercase and everything else to lowercase
    # and then sets self.first equal to the concatenated string.
    def set_first(self, first):
        self.first = first[0].upper() + first[1:].lower()
        return

    # Always sets the first character to uppercase and everything else to lowercase
    # and then sets self.first equal to the concatenated string.
    def set_last(self, last):
        self.last = last[0].upper() + last[1:].lower()
        return

    # Only takes the first character and capitalizes it.
    # If there is no middle initial, set it to 'X'
    def set_mi(self, mi):
        if not mi:
            self.mi = 'X'
        else:
            self.mi = mi[0].upper()
        return

    # Method sets the id attribute by calling its respective helper function.
    # Afterwards it updates the dictionary with valid ID as key and self (person instance) as value.
    def set_id(self, my_id, id_dict):
        self.id = self.set_id_helper(my_id, id_dict)
        id_dict[self.id] = self
        return

    # Sets the ID. First checks to see if it is valid. If not, the recursive loop keeps requesting
    # a valid ID until a valid ID is entered.
    # If the ID is already valid, or when the ID becomes valid, we check to see if the ID was already used.
    # If so, keep requesting a unique ID until a unique ID is entered.
    def set_id_helper(self, my_id, id_dict):
        prefix = self.first + ' ' + self.last  # Helps indicate which ID is associated with who
        if len(my_id) != 6 or not my_id[:2].isalpha() or not my_id[:2].isupper() or not my_id[2:].isdigit():
            print(prefix + ' - ID invalid: ' + my_id)
            print(prefix + ' - ID is two letters followed by 4 digits')
            my_id = input(prefix + ' - Please enter a valid id: ')
            my_id = self.set_id_helper(my_id, id_dict)  # Enter recursion
        elif my_id in id_dict.keys():
            my_id = input(prefix + ' - ID ' + my_id + ' already in use! Please enter an unused ID: ')
            my_id = self.set_id_helper(my_id, id_dict)  # Enter recursion
        return my_id  # If we fall through all of the conditions, we can return the final valid ID

    # Sets the phone number.
    # First strips all non-digit characters from the string.
    # Then separates into 2 groups of 3-digit numbers and one of 4-digits,
    # inserts '-' and then concatenates back together.
    def set_phone(self, phone):
        phone = re.sub('[^0-9]', '', phone)
        self.phone = phone[:3] + '-' + phone[3:6] + '-' + phone[6:]
        return

    # Prints out all of the attributes in the order shown in the assignment document.
    def display(self):
        print('Employee ID: ' + self.id)
        print('\t', self.first, self.mi, self.last)
        print('\t', self.phone, '\n')
        return


# Gets the input from the relative path.
# It also splits the rows by the comma delimiter used in CSV files.
def get_input(path):
    cwd = os.getcwd()
    path = os.path.join(cwd, path)  # Path to file
    with open(path, 'r', encoding='UTF-8') as f:  # Open file for reading
        content = f.readlines()[1:]  # Discard the first line
        cleaned = [re.split(',', line) for line in content]  # Split along the comma delimiter
    return cleaned


# Enter all the data row by row, each row representing a different person
# Returns the id dictionary for use in the main method.
def enter_data(cleaned):
    id_dict = {}
    for entry in cleaned:
        new_person = Person()
        new_person.set_fields(entry, id_dict)
    return id_dict


# Display all people in the dictionary
def display_all(people_dict):
    print('\n\nEmployee List: \n')
    for person in people_dict.values():
        person.display()
    return


# Main function to prevent global variable declarations and acts as overhead
def main():
    path = sys.argv[1]  # The relative path is the argument with index 1
    cleaned = get_input(path)  # Get the list of csv rows with data split along commas
    people_dict = enter_data(cleaned)  # enter_data sets all the data and also returns the completed dictionary

    # Export the dictionary to a pickle file
    with open('pickle_dict.pickle', 'wb') as p:
        pickle.dump(people_dict, p, protocol=pickle.HIGHEST_PROTOCOL)

    # Check that pickle file is correctly storing dictionary
    with open('pickle_dict.pickle', 'rb') as p:
        pickle_dict = pickle.load(p)
        display_all(pickle_dict)
    return


# Checks to see if input path exists and then calls the main function
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('ERROR! You must provide a relative path name!')
        quit()
    main()
