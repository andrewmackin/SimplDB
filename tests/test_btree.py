import unittest
import shutil
import os
from btree import BTree, BTreeNode
from node_manager import NodeManager

class TestBTree(unittest.TestCase):

    def setUp(self):
        self.storage_path = 'test_data_btree'
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
        # Insert key-value pairs
        data = {
            1: 'value1',
            2: 'value2',
            3: 'value3',
            4: 'value4',
            5: 'value5'
        }

        for key, value in data.items():
            self.btree.insert(key, value)

        # Traverse the B-tree and verify the order
        records = self.btree.traverse()
        expected = sorted(data.items())
        self.assertEqual(records, expected, "B-tree traversal does not match expected data.")

    def test_search(self):
        """Test search functionality for existing and non-existing keys."""
        # Insert key-value pairs
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

        print(str(self.btree))

        # Search for existing keys
        for key, value in data.items():
            result = self.btree.search(key)
            self.assertEqual(result, value, f"Search for key {key} returned incorrect value.")

        # Search for a non-existing key
        self.assertIsNone(self.btree.search(100), "Search for non-existing key should return None.")

    def test_split_child(self):
        """Test splitting of child nodes during insertion."""
        # Insert keys to force node splits
        keys = [i for i in range(1, 20)]
        for key in keys:
            self.btree.insert(key, f"value{key}")

        # Check that root has children after splits
        root = self.btree.node_manager.load_node(self.btree.root_id)
        self.assertFalse(root.leaf, "Root should not be a leaf after splits.")
        self.assertGreaterEqual(len(root.children), 2, "Root should have at least two children after splits.")

    def test_delete(self):
        """Test deletion of keys from B-tree."""
        # Insert keys
        keys = [15, 8, 25, 5, 10, 20, 30]
        for key in keys:
            self.btree.insert(key, f"value{key}")

        # Delete a key
        self.btree.delete(10)
        result = self.btree.search(10)
        self.assertIsNone(result, "Deleted key should not be found in B-tree.")

        # Verify traversal after deletion
        records = self.btree.traverse()
        expected_keys = sorted([k for k in keys if k != 10])
        expected_records = [(k, f"value{k}") for k in expected_keys]
        self.assertEqual(records, expected_records, "B-tree traversal does not match expected data after deletion.")

    def test_insert_duplicate_key(self):
        """Test insertion of duplicate keys updates the value."""
        # Insert a key
        self.btree.insert(1, 'value1')
        # Insert duplicate key with a different value
        self.btree.insert(1, 'value1_updated')
        # Search for the key and check the value
        result = self.btree.search(1)
        self.assertEqual(result, 'value1_updated', "Duplicate key insertion should update the value.")

    def test_node_manager_save_and_load(self):
        """Test that NodeManager correctly saves and loads nodes."""
        node_manager = NodeManager(self.storage_path)
        node = BTreeNode(t=3, leaf=True)
        node.keys = [(1, 'value1'), (2, 'value2')]
        node.children = []
        node_id = node_manager.save_node(node)

        # Load the node back
        loaded_node = node_manager.load_node(node_id)
        self.assertEqual(node.keys, loaded_node.keys, "Loaded node keys do not match.")
        self.assertEqual(node.children, loaded_node.children, "Loaded node children do not match.")

    def test_metadata_persistence(self):
        """Test that B-tree metadata persists across instances."""
        # Insert a key to ensure root_id is set
        self.btree.insert(1, 'value1')

        # Create a new BTree instance to simulate restarting the application
        new_btree = BTree(t=3, storage_path=self.storage_path)
        # Check that the root_id is the same
        self.assertEqual(self.btree.root_id, new_btree.root_id, "Root ID should persist across BTree instances.")

    def test_delete_non_existing_key(self):
        """Test that deleting a non-existing key does not affect the tree."""
        # Insert some keys
        keys = [5, 15, 25]
        for key in keys:
            self.btree.insert(key, f"value{key}")

        # Attempt to delete a non-existing key
        self.btree.delete(100)
        # Ensure existing keys are still present
        for key in keys:
            result = self.btree.search(key)
            self.assertIsNotNone(result, f"Key {key} should still exist after attempting to delete non-existing key.")

    def test_delete_from_empty_tree(self):
        """Test that deleting from an empty tree does not cause errors."""
        # Attempt to delete from an empty tree
        self.btree.delete(10)
        # Ensure tree is still empty
        records = self.btree.traverse()
        self.assertEqual(records, [], "Tree should remain empty after attempting to delete from an empty tree.")

    # def test_insert_large_number_of_keys(self):
    #     """Test B-tree with a large number of keys."""
    #     # Insert a large number of keys
    #     num_keys = 1000
    #     for key in range(num_keys):
    #         self.btree.insert(key, f"value{key}")

    #     # Verify that all keys are present
    #     for key in range(num_keys):
    #         result = self.btree.search(key)
    #         self.assertEqual(result, f"value{key}", f"Key {key} should have value 'value{key}'.")

    def test_split_root(self):
        """Test that the root node splits correctly when full."""
        # Insert keys to fill the root node and cause a split
        keys = [1, 2, 3, 4, 5]
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

    def tearDown(self):
        shutil.rmtree(self.storage_path, ignore_errors=True)
