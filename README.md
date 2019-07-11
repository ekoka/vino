# /!\ Warning: this library is still a work in progress. 
### As a validation library I feel compelled to tell you to wait until it's been thoroughly reviewed for possible vulnerabilities, before trusting it with sensitive data.
# /!\

# Vino: a data validation toolkit

### In Vino Veritas (In wine lies the truth)

**Vino** (pronounced vee-noh) is a Python data validation toolkit that aims to be quick to learn, intuitive to use, while also providing enough flexibility to cover a wide range of validation scenarios. It was designed to work mainly with data that is transported and structured in the main JSON data types, namely `Number`, `String`, `Boolean`, `Array`, `Object`, and `null`, once they've been converted to their Python equivalent: `int` or `float`, `string`, `boolean`, `list`, `dict`, and `None`. Vino is versatile, you can use it as a library to directly handle validations in your application, or it can become the engine that powers your own validation library that provides a layer of abstraction in the form of an alternative declarative syntax.

### The rational behind Vino: 

Python is blessed with a plethora of high quality libraries to solve all kinds of problems and validation is no exception. For one reason or another, however, I've never been completely satisfied with what existing libraries allow me to do in my applications. I've sometimes wanted a level of control over the validation steps that I've never found. Then one day I sat and I started creating Vino. 

    #TODO quick example should go here

To give a simplified and very abstract overview of the concepts behind a Vino schema, it will typically be made up of 2 types of constructs: contexts and instructions, arranged together to guide validation in a precise sequence.

    schema = ctx(
        ctx(instruction, instruction, instruction),
        ctx(instruction),
        instruction,
        instruction,
        ctx(instruction, instruction, ctx(instruction))
        ctx(ctx(instruction), ctx(instruction), instruction)
        instruction,
    )

In the schema above the *contexts* represent the data that the schema expects to work with and the containing *instructions* are operations that will be applied to that data.

Vino schemas are made up of 4 main components:
- **Values** or **Primitives**: a representation of the basic JSON data types including *strings*, *booleans*, *numbers* and *null*. The data to validate may be a single value such as `true`, `3.14`, `"john"`, `null`.
- **Objects**: a representation of JSON *objects*. The data to validate can hold a set of named properties that refer to values of any type (*Primitives*, *Arrays*, or other *Objects*).
- **Arrays**: represent JSON *arrays*. The data to validate may contain a collection of unnamed items that can be *Primitives*, *Arrays*, or *Objects*.
- **Processors**: these are the constructs that hold the validation logic. They're tasked with either validating, transforming, ignoring, or sometimes removing data items submitted for validation.
    
    # TODO: this excerpt should go under the paragraph discussing creation of Processors

Except for 3 special cases (discussed a bit later), Vino makes little distinction between processors, they all take the same elements as input, raise some `VinoValidation` error when they fail to perform their task, or return the valid data on success.

One of the first things you'll notice with Vino is the syntax that doesn't use the popular approach of describing a schema with a dictionary or a class. Vino was designed to as a library that would be simple to use, yet flexible and powerful. Something to allow anyone to quickly write some simple functions to validate their data. In that spirit, there is a strong focus in keeping its syntax simple. It does not, however, prohibits for some wrappers to provide a supplemental syntax and then proxy to its validation routines.

The simplicity of Vino's syntax is deceptive in its flexibility and what it allows one to do. Here's a very explicit and detailed demonstration of how one could declare a user schema:


