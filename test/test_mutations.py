from collections import defaultdict
from test import ODMTestCase, DB
from test.models import User
from pymodm.mutations import Set, Unset, MutationsTracker



class TestSetMutation(ODMTestCase):
    def test_add_operation(self):
        mutation = Set(User.lname, 'doe')
        operations = defaultdict(dict)
        mutation.add_operation(operations)
        self.assertEqual(operations, {'$set': {'lname': 'doe'}})


class TestUnsetMutation(ODMTestCase):
    def test_add_operation(self):
        mutation = Unset(User.lname)
        operations = defaultdict(dict)
        mutation.add_operation(operations)
        self.assertEqual(operations, {'$unset': {'lname': ''}})


class TestMutationsTracker(ODMTestCase):
    def setUp(self):
        self._tracker = MutationsTracker()

    def test_track_set(self):
        self._tracker.track_set(User.lname, 'doe')
        operations = self._tracker.get_operations()
        self.assertEqual(operations, {'$set': {'lname': 'doe'}})

    def test_track_unset(self):
        self._tracker.track_unset(User.lname)
        operations = self._tracker.get_operations()
        self.assertEqual(operations, {'$unset': {'lname': ''}})

    def test_get_operations_with_multiple_fields(self):
        self._tracker.track_set(User.lname, 'doe')
        self._tracker.track_set(User.fname, 'john')
        self._tracker.track_unset(User.phone)

        operations = self._tracker.get_operations()
        self.assertEqual(operations, {
            '$unset': {'phone': ''},
            '$set': {'lname': 'doe', '_id': 'john'}
        })
