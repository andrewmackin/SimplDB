import pickle
import os

class BTreeNode:
    def __init__(self, t, leaf=False):
        self.t = t  # Minimum degree
        self.leaf = leaf
        self.keys = []  # List of keys
        self.children = []  # List of child nodes

    def insert_non_full(self, key, value):
        i = len(self.keys) - 1
        if self.leaf:
            # Check for existing key
            for idx, (k, _) in enumerate(self.keys):
                if k == key:
                    # Key exists, update value
                    self.keys[idx] = (key, value)
                    return
            self.keys.append((key, value))
            self.keys.sort(key=lambda x: x[0])
        else:
            # Find child to insert into
            while i >= 0 and key < self.keys[i][0]:
                i -= 1
            i += 1
            # Check if child is full
            if len(self.children[i].keys) == 2 * self.t - 1:
                self.split_child(i)
                if key > self.keys[i][0]:
                    i += 1
            self.children[i].insert_non_full(key, value)

    def split_child(self, i):
        t = self.t
        y = self.children[i]
        z = BTreeNode(t, y.leaf)
        z.keys = y.keys[t:]  # Last (t-1) keys to z
        y.keys = y.keys[:t - 1]  # Reduce keys in y

        if not y.leaf:
            z.children = y.children[t:]
            y.children = y.children[:t]

        self.children.insert(i + 1, z)
        self.keys.insert(i, y.keys[t - 1])

    def delete_key(self, key):
        # TODO: Implement B-Tree Deletion Alg
        pass

class BTree:
    def __init__(self, t=3, filename=None):
        self.t = t
        self.root = None
        self.filename = filename
        if filename and os.path.exists(filename):
            self.load()
        else:
            self.root = BTreeNode(t, leaf=True)

    def search(self, k, node=None):
        if node is None:
            node = self.root
        i = 0
        while i < len(node.keys) and k > node.keys[i][0]:
            i += 1
        if i < len(node.keys) and k == node.keys[i][0]:
            return node.keys[i][1]
        elif node.leaf:
            return None
        else:
            return self.search(k, node.children[i])

    def insert(self, key, value):
        root = self.root
        if len(root.keys) == (2 * self.t) - 1:
            temp = BTreeNode(self.t)
            temp.children.insert(0, root)
            temp.leaf = False
            temp.split_child(0)
            self.root = temp
            self.root.insert_non_full(key, value)
        else:
            self.root.insert_non_full(key, value)
        self.save()

    def traverse(self, node=None, results=None):
        if results is None:
            results = []
        if node is None:
            node = self.root
        for i in range(len(node.keys)):
            if not node.leaf:
                self.traverse(node.children[i], results)
            results.append(node.keys[i])
        if not node.leaf:
            self.traverse(node.children[-1], results)
        return results

    def delete(self, key):
        # Simplified deletion: Rebuild the tree without the key
        all_records = self.traverse()
        self.root = BTreeNode(self.t, leaf=True)
        for k, v in all_records:
            if k != key:
                self.insert(k, v)
        self.save()

    def save(self):
        if self.filename:
            with open(self.filename, 'wb') as f:
                pickle.dump(self, f)  # Save the entire BTree object

    def load(self):
        with open(self.filename, 'rb') as f:
            obj = pickle.load(f)
            self.__dict__.update(obj.__dict__)