```python
# first import the basic data constructs: primitives, arrays, and objects
from vino import prim, arr, obj
# then import some validating processors
from vino.processors.validating import (
    required, notrequired,
    allownull, notallownull, 
    allowempty, notallowempty, 
    string, checkuuid, 
    maxlength, minlength, 
    mustmatch
)
# then import some marshalling processors
from vino.processors.marshalling import (
    strip, camelcase, stringify
)

# some custom processors
from .my_validation_utils import (
    address_schema, 
    check_unique_username, 
    check_email
)

user_schema = obj(                                                      # (0)
    prim(notrequired, checkuuid).apply_to('user_id'),                   # (1)
    prim(required, string, strip allownull, notallowempty, 
         minlength(10), maxlength(20)).apply_to('username')             # (2)
    check_unique_username,                                              # (3)
    prim(notrequired, string, strip, notallownull, notallowempty,
         minlength(10), maxlength(500)).apply_to('password'),           # (4)
    address_schema.apply_to('address'),                                 # (5)
    prim(required, string, strip, allownull, notallowempty, 
        check_email).apply_to('email')                                  # (6)
    prim(notrequired, string, strip, allownull, notallowempty,
         camelcase).apply_to(
            'first_name', 'first-name', 'firstname', 
            'last_name', 'last-name', 'lastname')                       # (7)



try:
    sane_data = user_schema.validate(user_data)                         # (8)
    db.User.get(user_id=sane_data.get('user_id'))                       # (9)
except vino.ValidationError as e:
    raise HTTPError(400, e.msg)                                         # (10)
```

0- open the schema declaration with an object data type. This is typical because, whether for practical reason or out of necessity, data is often transported as part of a wrapping construct which is usually a JSON object.

1- declare a primitive type for the `user_id` field of the object. The primitive declaration opens a context specific to that value. Within that context a number of processing declaration are specified. The value is *not required*, which in Vino's parlance means that it absent from the data being validated. If present, it must pass the uuid check. 

2- we declare a schema for the *user_id* field. primitive values with some sane defaults. That declaration will be reused later for data with similar base requirements. In this case we specify that a value is required and some data should be provided during validation otherwise it will fail; it must be of string type or can be set to None (Vino makes a clear distinction between a value that is *missing* (unspecified) and a value set to `None`), if set to a string it will be stripped of whitespaces on both ends, it must not be set to an empty value (Vino does not consider *missing* or `None` values to be empty. Empty values are empty strings, objects, or arrays)
    
1-  similar to the previous declaration, except that now the value is not required. So if the data is not provided, no error is raised. Validation simply ends on this specific schema and moves on to the next, if any (you could alternately declare a `default` or a fail-safe to run on a processor in the advent it should fail, which would then allow the validation to continue. More on this later.)
2- declaration of an Object schema.
3- we declare a field named `user_id` on the object and we assign a primitive data type to it. Similarly to (1) the item is not required, but must pass a `uuid` check if provided. Thus the data should either be provided as uuid or be completely absent from the data set.
    # (4) field "username" declared using our previous base schema that we extend by specifying `minlength` and `maxlength` processors.
    # (5) 
    # (6)
    # (7)
    # (8)
    # (9)
    # (10)

It should be noted that schema objects are not immutable, but to ensure their safe reusability their API makes the mutability explicit, not accidental. So when adding new processors to a Schema, you're in fact returning another schema, not extending the current one.

    my_schema = obj(
        ...
    ).add(
        ...
    ) # this is creating another schema and tacking the previous one in front of it.

    # for new user data i.e. when user_id is not provided

    # you cannot override a listed processor, you can only add a stricter setting

    # in the above the check_unique_username would be a user-defined 
    # processor that checks wether a `user_id` has been sent with the 
    # data, if not it signals that this is probably a new user data and
    # a check for username unicity is warranted.

Vino's approach to data validation is that of a script, there's a precise set of instructions to follow to arrive at a desired result. It's akin to how a cooking recipe works. In this analogy the Primitives, Arrays and Objects in the schema can be seen as the recommended ingredients from the recipe book, whereas the incoming data represents the actual ingredients you'll be working with, and the Processors are the required steps to achieve what you want, and the resulting data is the cake. If during processing a validating processor can't complete its job, it raises an error with details about what went wrong. Unless specifically configured to do so, marshalling processors do not raise an error on failure. Except for very few exceptions (see Smart vs Explicit mode and Special Processors), processing happens in the exact order in which the schema and processors are declared.

