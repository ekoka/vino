## /!\ This library is a WIP
Being a validation library, I feel compelled to post this warning, while I'm writing its documentation. I think it's a great tool and I already use it myself in my own personal projects, but that's because I built it and know all its nooks and cranes :) Feel free to download the code to play in *non-critical* settings.

# Vino: a data validation toolkit

### In Vino Veritas (In wine lies the truth)

**Vino** (pronounced vee-noh) is a Python data validation toolkit that aims to be quick to learn, intuitive to use, while also providing enough flexibility to cover a wide range of validation scenarios. It was designed to work mainly with data that is transported and structured in the main JSON data types, namely `Number`, `String`, `Boolean`, `Array`, `Object`, and `null`, once they've been converted to their Python equivalent: `int` or `float`, `string`, `boolean`, `list`, `dict`, and `None`.

---

##### TODO Quick example should go here.

---

Here's an abstract overview of the concepts. A Vino schema is typically made up of 2 types of constructs: *contexts* and *instructions*, arranged together to guide validation in a precise sequence.

```python
schema = ctx(
    ctx(instruction, processor, processor),
    ctx(instruction),
    instruction,
    instruction,
    ctx(instruction, processor, ctx(processor))
    ctx(ctx(instruction), ctx(processor), processor)
    instruction,
)
```

In the schema above the *contexts* represent the data that the schema expects to work with and the containing *instructions* are operations that will be applied to that data.

More concretely, Vino schemas are made up of 4 main components:
- **Primitives**: analogous to the basic JSON data types including *strings*, *booleans*, *numbers* and *null*. The data to validate may be a single value such as `true`, `3.14`, `"john"`, `null`.
- **Objects**: analogous to JSON *objects*. The data to validate can hold a set of named properties that refer to values of any type (*Primitives*, *Arrays*, or other *Objects*).
- **Arrays**: represent JSON *arrays*. The data to validate may contain a collection of unnamed items that can be *Primitives*, *Arrays*, or *Objects*.
- **Processors**: these are constructs that hold the validating or marshalling logic. They're tasked with either validating, transforming, ignoring, or sometimes removing data items submitted for validation.

Except for 3 special cases (discussed a bit later), Vino makes little distinction between processors, they all take the same elements as input, raise some `vino.ValidationError` when they fail to perform their task, and return the valid data on success.

One of the first things you'll notice with Vino is the syntax that doesn't use the popular approach of describing a schema with a dictionary or a class. Vino was designed as a library that is conceptually simple to understand and use, yet flexible and powerful. Something to allow anyone to quickly write some simple functions to validate their data. In that spirit, there is a strong focus in keeping its syntax succinct. It does not, however, prohibits for some wrappers to supplement it with a domain-specific syntax which then proxies to its validation engine.

The simplicity of Vino's syntax is deceptive in its flexibility and what it allows one to do. The following is a demonstration of how one could declare a "User" schema. Note that the example is purposely very explicit and detailed for demonstrative reasons. In reality, there are numerous opportunities for more compact declarations (e.g. through abstractions, reusable constructs, partials, etc).

```python
# first import the 3 basic context constructs: primitive, array, and object
from vino import prim, arr, obj
# then import some validating processors
from vino.processors.validating import (
    required, notrequired,
    allownull, allowempty,
    rejectnull, rejectempty, # aliases for allownull(False) and allowempty(False)
    string, checkuuid,
    maxlength, minlength,
    mustmatch,
)
# then import some marshalling processors
from vino.processors.marshalling import strip, camelcase, stringify

# some custom processors
from .my_validation_utils import emailformat
from .my_marshalling_utils import saltyhash

user_schema = obj(                                                      # (0)
    prim(required, string, strip, allownull, rejectempty, emailformat)
        .apply_to('email')                                              # (1)
    prim(notrequired, string, strip, rejectnull, rejectempty,
         minlength(10), maxlength(500), saltyhash).apply_to('password'), # (2)
    prim(notrequired, string, strip, allownull, rejectempty,
        camelcase).apply_to('first_name', 'last_name')                  # (3)
)
```

