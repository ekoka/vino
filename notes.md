#TODO
- Because Vino only understand JSON data types, there's an opportunity to enforce more immutability by deep copying the data submitted for validation and modifying the copy, rather than the orginal.

- versatile schema that accepts any of the three formats, *primitives*, *array*, or *object*, as well as *null* and *_undef*.

- qualifier syntax to express that *all items* should apply (e.g. '\*', 'all', None)

- need to test for contingencies

- need to test for new namedtuple wrapper

- replace allow\* processors and their associated processors with the equivalent rejet\* processors (e.g allownull => notrejectnull, notallownull => rejectnull)

- ensure that validating processors do not output a transformed version of their input, unless "casting" is explicitly specified.  