Primitives
----------

You create a Primitive construct with `vino.prim()`.

A simple Primitive with only the `datalist()` processor explicitly added. We want
a validator that will accept only the string 'Vim':

    from vino.processors import datalist
    v = vino.prim(datalist(u'Vim'))
    v.validate(u'Vim')                  # True
    v.validate(u'Emacs')                # raises ValidationError etc...
    # let's not be so dogmatic...
    v = vino.prim(datalist(u'Vim', u'Emacs'))
    v.validate(u'Emacs')                # True

Some more processors explicitly added.

    from vino.processors import allowblank, allownull, checktype, checkpattern

You can also create your own processors. A simple processor to strip white spaces
(see `Processors Creation`).

    def strstrip_processor(input): 
        return input.strip()     
        
    email_pattern = r'^\S+@\S+\.\S+$'

    email_schema = vino.prim(
        checktype('str'), 
        strstrip_processor,
        checkpattern(email_pattern),
        allowblank(False), allownull(True)
    )
    email_schema.validate('michael@sundry.ca') # True


Arrays
------

You create an Array schema with the `vino.arr()` or `vino.a()` constructors.
In the next example we want a validator for an array whose items are only
allowed to be strings, booleans or null. Note that Vino makes a distinction
between null values and empty values (empty strings, empty arrays, empty
object). In this example although the validator accepts null values it doesn't
also accept empty strings.

    from vino.processors import batch, items 
    arr_schema = vino.arr(
        items(batch(
            checktype('str', 'bool'),
            allowempty(False),
            allownull(True)
        ))
    )
    arr_schema.validate(['Jen', 'Paula', False, 123])  # fails: int type value
    arr_schema.validate(['Jen', ""])                   # fails: empty string
    arr_schema.validate(['Jen', None])                 # passes, null allowed

In the previous example the schema is declared for all array items at once. It
will only accept strings, booleans and null.

When validating an Array you're working in two contexts: 
- the context of the Array itself as a whole (min/max length, sorting of
  elements, trimming, slicing, splicing of the array, etc).

    arr_schema = vino.arr(minlength(4), maxlength(8), my_sorting_fnc)

- the context of the items represented by `items()`
    
    itemsvalidation = items(batch(
        checktype('str', obj(...), 'bool', prim(...))
    ))
    arr_schema = vino.arr(
        minlength(4), 
        maxlength(8), 
        my_sorting_fnc, 
        itemsvalidation
    )
    
#############################################################################
####### TODO: review these 2 paragraphs to determine which is which. ########

    Validation of array items present some notable exceptions to the usual rules:
        - to validate items of an array you put them in an `items()` construct.
        - all processors that are declared as part of the `batch()` are part of a "bundle" that will be validated in a batch. 
        - validation of items within a batch always happens in the ordered sequence of those items.
        - within the `items()` declaration, processors still obey the order of declaration.

    ------

    Validation of array items present some notable exceptions to the usual rules:
        - to validate items of an array you put them in an `items()` construct.
        - all items that are declared in a `batch()` are part of a "bundle" that will be validated in a batch. 
        - validation of items within a bundle always happens in the ordered sequence of those items, not their individual declaration (if any).
        - individual declaration of items in a bundle serves to affect the validation of those specific items, not to give order or priority to their validation.
        - within the bundle declaration (`items()`), processors still do obey the order of declaration.

#############################################################################

Validating all array items at once is probably the most common use-case, but
it's also possible to craft a schema that specifies a declaration for
individual items.

    from vino.processors import minitems, maxitems
    arr_schema = vino.arr(
        items(vino.prim(checktype('str', 'bool')),           # validates first item
              vino.prim(checktype('int'), allownull(True)),  # validates next item, 
              vino.obj(allownull(False)),                    # item is an embedded object
              vino.arr(...),                                 # item is an array
              vino.prim(allownull(False)),  # and so forth...
        ),
        minitems(2),
        maxitems(6),
    )
    arr_schema.validate(['John', 'Mark', None]) # fails: null not allowed on 3rd item
    arr_schema.validate(['John', ""])           # fails: second item must be an int
    arr_schema.validate(['John', None])         # passes, see explanation next

