import os
import pickle

class NodeManager:
    def __init__(self, storage_path):
        self.storage_path = storage_path
        os.makedirs(self.storage_path, exist_ok=True)
        self.node_id_counter = self._get_initial_node_id()

    def _get_initial_node_id(self):
        if not os.listdir(self.storage_path):
            return 0
        else:
            existing_ids = [int(fname.split('.')[0]) for fname in os.listdir(self.storage_path) if fname.endswith('.node')]
            return max(existing_ids) + 1 if existing_ids else 0

    def save_node(self, node):
        node_id = self.node_id_counter
        node.node_id = node_id
        filepath = os.path.join(self.storage_path, f"{node_id}.node")
        with open(filepath, 'wb') as f:
            pickle.dump(node, f)
        self.node_id_counter += 1
        return node_id

    def load_node(self, node_id):
        filepath = os.path.join(self.storage_path, f"{node_id}.node")
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Node file {filepath} does not exist.")
        with open(filepath, 'rb') as f:
            node = pickle.load(f)
        return node

    def update_node(self, node):
        filepath = os.path.join(self.storage_path, f"{node.node_id}.node")
        with open(filepath, 'wb') as f:
            pickle.dump(node, f)

    def delete_node(self, node_id):
        """Deletes the node file from disk."""
        filepath = os.path.join(self.storage_path, f"{node_id}.node")
        if os.path.exists(filepath):
            os.remove(filepath)
        else:
            raise FileNotFoundError(f"Node file {filepath} does not exist.")
