import pickle
import os
import math
from node_manager import NodeManager

class BTreeNode:
    def __init__(self, t, leaf=True, node_id=None):
        self.t = t  # Minimum degree
        self.leaf = leaf
        self.keys = []  # List of keys
        self.children = []  # List of child nodes
        self.node_id = node_id # Unique identifier for disk storage

    def insert_non_full(self, key, value, btree):
        i = len(self.keys) - 1
        if self.leaf:
            for idx, (k, _) in enumerate(self.keys):
                if k == key:
                    self.keys[idx] = (key, value)
                    btree.node_manager.update_node(self)
                    return
            self.keys.append((key, value))
            self.keys.sort(key=lambda x: x[0])
            btree.node_manager.update_node(self)
        else:
            while i >= 0 and key < self.keys[i][0]:
                i -= 1
            i += 1
            child_id = self.children[i]
            child = btree.node_manager.load_node(child_id)
            if len(child.keys) == (2 * btree.t) - 1:
                self.split_child(i, btree)
                if key > self.keys[i][0]:
                    i += 1
                child_id = self.children[i]
                child = btree.node_manager.load_node(child_id)
            child.insert_non_full(key, value, btree)

    def split_child(self, i, btree):
        t = btree.t
        y_id = self.children[i]
        y = btree.node_manager.load_node(y_id)
        z = BTreeNode(t, leaf=y.leaf)

        # z gets y's keys from index t onwards
        z.keys = y.keys[t:]
        y.keys = y.keys[:t]

        if not y.leaf:
            z.children = y.children[t:]
            y.children = y.children[:t]

        # Insert z into self.children
        z_id = btree.node_manager.save_node(z)
        self.children.insert(i + 1, z_id)

        # Move y's last key up to self.keys
        self.keys.insert(i, y.keys.pop(-1))

        btree.node_manager.update_node(y)
        btree.node_manager.update_node(self)
        btree.node_manager.update_node(z)

    def traverse(self, btree, results=None):
        if results is None:
            results = []
        for i in range(len(self.keys)):
            if not self.leaf:
                child = btree.node_manager.load_node(self.children[i])
                child.traverse(btree, results)
            results.append(self.keys[i])
        if not self.leaf:
            child = btree.node_manager.load_node(self.children[-1])
            child.traverse(btree, results)
        return results

    def search(self, key, btree):
        i = 0
        while i < len(self.keys) and key > self.keys[i][0]:
            i += 1
        if i < len(self.keys) and self.keys[i][0] == key:
            return self.keys[i][1]
        if self.leaf:
            return None
        else:
            child = btree.node_manager.load_node(self.children[i])
            return child.search(key, btree)
    
    def to_string(self, btree, level=0):
        indent = '  ' * level
        keys_str = ', '.join([str(key) for key, _ in self.keys])
        result = f'{indent}Node(ID={self.node_id}, Keys=[{keys_str}], Leaf={self.leaf})\n'
        if not self.leaf:
            for child_id in self.children:
                child = btree.node_manager.load_node(child_id)
                result += child.to_string(btree, level + 1)
        return result
    
    def __str__(self):
        return f"{self.t = }; {self.leaf = }; {self.keys = }; {self.children = }; {self.node_id = }"


class BTree:
    def __init__(self, t=3, storage_path='data/btree'):
        self.t = t
        self.node_manager = NodeManager(storage_path)
        self.storage_path = storage_path
        self.metadata_file = os.path.join(self.storage_path, 'metadata.pkl')

        os.makedirs(self.storage_path, exist_ok=True)

        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'rb') as f:
                metadata = pickle.load(f)
                self.root_id = metadata['root_id']
        else:
            root = BTreeNode(self.t, leaf=True)
            self.root_id = self.node_manager.save_node(root)
            self._save_metadata()

    def insert(self, key, value):
        root = self.node_manager.load_node(self.root_id)
        if len(root.keys) == (2 * self.t - 1): # TODO: sometimes len(keys) still exceeds this
            new_root = BTreeNode(self.t, leaf=False)
            new_root.children.append(root.node_id)
            new_root.split_child(0, self)
            self.root_id = self.node_manager.save_node(new_root)
            self._save_metadata()
            new_root.insert_non_full(key, value, self)
        else:
            root.insert_non_full(key, value, self)

    def delete(self, key):
        root = self.node_manager.load_node(self.root_id)
        self._delete_recursive(root, key)

        if len(root.keys) == 0 and not root.leaf:
            self.root_id = root.children[0]
            self.node_manager.update_node(root) 
            self.node_manager.delete_node(root.node_id)
            self._save_metadata()

    def search(self, key):
        root = self.node_manager.load_node(self.root_id)
        return root.search(key, self)

    def traverse(self):
        root = self.node_manager.load_node(self.root_id)
        return root.traverse(self)

    def _save_metadata(self):
        with open(self.metadata_file, 'wb') as f:
            pickle.dump({'root_id': self.root_id}, f)

    def _delete_recursive(self, node, key):
        for i, (k, _) in enumerate(node.keys):
            if k == key:
                node.keys.pop(i)
                self.node_manager.update_node(node)

                if len(node.keys) == 0:
                    if node.leaf:
                        return True
                    else:
                        self._promote_child(node, 0)
                        return True
                return True

        if node.leaf:
            return False

        for i in range(len(node.keys)):
            if key < node.keys[i][0]:
                child_id = node.children[i]
                child_node = self.node_manager.load_node(child_id)
                if self._delete_recursive(child_node, key):
                    if len(child_node.keys) == 0:
                        self._promote_child(node, i)
                    return True
                break
        else:
            child_id = node.children[-1]
            child_node = self.node_manager.load_node(child_id)
            if self._delete_recursive(child_node, key):
                if len(child_node.keys) == 0:
                    self._promote_child(node, len(node.keys))
                return True

        return False

    def _promote_child(self, node, index):
        if index < len(node.children):
            child_id = node.children[index]
            child_node = self.node_manager.load_node(child_id)
 
            node.keys.insert(index, child_node.keys.pop(-1))
            self.node_manager.update_node(node)
            self.node_manager.update_node(child_node)
            
            if not child_node.leaf:
                node.children.insert(index + 1, child_node.children.pop(-1))
                self.node_manager.update_node(child_node)

    def __str__(self):
        root = self.node_manager.load_node(self.root_id)
        return root.to_string(self)