The third validation case passes because, (a) the first and second items conform to the specs and (b) the remaining items in the schema are not required as per the declaration `minitems(2)`.

What if you have 50 items in your array and you would like to validate the first 48 according to the same rules, and the last 2 with individual ones?

    first48 = batch(range=range(48), checktype('str', 'int'))
    a = vino.arr(
        items(first48, 
              vino.p(...), 
              vino.a(...),
        )
    )

In fact you can target individual items for validation by passing a list of
indices (or an equivalent iterable) as the first attribute to `batch()` or to the
`range` parameter.

    even = batch(range(0,50,2), checktype('str'), datalist('red', 'yellow', 'purple'))
    odd = batch(range(1,50,2), checktype('str'), datalist('blue', 'green', 'white'))
    a = vino.arr(items(odd, even))

#TODO: 
========
find a better way to handle this. As it is the validation will first
process the even batch then the odd. I'd like something that can process a
zipped batch to stay consistent with the scripted character of the library.

one solution would be to apply a flag at the array level to specify the kind
of sequencing should be followed for validation. It would specify in which
order the data items are validated, 
case 1: iterate through the list of data items and match their position with
one or more batches before applying the validation.
case 2: iterate through the batches and apply validations to each matching
item.
========


- Objects: a representation of a json object, an object holds a set of other
named elements:

    >>> from vino.processors import extraproperties, remove_property
    >>> from my.own.validation.funcs import email_unique
    >>> user_schema = vino.obj(
    ...     vino.p('firstname', checktype('str'), 
    ...         allowempty(False), allownull(True)), 
    ...     vino.p('user_id', checktype('int')),
    ...     vino.p('email', required(), checktype('str'), email_unique,
    ...             allowempty(False), allownull(False)), 
    ...     # you can intersperse processors among properties as well.
    ...     remove_property('user_id'),
    ...     vino.o('role', ...),
    ...     vino.a('keys', ...),
    ...     vino.p('password', ...),
    ...     extraproperties('remove'), # 'ignore'|'error'|'pass'
    ... )


As demonstrted above, an Object's data properties (Primitives, Arrays and
inner Objects) must be named by specifying the name as the first parameter in
the constructor. We placed the remove_property processor between two properties
here simply to illustrate that you can. Sometimes one might need to perform a
certain task in the midst of validation. With Vino, you simply need to
remember that schema and processors are processed in the order they've been
declared.

- Processors
----------
These are components that process the data provided for validation. They're
not limited to simply evaluating the validity of data, they can also transform
it to a more suitable purpose.

The best way to visualize is with an example. Let's look at the common case of
user profile creation and edition. This is a simple idea that can turn pretty
complex really fast when you start focusing on the fine lines.

In this particular case, at profile creation you want users to provide at the
very least an email. That attribute should be mandatory since it'll be used to
authenticate members of your service, or to communicate with them if they've
lost or haven't created a passowrd yet. Since the email will serve to identify
them, you want it to be unique in your database's profile table. Furthermore,
you also want the address to be valid since it'll be used for communication,
however the only truly practical way to ensure the validity of an email
address is to send a verification link to its owner, a step which is beyond
the scope of what Vino can do. So for this app, email verification will be
limited to a simple typo check.

    import vino
    from vino.processors import allowblank, allownull, checktype, required, checkformat

    user_schema = vino.obj('user',
        vino.p('first_name', checktype('string'), allowblank(False), allownull()),
        vino.p('last_name', checktype('string'), allowblank(False), allownull()),
        # for the unique email check, we specify a user-defined function that
        # will do some quick database querying.
        vino.p('email', required(), checktype('string'), 'strip', 
                checkformat('simple_email'), unique_email, allowblank(False), 
                allownull(False)),
        vino.p('password', required(), checktype('string'), allowblank(False),
                allownull(False)),
    )

    # user-defined processor to ensure that the address doesn't yet exist in the database
    from vino import ValidationError 
    from myapp.db import User
    def check_unique_email(value, path=None, fieldname=None, schema=None, data=None):
        u = User.query.processor_by(email=value).first()
        if not u:
            return value
        raise ValidationError(message='email is not unique', value=value, )


