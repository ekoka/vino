# What's Vino
Vino data validation library. It's designed to handle data deserialized from JSON documents into Python. Its schema declaration is procedural (as opposed to purely declarative), meaning that you describe what you want it to do and in what order.

# Why Vino?
It was designed with a few goals in mind: 
    - to be quick to learn with a relatively simple syntax.
    - to be capable of handling intricate validation scenarios.
    - to be easy to extend and make it easy for its users to provide their own validation and marshalling functions ("processors" in Vino's parlance). 

# How to use?
Here is a simple scenario to show basic usage.

    # import the schema builders corresponding to JSON data types:
    # primitives (booleans, numbers, strings), arrays, objects
    from vino import prim, arr, obj
    # import some native validating and marshalling processors
    from vino import allowempty, allownull, required, is_str, unmatchedproperties 
    # import some user-defined processors
    from my_validations import email_format, valid_password

    user_registration_schema = obj(
        prim(~required, is_str, allownull, ~allowempty).apply_to('firstname', 'lastname'),
        prim(required, ~allownull, ~allowempty, is_str, email_format).apply_to('email'),
        prim(~required, ~allowempty, ~allowempty, is_str,
             valid_password).apply_to('password'),
        arr(~required, allowempty, ~allownull, maxitems(10),
            prim(~allownull, ~allowempty, is_str).apply_to(range(3)),
        ).apply_to('technologies')
        unmatchedproperties('removed')
    )

    clean_data = user_schema.validate(user_data)

- In the above definition, the "firstname" and "lastname" fields are not required, i.e. they could be missing from the data submitted for validation. If provided, they must be set to a string or `null`, but the empty string is not allowed.

- The "email" field is required, it must be a string, it does not accept null, nor an empty string. In addition, it will be submitted to a user-defined processor to check the validity of the email format.

- The "password" field is also optional, but if provided cannot be set to an empty string or null. In addition, it will be checked for validity by a user-defined processor.

- The "technologies" field is not required, but if provided must be an array. It can be empty, but cannot be null. It must be limited to 10 items. Its first 3 items must be strings and cannot be empty or null.

- all extra (undeclared) properties on the main object will be removed from the returned data.


# not required (can, cannot be empty (empty string), but can be null

    