0. open an `Object` type context declaration as a global container for our validation. This is typical in real life scenarios since whether for practical reasons or out of necessity, data is often transported as part of an envelope which is usually a JSON object.
1. Next, within our object type context, declare a primitive type context for the `email` property of the object. This declaration opens a context specific to the value being validated. Within that context a number of validation processors are declared. The first is a `required` processor which makes the field mandatory, meaning that it cannot be *missing* from the submitted data. The following `string` processor accepts either `null` or `string` types. If the value is indeed a string, the `strip` processor removes padded whitespaces, else it simply returns the value as it received it. The `allownull` processor explicitly states that `null` values are allowed, the reason for adding this processor will be explained later. The `rejectempty` processor will fail for any empty string. Finally, a user-defined processor supposedly validates the format of the email address. A few things to note here:
    - First, Vino makes a clear distinction between a property that is *missing* (i.e. is absent from the submitted lump of data), a property that is `null`, and a property that is *empty* (only empty strings, empty arrays, and empty objects are considered *empty*). We'll talk more about this in a later section.
    - Second, the type checkers provided directly by Vino (you can provide your own), such as the `string` type checker above, typically allow `null` as a valid value. That is, when checking if a value is a string type, if it's `null` it will pass the check. The rationale here is that since you can combine type checks with another more explicit processor to handle `null`, such as the `rejectnull` processor, it makes sense to let type checks ignore them, as it offers more granularity and more control.
    - Finally, observe that most of Vino's own processors are grouped into either *validating* or *marshalling*. Although they have the same signature and expect to work the same, Vino's validating processors typically do not modify values, they either raise an error on validation, or return the value that they received to mark success. Whereas, Vino's marshalling processors typically do not raise errors, but simply apply their modifications to the data that they're designed to modify. For example, the `strip` marshalling processor only removes whitespace padding from strings. If something is not a string, it does nothing and simply returns the value it received. Of course, you're free to handle things differently in your own processors. Vino expects processors to all have the same signature and mechanism and Vino does not enforce a particular philosophy.
2. The `password` property is validated in a primitive type context. Its first processor explicitly flags it as a property that *is not required*, which means that it's an optional property and if absent from the validated data, its entire validation chain will simply be skipped. The subsequent processors are self explanatory. The custom `saltyhash` marshalling processor transforms the original password string according to some user-defined rules.
3. Similar rules different fields, with the difference that here the same context is applied to the `first_name` and `last_name` properties.

```python
try:
    sane_data = user_schema.validate(user_data)                     # (4)
    db.update(User, sane_data)                                      # (5)
    user.update(sane_data)
except vino.ValidationError as e:
    raise HTTPError(400, e.msg)                                     # (6)
```

4. The schema is then applied to some untrusted data and if everything goes well, a validated and marshalled version is returned.
5. The sane data is then persisted.
6. In case something wrong happened, an error is raised. In this case the validation message is reused as the error description in the HTTP Error response.

It should be noted that schema objects are not immutable, but to ensure their safe reusability Vino's API makes the mutability explicit, not accidental. So when adding new processors to a Vino schema, you're in fact returning another schema, not extending the current one.

```python
my_schema = obj(
    ...
).add(
    ...
) # this creates another schema, tacking the previous one in front of it.
```

Vino's approach to data validation is that of a script, there's a precise set of processors to follow to arrive at a desired result. If during processing a validating processor can't complete its job, it raises a `ValidationError` with details about what went wrong. Unless specifically configured to do so, marshalling processors do not raise an error on failure. Except for very few exceptions (see `Smart vs Explicit` mode and `Special Processors`), processing happens in the exact order in which the schema and processors are declared.

### Primitives

You create a Primitive construct with `vino.prim()`.

To give an example, here's a simple Primitive with only the `datalist()` processor explicitly added. This processor instructs the schema to only accept its listed values as valid:

```python
import vino
from vino.processors.validating import datalist

v = vino.prim(datalist('banana', 'mango'))
v.validate('orange')                    # raises ValidationError
v.validate('mango')                     # True
```

Some more processors explicitly added.

```python
from vino.processors.validating import (
    allowempty, allownull, string, checkpattern
)
```

You can also create your own processors (see `Processors Creation`). Here's a simple processor to strip white spaces.