- Special validation processes: handling missing fields, blank values, and null.
required(), which is added as the first processors when absent from the list.
allowblank() and allownull(), which are both added at the end of the list when
absent from it.

checktype():
As the name implies, this processor checks data items against the types listed
during registration in the schema. Note that this processor doesn't care for null
values (use the allownull() processor for that), except in one specific case, if
the only type it accepts is `null`, in which case all other types cause `checktype()` 
to fail.

    >>> schema = prim(name('city'), checktype('string', 'int'), allownull())
    >>> prim.validate(None) # will pass
    >>> schema = prim(name('city'), checktype('string', 'int'), allownull(False))
    >>> schema.validate(None) # will fail

Boolean processors:
These are processors that take True/False settings.

They are implicitly set to True, that is you can set a processor to True like this:

    >>> mandatory = required() 

or if you wish to be more explicit 

    >>> required(True)

Boolean `not` can be applied to Boolean processors. That is, the following declaration 

        vino.p('nickname', required(False), checktype('string'), 'strip', 
                checkformat('simple_email'), unique_email, allowblank(False), 
                allownull(False))

could be rewritten as

        vino.p('nickname', not required(), checktype('string'), 'strip', 
                checkformat('simple_email'), unique_email, not allowblank(), 
                not allownull())

Boolean processors can also just be set by listing their type without
instantiating them. So to keep with the above example, it becomes

        vino.p('nickname', not required, checktype('string'), 'strip', 
                checkformat('simple_email'), unique_email, not allowblank, 
                not allownull)
    

- Smart vs Explicit mode
Vino has two modes designed to be helpful depending on the way you'd like to be assisted. Smart mode, the default, tries to guess the most likely scenario when designing a schema and might automatically include certain processors for convenience, whereas Explicit mode stays out of your way (within reason) and requires much more explicit directions. Take this schema for example:

    >>> userschema = obj(prim('firstname', checktype("str")))

