# import the schema builders corresponding to JSON data types:
# primitives (booleans, numbers, strings), arrays, objects
from vino import prim, arr, obj
# import some native validating and marshalling processors
from vino import allowempty, allownull, required, unmatched_properties 
from vino import is_str, maxlength, is_int
# import ValidationError
from vino import ValidationError
# import some user-defined processors
#from my_validations import email_format, valid_password

def email_format(data, state):
    if not '@' in data:
        raise ValidationError('Email format does not seem valid')
    return data

def valid_password(data, state):
    invalid_password = ValidationError('Invalid password')
    digits = set('0123456789')
    if len(data) < 8:
        # password too short
        raise invalid_password
    if len(digits.intersection(data))==len(data):
        # password only made up of digits
        raise invalid_password
    if len(digits.intersection(data))==0:
        # password has no digits
        raise invalid_password
    return data


lastname = lambda x,y: x=='lastname'
user_registration_schema = obj(
    prim(~required, is_str, allownull, ~allowempty).apply_to('firstname', lastname),
    prim(required, ~allownull, ~allowempty, is_str, email_format).apply_to('email'),
    prim(~required, ~allownull, ~allowempty, is_str,
            valid_password).apply_to('password'),
    arr(~required, allowempty, ~allownull, 
        maxlength(8),
        prim(~allownull, ~allowempty, is_str).apply_to(range(3)),
        prim(allownull, is_int).apply_to(range(4,7)),
    ).apply_to('technologies'),
    unmatched_properties('remove'),
)

"""
The above validation specifies that:
    - "firstname" and "lastname" fields:
        - are not required (they may be missing from submitted data).

            # ok
            data = {
                "email": "user@example.com", 
                "password": "abcd1234",
                "technologies": [
                    "python"
                ]
            }

        - if present, they must be strings. 

            # ok
            "firstname": "Michael"
            # not ok
            "lastname": 007

        - a null value is also acceptable. 
            
            # ok
            "firstname": null

        - but an empty string is not.
            # not ok
            "lastname": "" 

    - "email" field: 
        - is required (cannot be missing from submitted data)

            # not ok
            {
                "firstname": "foo",
                "lastname": "bar",
                "password": "1234abcd",
                "technologies": ["python"]
            }

        - null or empty strings are not allowed

            # not ok
            "email": null
            "email": ""

        - in addition, will be checked against user-defined processor "email_format", which only checks for the presence of '@' sign to validate an address.

            # ok
            michael@example
            # not ok
            michael[at]example

    - "password" field:
        - not required
        - if present, cannot be null or an empty string.
        - in addition, will be checked against a user-defined processor "valid_password", which verifies length, presence of digits and at least one other character type.

    - "technologies" field:
        - not required.
        - if present must be an array.
        - can be an empty array.
        - cannot be a null.
        - will be limited to 8 items, anything beyond will be trimmed in the results.
        - first 3 items (index 0 to 2)  (if present)
            - must be strings
            - do not accept null
            - do not accept empty values
        - items in range [4:7] (index 4 to 6) 
            - must be integers
            - accept null
        - items at index 3 and 7 must be boolean, if present 

    - any undeclared properties will be removed from the returned data. The other options are`unmatched_properties('ignore')` which return extra as they are, or `unmatched_properties('raise')` which raises a `vino.ValidationError`. 
    
"""

# valid
user_data = {
    'firstname': 'Peter',
    'lastname': 'Parker',
    'email': 'spidey@example.com',
    'password': '1234abcd',
    'technologies': [
        'python', 'postgresql', 'mysql', True, 8, 3, 900
    ],
}

# invalid
user_data = {
    'firstname': 'Peter',
    'lastname': 'Parker',
    'email': 'spidey@example.com',
    'password': '1234abcd',
    'technologies': [
        # invalid 3rd item (bool instead of str)
        'python', 'postgresql', True, 8, 3, 900
    ],
}

# invalid
user_data = {
    'firstname': 'Peter',
    'lastname': 'Parker',
    'email': 'spidey@example.com',
    'password': '1234abcd',
    'technologies': [
        # invalid 5th item (bool instead of int)
        'python', 'postgresql', 'mysql', True, False, 3, 900
    ],
}

# valid
user_data = {
    'firstname': 'Peter',
    # "lastname" set to null
    'lastname': None,
    'email': 'spidey@example.com',
    # "password" not provided
    'technologies': [
        # will be trimmed to 8 items
        'python', 'postgresql', 'mysql', True, 8, 3, 900, False, "abc", "def", "ghi", True
    ],
}
print(user_registration_schema.validate(user_data)) 

# valid
user_data = {
    'firstname': 'Peter',
    'lastname': 'Parker',
    'email': 'spidey@example.com',
    'password': '1234abcd',
    'technologies': [
        'python', 'postgresql', 'mysql', True, 8, 3, 900
    ],
    # will be removed from the results
    "foo": "bar",
    "username": "spiderman",
}


#print(user_registration_schema.validate(user_data)) 