```python
strstrip_processor = lambda input: input.strip()
naive_email_pattern = r'^\S+@\S+\.\S+$'
email_schema = vino.prim(
    string,
    strstrip_processor,
    checkpattern(naive_email_pattern),
    allowempty, allownull,
)
email_schema.validate('michael@example.com') # True
```

### Arrays

##### TODO /!\ This section is a work in progress. The API to work with arrays hasn't been settled on yet. The actual current implementation may or may not work according to what's been described here.

You create an `Array` schema with the `vino.arr()` utility. In the next example we want a validator for an array whose items are only allowed to be strings, booleans or null. Note that Vino makes a distinction between *null* values and *empty* values (empty strings, empty arrays, empty object). In this example, although the validator accepts null values, it doesn't also accept empty strings.

```python
import vino
from vino.processors.validating import (
    checktypes, string, boolean, allowempty, allownull
)

arr_schema = vino.arr(
    vino.items(vino.batch(
        checktypes(string, boolean),
        allowempty(False),
        allownull,
    ))
)
arr_schema.validate(['Jen', 'Paula', False, 123])  # fails: int type value
arr_schema.validate(['Jen', ""])                   # fails: empty string
arr_schema.validate(['Jen', None])                 # passes, null allowed
```

In the previous example the schema is declared for all array items at once. It will only accept strings, booleans and null.

When validating an `Array` you're working in two contexts:
1. The context of the `Array` itself as a whole. Validating and marshalling operations include for example min/max length of the collection, sorting of elements, trimming, slicing, splicing of the array, etc.

```python
arr_schema = vino.arr(minlength(4), maxlength(8), my_sorting_fnc)
```
2. The context of the items represented by the `vino.items()` utility.

```python
itemsvalidation = vino.items(...)
arr_schema = vino.arr(
    minlength(4),
    maxlength(8),
    my_sorting_fnc,
    itemsvalidation,
)
```

---

###### TODO review the next two paragraphs to determine which is which.

Validation of array items present some notable exceptions to the usual rules:
    - to validate items of an array you put them in an `items()` construct.
    - all processors that are declared as part of the `batch()` are part of a "bundle" that will be validated in a batch.
    - validation of items within a batch always happens in the ordered sequence of those items.
    - within the `items()` declaration, processors still obey the order of declaration.


Validation of array items present some notable exceptions to the usual rules:
    - to validate items of an array you put them in an `items()` construct.
    - all items that are declared in a `batch()` are part of a "bundle" that will be validated in a batch.
    - validation of items within a bundle always happens in the ordered sequence of those items, not their individual declaration (if any).
    - individual declaration of items in a bundle serves to affect the validation of those specific items, not to give order or priority to their validation.
    - within the bundle declaration (`items()`), processors still do obey the order of declaration.

---

Validating all array items at once is probably the most common use-case, but it's also possible to craft a schema that specifies a declaration for individual items.

```python
from vino.processors import minitems, maxitems
arr_schema = vino.arr(
    items(
        vino.prim(checktypes(string, boolean)),         # validates first item
        vino.prim(checktypes(integer), allownull),      # validates next item,
        vino.obj(allownull(False)),                     # item is an embedded object
        vino.arr(...),                                  # item is an embedded array
        vino.prim(allownull(False)),                    # and so forth...
    ),
    minitems(2),
    maxitems(6),
)
arr_schema.validate(['John', 'Mark', None])             # fails: null not allowed on 3rd item
arr_schema.validate(['John', ""])                       # fails: second item must be an int
arr_schema.validate(['John', None])                     # passes, see explanation next
```

The third validation case passes because, (a) the first and second items conform to the specs, and (b) the remaining items in the schema are not required as per the declaration `minitems(2)`.

What if you have 50 items in your array and you would like to validate the first 48 according to the same rules, and the last 2 with individual ones?

```python
first48 = batch(range=range(48), checktypes(string, integer))
a = vino.arr(
    items(
        first48,
        vino.prim(...),
        vino.arr(...),
    )
)
```

In fact, you can target individual items for validation by passing a list of indices (or an equivalent iterable) as the first attribute to `batch()` or to the `range` parameter.

```python
even = batch(range(0,50,2), string, datalist('red', 'yellow', 'purple'))
odd = batch(range(1,50,2), string, datalist('blue', 'green', 'white'))
a = vino.arr(items(odd, even))
```
----

