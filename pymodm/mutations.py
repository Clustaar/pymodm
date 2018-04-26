from collections import defaultdict
from abc import ABCMeta, abstractmethod


class Mutation(object):
    __metaclass__ = ABCMeta

    def __init__(self, field):
        self._field = field

    @abstractmethod
    def add_operation(self, operations):
        """Adds a dict representing the mongodb operation that
        must take place in order to save the change in DB into the operations dict.

        :parameters:
          - `operations`: dict of mongodb operations
        """


class Set(Mutation):
    """Mutation that take place when a field is updated with a new value"""
    _operation = '$set'

    def __init__(self, field, value):
        super(Set, self).__init__(field)
        self._value = value

    def add_operation(self, operations):
        """Adds a $set operation for the field that changed

        :parameters:
          - `operations`: dict of mongodb operations
        """
        operations.setdefault(self._operation, {})
        operations[self._operation][self._field.mongo_name] = self._field.to_mongo(self._value)


class Unset(Mutation):
    """Mutation that take place when a field has been deleted from an object"""
    _operation = '$unset'

    def add_operation(self, operations):
        """Adds a $unset operation for the field that changed

        :parameters:
          - `operations`: dict of mongodb operations
        """
        operations.setdefault(self._operation, {})
        operations[self._operation][self._field.mongo_name] = ''


class MutationsTracker(object):
    """Object tracking changes of a MongoModel objects.
    It's used for updating only the fields that were changed on the model instance.
    """
    def __init__(self):
        self._mutations = {}

    def track_set(self, field, value):
        """Track a change that must result in a $set operation

        :parameters:
          - `field`: field that changed
          - `value`: new value
        """
        self._mutations[field.attname] = Set(field, value)

    def track_unset(self, field):
        """Track a change that must result in an $unset operation

        :parameters:
          - `field`: field that changed
        """
        self._mutations[field.attname] = Unset(field)

    def reset(self):
        """Reset object as no mutations have taken place"""
        self._mutations = {}

    def get_operations(self):
        """Returns the mongoDB operations that must
        take place to update an object.
        """
        operations = {}
        for mutation in self._mutations.values():
            mutation.add_operation(operations)

        return operations
