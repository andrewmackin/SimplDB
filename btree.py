# btree.py

import pickle
import os

class BTreeNode:
    def __init__(self, t, leaf=False):
        self.t = t  # Minimum degree (defines the range for number of keys)
        self.leaf = leaf  # Is true when node is leaf. Otherwise false
        self.keys = []  # An array of keys
        self.children = []  # An array of child pointers

    def insert_non_full(self, key, value):
        i = len(self.keys) - 1
        if self.leaf:
            # Insert the new key at the correct location
            self.keys.append((None, None))
            while i >= 0 and key < self.keys[i][0]:
                self.keys[i + 1] = self.keys[i]
                i -= 1
            self.keys[i + 1] = (key, value)
        else:
            # Find the child which is going to have the new key
            while i >= 0 and key < self.keys[i][0]:
                i -= 1
            i += 1
            # Check if the found child is full
            if len(self.children[i].keys) == 2 * self.t - 1:
                self.split_child(i)
                if key > self.keys[i][0]:
                    i += 1
            self.children[i].insert_non_full(key, value)

    def split_child(self, i):
        t = self.t
        y = self.children[i]
        z = BTreeNode(t, y.leaf)
        z.keys = y.keys[t:]  # Copy the last (t-1) keys to z
        y.keys = y.keys[:t - 1]  # Reduce the number of keys in y

        if not y.leaf:
            z.children = y.children[t:]  # Copy the last t children to z
            y.children = y.children[:t]

        self.children.insert(i + 1, z)
        self.keys.insert(i, y.keys[t - 1])

class BTree:
    def __init__(self, t=3, filename=None):
        self.t = t  # Minimum degree
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
            root.insert_non_full(key, value)
        self.save()

    def traverse(self, node=None, results=None):
        if results is None:
            results = []
        if node is None:
            node = self.root
        i = 0
        for i in range(len(node.keys)):
            if not node.leaf:
                self.traverse(node.children[i], results)
            results.append(node.keys[i])
        if not node.leaf:
            self.traverse(node.children[i + 1], results)
        return results

    def save(self):
        if self.filename:
            with open(self.filename, 'wb') as f:
                pickle.dump(self, f)

    def load(self):
        with open(self.filename, 'rb') as f:
            obj = pickle.load(f)
            self.__dict__.update(obj.__dict__)