###### TODO Find a better way to handle the above scenario.
As it is, the validation will first process the even batch then the odd. I'd like something that can process a zipped batch to stay consistent with the scripted character of the library.

One solution would be to apply a flag at the array level to specify the kind of sequencing should be followed for validation. It would specify in which order the data items are validated,
- case 1: iterate through the list of data items and match their position with one or more batches before applying the validation.
- case 2: iterate through the batches and apply validations to each matching item.

---

###  Objects
An `Object` is analogous to a json object and holds a set of named elements:

```python
import vino
from vino.processors.validating import allowempty, ...
from vino.processors.marshalling import extraproperties, remove_property
from .own.validation.funcs import unique_email

user_schema = vino.obj(
    vino.prim('firstname', string, allowempty(False), allownull),
    vino.prim(integer).apply_to('user_id'),
    vino.prim('email', required, string, unique_email, rejectempty, rejectnull),
    # you can place processors for the Object between properties.
    remove_property('user_id'),
    vino.obj('role', ...),
    vino.arr('keys', ...),
    vino.prim('password', ...),
    extraproperties('remove'), # ignore|error|remove
)
```

As seen above, an `Object`'s data properties (`Primitives`, `Arrays` and inner `Objects`) must be named by either specifying the name as the first parameter of their constructor (e.g. `vino.prim('foo', ...)`), or with via the instance's `apply_to()` method (e.g. `vino.prim(...).apply_to('foo')`).

We placed the `remove_property` processor between two properties here simply to illustrate that you can. Sometimes one might need to perform a certain task in the midst of validation. With Vino, you simply need to remember that schema and processors are processed in the order they've been declared.

###  Processors

These are components that process the data provided for validation. They're not limited to simply evaluating the validity of data, they can also transform it to a more suitable purpose. The best way to visualize is with an example. Let's look at the common case of user profile creation and edition. This is a simple idea that can turn pretty complex really fast when you start focusing on the fine lines. In this particular case, at profile creation you want users to provide at the very least an email. That attribute should be mandatory since it'll be used to authenticate members of your service, or to communicate with them if they've lost or haven't created a passowrd yet. Since the email will serve to identify them, you want it to be unique in your database's profile table. Furthermore, you also want the address to be valid since it'll be used for communication, however the only truly practical way to ensure the validity of an email address is to send a verification link to its owner, a step which is beyond the scope of what Vino can do. So for this app, email verification will be limited to a simple typo check.

```python
import vino
from vino.processors import allowempty, allownull, checktype, required, checkformat

user_schema = vino.obj('user',
    vino.p('first_name', checktype('string'), allowempty(False), allownull()),
    vino.p('last_name', checktype('string'), allowempty(False), allownull()),
    # for the unique email check, we specify a user-defined function that
    # will do some quick database querying.
    vino.p('email', required(), checktype('string'), 'strip',
            checkformat('simple_email'), unique_email, allowempty(False),
            allownull(False)),
    vino.p('password', required(), checktype('string'), allowempty(False),
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
```

##### Special validation processes: handling missing fields, empty values, and null.
-  `required()`, which is added as the first processors when absent from the list.
- `allowempty()` and `allownull()`, which are both added at the end of the list when absent from it.
- `checktype()`: As the name implies, this processor checks data items against the types listed during registration in the schema. Note that this processor doesn't care for null values (use the `allownull()` processor for that), except in one specific case, if the only type it accepts is `null`, in which case all other types cause `checktype()` to fail.

```python
schema = prim(name('city'), checktype('string', 'int'), allownull())
prim.validate(None) # will pass
schema = prim(name('city'), checktype('string', 'int'), allownull(False))
schema.validate(None) # will fail
```

##### Boolean processors


These are processors that take `True`/`False` settings. They are implicitly set to `True`. That is, you can set a processor to `True` like this:

```python
mandatory = required()
```

or if you wish to be more explicit

```python
required(True)
```

######  /!\ TODO: I'm not sure if any of the following is implemented. The original syntax made used of the unary operator for negating the boolean operator. E.g. `~allownull` to express `not allownull`.

Boolean `not` can be applied to Boolean processors. That is, the following declaration

