class tree_node:
    def __init__(self, data = None):
        self.data = data
        self.is_end = False
        self.children = {}

class D_tree:
    def __init__(self):
        self.root = tree_node()

    def check(self, id):
        node = self.root
        result = 0  #-1 for not exist, 0 for judging
        for ch in id:
            if ch in node.children.keys():
                node = node.children[ch]
            else:
                result = -1
                node.children[ch] = tree_node(ch)
                node = node.children[ch]
        if result == 0:
            if node.is_end:
                return True
        node.is_end = True
        return False