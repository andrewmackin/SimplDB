import unittest
import shutil
import os
from btree import BTree, BTreeNode
from node_manager import NodeManager

class TestBTree(unittest.TestCase):

    def setUp(self):
        self.storage_path = 'data'
        shutil.rmtree(self.storage_path, ignore_errors=True)
        os.makedirs(self.storage_path, exist_ok=True)
        self.btree = BTree(t=3, storage_path=self.storage_path)

    def test_btree_node_initialization(self):
        """Test initialization of BTreeNode."""
        node = BTreeNode(t=3)
        self.assertTrue(node.leaf)
        self.assertEqual(node.t, 3)
        self.assertEqual(node.keys, [])
        self.assertEqual(node.children, [])
        self.assertIsNone(node.node_id)

    def test_insert_and_traverse(self):
        """Test insertion and traversal of keys in B-tree."""
        data = {
            1: 'value1',
            2: 'value2',
            3: 'value3',
            4: 'value4',
            5: 'value5'
        }

        for key, value in data.items():
            self.btree.insert(key, value)

        records = self.btree.traverse()
        expected = sorted(data.items())
        self.assertEqual(records, expected, "B-tree traversal does not match expected data.")

    def test_search(self):
        """Test search functionality for existing and non-existing keys."""
        data = {
            10: 'value10',
            20: 'value20',
            5: 'value5',
            6: 'value6',
            12: 'value12',
            30: 'value30',
            7: 'value7',
            17: 'value17'
        }

        for key, value in data.items():
            self.btree.insert(key, value)

        for key, value in data.items():
            result = self.btree.search(key)
            self.assertEqual(result, value, f"Search for key {key} returned incorrect value.")

        self.assertIsNone(self.btree.search(100), "Search for non-existing key should return None.")

    def test_split_child(self):
        """Test splitting of child nodes during insertion."""
        keys = [i for i in range(1, 20)]
        for key in keys:
            self.btree.insert(key, f"value{key}")

        root = self.btree.node_manager.load_node(self.btree.root_id)
        self.assertFalse(root.leaf, "Root should not be a leaf after splits.")
        self.assertGreaterEqual(len(root.children), 2, "Root should have at least two children after splits.")

    def test_delete(self):
        """Test deletion of keys from B-tree."""
        keys = [15, 8, 25, 5, 10, 20, 30]
        for key in keys:
            self.btree.insert(key, f"value{key}")

        self.btree.delete(10)
        result = self.btree.search(10)
        self.assertIsNone(result, "Deleted key should not be found in B-tree.")

        records = self.btree.traverse()
        expected_keys = sorted([k for k in keys if k != 10])
        expected_records = [(k, f"value{k}") for k in expected_keys]
        self.assertEqual(records, expected_records, "B-tree traversal does not match expected data after deletion.")

    def test_insert_duplicate_key(self):
        """Test insertion of duplicate keys updates the value."""
        self.btree.insert(1, 'value1')
        self.btree.insert(1, 'value1_updated')

        result = self.btree.search(1)

        self.assertEqual(result, 'value1_updated', "Duplicate key insertion should update the value.")

    def test_node_manager_save_and_load(self):
        """Test that NodeManager correctly saves and loads nodes."""
        node_manager = NodeManager(self.storage_path)
        node = BTreeNode(t=3, leaf=True)
        node.keys = [(1, 'value1'), (2, 'value2')]
        node.children = []
        node_id = node_manager.save_node(node)

        loaded_node = node_manager.load_node(node_id)
        self.assertEqual(node.keys, loaded_node.keys, "Loaded node keys do not match.")
        self.assertEqual(node.children, loaded_node.children, "Loaded node children do not match.")

    def test_metadata_persistence(self):
        """Test that B-tree metadata persists across instances."""
        self.btree.insert(1, 'value1')

        new_btree = BTree(t=3, storage_path=self.storage_path)
        self.assertEqual(self.btree.root_id, new_btree.root_id, "Root ID should persist across BTree instances.")

    def test_delete_non_existing_key(self):
        """Test that deleting a non-existing key does not affect the tree."""
        keys = [5, 15, 25]
        for key in keys:
            self.btree.insert(key, f"value{key}")

        self.btree.delete(100)
        for key in keys:
            result = self.btree.search(key)
            self.assertIsNotNone(result, f"Key {key} should still exist after attempting to delete non-existing key.")

    def test_delete_from_empty_tree(self):
        """Test that deleting from an empty tree does not cause errors."""
        self.btree.delete(10)
        records = self.btree.traverse()
        self.assertEqual(records, [], "Tree should remain empty after attempting to delete from an empty tree.")

    def test_delete_single_value(self):
        self.btree.insert(5, "value5")

        self.btree.delete(5)
        self.assertIsNone(self.btree.search(5), "Deleted key should not be found in B-tree")
        records = self.btree.traverse()
        self.assertEqual(records, [], "B-tree traversal does not match expected data after deleting key with children.")

    def test_insert_large_number_of_keys(self):
        """Test B-tree with a large number of keys."""
        num_keys = 1000
        for key in range(num_keys):
            self.btree.insert(key, f"value{key}")

        for key in range(num_keys):
            result = self.btree.search(key)
            self.assertEqual(result, f"value{key}", f"Key {key} should have value 'value{key}'.")

    def test_split_root(self):
        """Test that the root node splits correctly when full."""
        keys = list(range(6))
        for key in keys:
            self.btree.insert(key, f"value{key}")

        root = self.btree.node_manager.load_node(self.btree.root_id)
        self.assertFalse(root.leaf, "Root should not be a leaf after splitting.")
        self.assertEqual(len(root.keys), 1, "Root should have one key after splitting.")
        self.assertEqual(len(root.children), 2, "Root should have two children after splitting.")

    def test_traverse_empty_tree(self):
        """Test traversal on an empty tree."""
        records = self.btree.traverse()
        self.assertEqual(records, [], "Traversal of empty tree should return an empty list.")

    def test_delete_key_with_children(self):
        """Test deletion of a key that has children."""
        keys = [10, 20, 30, 40, 50, 60]
        for key in keys:
            self.btree.insert(key, f"value{key}")

        self.btree.delete(20)
        self.assertIsNone(self.btree.search(20), "Deleted key with children should not be found in B-tree.")
        records = self.btree.traverse()
        expected_keys = sorted(keys)
        expected_keys.remove(20)
        expected_records = [(k, f"value{k}") for k in expected_keys]
        self.assertEqual(records, expected_records, "B-tree traversal does not match expected data after deleting key with children.")

    def test_delete_root(self):
        """Test deletion of the root key in the B-tree."""
        keys = [10, 20, 30, 40, 50]
        for key in keys:
            self.btree.insert(key, f"value{key}")
        print(str(self.btree))

        root_before = self.btree.node_manager.load_node(self.btree.root_id)
        self.assertEqual(len(root_before.keys), 5, "Root should have 5 keys before deletion.")

        self.btree.delete(30)
        root_after = self.btree.node_manager.load_node(self.btree.root_id)

        self.assertIsNone(self.btree.search(30), "Deleted key should not be found in B-tree.")

        self.assertEqual(len(root_after.keys), 4, "Root should have 4 keys after deletion.")

        expected_keys_after = sorted([10, 20, 40, 50])
        records_after = self.btree.traverse()
        expected_records_after = [(k, f"value{k}") for k in expected_keys_after]
        self.assertEqual(records_after, expected_records_after, "B-tree traversal does not match expected data after deleting root key.")

    def test_split_child_updates_children(self):
        """Test that splitting a child node correctly updates the parent's children list."""
        for key in range(1, 8):
            self.btree.insert(key, f"value{key}")

        root = self.btree.node_manager.load_node(self.btree.root_id)

        self.assertGreater(len(root.children), 1, "Root should have more than one child after splits.")

        first_child_id = root.children[0]
        first_child = self.btree.node_manager.load_node(first_child_id)

        for key in range(8, 10):
            self.btree.insert(key, f"value{key}")

        root_after_split = self.btree.node_manager.load_node(self.btree.root_id)
        first_child_after_split = self.btree.node_manager.load_node(first_child_id)

        self.assertTrue(len(first_child_after_split.keys) < 3, "First child node should have fewer keys after splitting.")

        self.assertGreater(len(root_after_split.children), 1, "Parent should have more than one child after the split of the first child.")
        
        second_child_id = root_after_split.children[1]
        second_child = self.btree.node_manager.load_node(second_child_id)
        self.assertGreater(len(second_child.keys), 0, "Second child should have keys after split.")

    def tearDown(self):
        shutil.rmtree(self.storage_path, ignore_errors=True)