```python
vino.p('nickname', required(False), checktype('string'), 'strip',
        checkformat('simple_email'), unique_email, allowempty(False),
        allownull(False))
```

could be rewritten as

```python
    vino.p('nickname', not required(), checktype('string'), 'strip',
            checkformat('simple_email'), unique_email, not allowempty(),
            not allownull())
```

Boolean processors can also just be set by listing their type without instantiating them. So to keep with the above example, it becomes

```python
vino.p('nickname', not required, checktype('string'), 'strip',
        checkformat('simple_email'), unique_email, not allowempty,
        not allownull)
```

##### `Smart` and `Explicit` modes
Vino has two modes designed to be helpful, depending on the way you'd like to be assisted. "Smart" mode, the default, tries to guess the most likely scenario when designing a schema and might automatically include certain processors for convenience, whereas "Explicit" mode stays out of your way (within reason) and requires much more explicit directions. Take this schema for example:

```python
userschema = obj(prim('firstname', string))
```

What should happen with these validation attempts?

```python
# Field set to null value
userschema.validate({"firstname": None})

# Field missing and extra field added
userschema.validate({"email": "me@example.com"})
```

In "Smart" mode a `notrequired` processor will be placed as the first processor in the chain, while `allownull` and `rejectblank` will be queued up after other processors.

You can decide the value of implicit processors that are added by Vino by using the `vino.implicit_defaults()` context manager as such.

```python
with vino.implicit_defaults(allownull=False, allowempty=False, required=False):
    # the following will have its 3 *implicit* processors set to False.
    first_name_schema = prim(name('first_name'))
```

###### /!\ The implicit addition of the above 3 boolean processors by Vino should not be confused with the default value they take when you explicitly declare them without value.

Explicitly creating a boolean processor without specifying `True` or `False` *always* results in it be set to `True`. That is, this is always true `boolean_processor()==boolean_processor(True)`.

The above context manager only affects the values that Vino will set the processors when implicitly adding them to your declaration, when you don't declare them yourself. The context manager will *not* change the default value of your explicitly declared boolean processors.

Let's drive the point home with an example:

```python
with vino.implicit_defaults(allownull=False, allowempty=False, required=False):
    # the next 3 lines will set these boolean processors to True
    null = allownull()
    empty = allowempty()
    mandatory = required()
    null is True and empty is True and mandatory is True # True
    # meanwhile the following will have its 3 *implicit* processors set to False as per the context manager.
    first_name_schema = prim(name('first_name'))
```

---

###### TODO New content to review

---

### How to handle missing, empty and null fields:

It's important to note the subtle nuances between different states a field can be in. Vino makes a distinction between missing, empty and null fields as follows:
- a field can be missing, meaning that it has been specified in the schema, but is not present in the data submitted for validation.
- a field can be empty, meaning that although present in the data to validate, it's holding a value that is empty. Examples of empty values are empty strings, lists, tuples, sets (arrays), dicts (objects). "", [], {}, ()
- a field can be null, meaning that it's present, but holds a null value. `None` is the only value recognized as null in Python.