what should happen with these validation attempts?
   
    >>> # field set to null value
    >>> userschema.validate({"firstname": None})
    ?
    >>> # field missing and extra field added 
    >>> userschema.validate({"email": "me@example.com"}. 
    ?

In Smart mode a `not required` processor will be placed as the first processor in
the chain, `allownull` and `not allowblank` will be queued up after other processors.

You can decide the default value of implicit processors that are added by Vino by using the `vino.implicit_defaults()` context manager as such.
    >>> with vino.implicit_defaults(allownull=False, allowblank=False, required=False):
    ...     # the following will have its 3 *implicit* processors set to False. 
    ...     first_name_schema = prim(name('first_name')) 

/!\ ATTENTION
The implicit addition of the above 3 processors by Vino should not be confused with
the implicit value they take when you explicitly declare them without value.

Explicitly creating a boolean processor without specifying `True` or `False`
_always_ results in setting it True.

The above context manager only affects the default value that Vino
*implicitly* adds to your declaration when any of the above processors is not
declared. The context manager will *not* change the default value of your
explicitly declared boolean processors. 

Let's drive the point home with some code:

    >>> with implicit_defaults(allownull=False, allowblank=False, required=False):
    ...     # the next 3 lines will set these boolean processors to True
    ...     null = allownull()
    ...     blank = allowblank()
    ...     mandatory = required()
    ...     null is True and blank is True and mandatory is True
    True
    ...
    ...     # meanwhile the following will have its 3 *implicit* processors set to False.
    ...     first_name_schema = prim(name('first_name'))

-----
# TODO: New content to review


- How to handle missing, blank and null fields:

It's important to note the subtle nuances between different states a field can be in. Vino makes a distinction between missing, blank and null fields as follows: 
    - a field can be missing, meaning that it has been specified in the schema, but is not present in the data submitted for validation. 
    - a field can be blank, meaning that although present in the data to
      validate, it's holding a value that is blank. Examples of blank values
      are empty strings, lists, tuples, sets (arrays), dicts (objects). "", [], {}, ()
    - a field can be null, meaning that it's present, but holds a null value. `None` is the only value recognized as null.
The distinction might seem pedantic at first, but there are use cases where it comes in handy. A simple example is a field that should be either null or set to something specific other than an empty string (e.g. a database table's foreign key field).

- handling missing fields
When an expected data is not present during validation, it is not automatically considered to be null (or None) or empty, since null and empty values can be valid in the schema. Vino considers a value missing at validation time to be undefined. So to be a bit more formal, an undefined value is a value that although specified in the schema, is missing from the data to be validated.

    user_schema = obj(
        prim('user_id', checktype('int')),
        prim('firstname', checktype('str')), 
        prim('email', checktype('str'), email_unique),
        prim('password', checktype('str')),
    )

    # password is missing from the data to validate
    data = {
        "firstname": "John",
        "lastname": "Doe",
        "email": "john@mail.com",
    }

    user_schema.validate(data)

As you can see by the example, the password field will be missing during validation. Something should be done about that. Three ways to handle missing fields:
    - either it should not be required, in which case it's ignored during validation, this is the default behavious, but for the sake of explicitness:

    user_schema = obj(
        [...]
        prim('password', not required, checktype('str')),
        [...]
    )


    - or if made a required field, it will raise an error when missing.

    user_schema = obj(
        [...]
        prim('password', required, checktype('str')),
        [...]
    )

    - or it could also be required and given a default value for when it's missing.

    user_schema = obj(
        [...]
        # an example of horrible, horrible security practice
        prim('timezone', required(default='utc'), checktype('str')),
        [...]
    )
    
    - it's generally recommended to put the `required` processor as the first of the chain.
    - Also, the `required` processor only affects object's properties. Direct validation of Primitives doesn't have much of a purspose without a value present, and presence (or absence) of an item in an array can already be controlled with `minitems()`.


- handling empty fields

Currently strings, arrays and objects can have empty values ("", [] and {}
respectively). You can prevent or allow an item to hold such a value with
`allowempty`.

For practical reasons I decided that the implicitly `allowempty` processor that
Vino adds when there are no explicit declaration for it would be set to
`False`, for all three types. Although it generally makes sense to set it to
`False` for strings and `True` for arrays and objects, I didn't want to burden the
documentation with too many special behaviours. It's just simpler to remember
that if you don't specify an `allowempty` processor, Vino will add `not
allowempty` for you as the one before last element of your chain of validation
for all three types.

    user_schema = obj(
        [...]
        prim('email', 
             # required, (implicit)
             checktype('str'), 
             # not allowempty, (implicit)
             allownull
        ),
        [...]
    )

    data = {
        "firstname": "John",
        "lastname": "Doe",
        "email": "",            # <-- empty field
        "password": "s3cr3t"
    }
    validate(data, user_schema) # will fail

    data['email'] = None
    validate(data, user_schema) # will pass

# TODO: explain the rationale in making a distinction between null and empty values

- handling null values
Only `None` is considered a null value from within Python. Just like with
empty values, you can allow or prevent a field to be set to null with
`allownull`. When not explicitly specified it will be implicitly added as
`allownull(True)`.
    
    user_schema = obj(
        [...]
        prim('email', 
             # required,  (implicit)
             checktype('str'), 
             # not allowempty, (implicit)
             # allownull (implicit)
        ),
        [...]
    )



How Vino implicitly adds `required`, `allownull`, and `allowempty` in the validation chain
------------------------------------------------------------------------------------------
- If the `required` processor is missing from the validation chain in the schema
  declaration of a primitive or object's property, Vino will implicitly add it
  as the first processor of the validation chain for that property's or
  primitive's schema.  Although the `required` processor seems to make more sense
  in the context of an object's property's validation scheme, and much less so
  for a standalone primitive schema, it could be argued that a primitive
  schema declaration could be called as a standalone validation in some
  special scenario:

    # our function receives some primitive validation schema to call against
    # some data. The data comes from a service that outputs a list in which
    # missing items are marked with a null. 
    def validate_wrapper(data, primitive_schema):
        for value in data:
            if value is None:
                # we want to treat None value as missing fields
                primitive_schema.validate()
            else:
                primitive_schema.validate(value)
            

- If the processor `allowempty` is missing from the validation processor chain in
  the schema declaration of a primitive, object's property, or specific array
  item, that is declared to be a string, an array, or object Vino will
  implicitly add `not allowempty` as the second to last processor of the
  validation chain for that item. 

- If the processor `allownull` is missing from the validation processor chain in the
  schema declaration of a primitive, object's property, or specific array
  item, Vino will implicitly add `allownull` as the last processor of the
  validation chain for that item.

To prevent Vino from implicitly adding either of these 3 processors to the
validation chain of an item, add them yourself anywhere in the sequence.

    /!\ 
        If you explicitly declare one of the processors in the processor chain, its
        implicit counterparts will not be included by Vino. Remember this.
    /!\

Note also that since a processor can be added more than once you can include each
of those processors multiple times in the chain. This can be useful if some
processors in the chain do some data processing and transformation and you wish
to ensure that the post-processed data is still valid.

-----

Handling Validation Failure
---------------------------
The `failed` attribute and `throw()` and `end()` processors

- there may be situations where instead of having your validation raise an error you want to handle things differently. You can pass a list of processors to the `failed` attribute :

    # TODO: better explain this example
    e.g. Consider the case of a user profile form that you use both for
    registration and for updates. The form has both `password` and
    `confirm_password` fields. If you submit the `password` field you want to
    ensure that the `confirm_password` field also matches. If you don't submit
    `password`, you don't just want the `required` validation to fail, you
    want to first make sure that the user indeed already exists, if it's the
    case you want to end validation for the `password` field and move on to
    the next field.

    from vino.processors import exclude_field, field_match 
    from my.own.processors import check_user_exists
    user_schema = vino.obj(
        ...
        vino.p('user_id', not required, check_user_exists())
        vino.p('password', 
                required(
                    True, 
                    failed=(
                        check_field_exists('user_id'), 
                        end()
                    )
                ), 
                field_match('confirm_password')
        ),
        exclude_field(['user_id']) 
        
    )

In the above example, note how we use the `exclude_field` processor to remove the
value of `user_id` from the returned data. If you think about it after
validating the data, we don't actually want to push the user_id back in the
database. If it's a valid id, then good, we can use it to find the relevant
record to edit, but we'd rather confine the returned data to fields that will
be edited so we need to pop it regardless.

    try:
        result = user_schema.validate(data)
        # we excluded user_id, but we'd still like to work with it
        user_id = result.excluded['user_id']
        user = User.query.get(user_id)
        user.update(**result.data)
        user.save()
    except vino.ValidationError as e:
        # handle validation failure here
        pass
    except DBError as e:
        # handle db failure here
        pass


-----
- validation order

    - Extra fields
    - Required or Default 
    - type

    - pre_validation
    - empty, null
    - post_validation
"""

---
# Modifiers:
- default: 
    a `default` modifier will be called upon when no value (undef) has been given to the processor it is applied to. It will return a value for the processor to work with.

- override: 
    an `override` modifier applied to a processor will intercept the value passed to the processor. It will then discard, replace, or modify it and will submit the result to the processor.

- failsafe: 
    a `failsafe` modifier, when applied to a processor will intervene after the processor has failed validation. Its returned value is what is passed to the remaining validation chain.