The distinction might seem pedantic at first, but there are use cases where it comes in handy. A simple example is a field that should be either null or set to something specific other than an empty string (e.g. a database table's foreign key field).

### handling missing fields
When an expected data is not present during validation, it is not automatically considered to be null (or `None`) or empty, since null and empty values can be valid in the schema. Vino considers a value missing at validation time to be undefined. So to be a bit more formal, an undefined value is a value that although specified in the schema, is missing from the data to be validated.

```python
user_schema = obj(
    prim('user_id', integer)),
    prim('firstname', string),
    prim('email', string, email_unique),
    prim('password', string),
)
# password is missing from the data to validate
data = {
    "firstname": "John",
    "lastname": "Doe",
    "email": "john@mail.com",
}
user_schema.validate(data)
```

As you can see in the example, the password field will be missing during validation. Something should be done about that. Three ways to handle missing fields:
1. either it should not be required, in which case it's ignored during validation. This is the default behavior, but for the sake of explicitness:

```python
user_schema = obj(
    ...
    prim('password', notrequired, string),
    ...
)
```

2. or if made a required field, it will raise an error when missing.

```python
user_schema = obj(
    ...
    prim('password', required, string),
    ...
)
```

3. or it could also be required, but given a default value for when it's missing.

```python
user_schema = obj(
    ...
    prim('timezone', required(default='utc'), string),
    ...
)
```

It's generally recommended to put the `required` processor as the first of the chain. Also, the `required` processor only affects `Object` properties. Direct validation of `Primitives` doesn't have much of a purpose without a value present, and presence (or absence) of an item in an `Array` can already be controlled with `minitems()`.

### handling empty fields
Currently strings, arrays and objects can have empty values ("", [] and {} respectively). You can prevent or allow an item to hold such a value with `allowempty`. For practical reasons it was decided that the implicit `allowempty` processor that Vino adds when there are no explicit declaration for it would be set to `False`, for all three types (Object, Array, and Primitive). Although, it generally makes sense to set it to `False` for strings and `True` for arrays and objects, I didn't want to burden the documentation with too many special behaviours. It's just simpler to remember that if you don't specify an `allowempty` processor, Vino will implicitly add `allowempty(False)` (see rules on order of addition in later section).

So the following declaration

```
user_schema = obj(
    ...
    prim('email',
        string,
        allownull,
    ),
    ...
)
```

is prepared as so


```python
user_schema = obj(
    ...
    prim('email',
        required,             # implicitly added by Vino
        string,
        allowempty(False),    # implicitly added by Vino
        allownull,
    ),
    ...
)
```

and validates as so

```
data = {
    "firstname": "John",
    "lastname": "Doe",
    "email": "",            # <-- empty field
    "password": "s3cr3t"
}
validate(data, user_schema) # will fail

data['email'] = None
validate(data, user_schema) # will pass
```

###### TODO explain the rationale in making a distinction between null and empty values

### Handling null values

Only `None` is considered a null value from within Python. Just like with empty values, you can allow or prevent a field to be set to null with `allownull`. When not explicitly specified it will be implicitly added as `allownull(True)` by Vino.

Thus, the following declaration

```python
user_schema = obj(
    ...
    prim('email', string),
    ...
)
```

is prepared as follows.

```python
user_schema = obj(
    ...
    prim('email',
        required,           # implicitly added by Vino
        string,
        allowempty(False),  # implicitly added by Vino
        allownull           # implicitly added by Vino
    ),
    ...
)
```


### How Vino implicitly adds `required`, `allownull`, and `allowempty` in the validation chain

###### TODO: We should apply this to all types Object, Array and Primitive for the sake of reusability.

- If the `required` processor is missing from the validation chain of a schema declaration, Vino will implicitly add it as the first processor of the validation chain. Although the `required` processor seems to make more sense in the context of an object's property's validation scheme, and much less so for a standalone primitive schema, it could be argued that a primitive schema declaration could be reused as part of a an `Object`.

- If the `allownull` processor is missing from the validation processor chain in the schema declaration, Vino will implicitly add `allownull` as the last processor of the chain.

- If the `allowempty` processor is missing from the validation chain, Vino will implicitly add `allowempty`. The processor will be placed as the second to last processor of the validation chain if `allownull` is the last processor, or as the last processor otherwise.

To prevent Vino from implicitly adding either of these 3 processors to the validation chain of an item, add them yourself anywhere in the sequence.

---

###### /!\ If you explicitly declare one of the processors in the processor chain, its implicit counterparts will not be included by Vino. Remember this.

---

Note also that since a processor can be added more than once you can include each of those processors multiple times in the chain. This can be useful if some processors in the chain do some data processing and transformation and you wish to ensure that the post-processed data is still valid.

### Handling validation failure: the `failed` attribute, `throw()`, and `end()` processors
There may be situations where instead of having your validation raise an error you want to handle things differently. You can pass a list of processors to the `failed` attribute:

###### TODO Usage examples

### Modifiers
- default: a `default` modifier is called upon when no value (undef) has been given to the processor it is applied to. It will return a value for the processor to work with.
- override: an `override` modifier applied to a processor will intercept the value passed to the processor. It will then discard, replace, or modify it and will submit the result to the processor.
- failsafe: a `failsafe` modifier, when applied to a processor will intervene after the processor has failed validation. Its returned value is what is passed to the remaining validation chain.

###### TODO: Examples
