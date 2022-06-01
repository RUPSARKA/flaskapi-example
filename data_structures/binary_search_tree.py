class Blogpost:
    def __init__(self, id, title, body, date=None, user_id=None):
        self.id = id
        self.title = title
        self.body = body
        self.date = date
        self.user_id = user_id


class BSTnode:
    def __init__(self, key, value=None):
        self.key = key
        self.value = value
        self.left = None
        self.right = None
        self.parent = None

def insert(node, key, value):
    if node is None:
        node = BSTnode(key, value)
    elif key < node.key:
        node.left = insert(node.left, key, value)
        node.left.parent = node
    elif key > node.key:
        node.right = insert(node.right, key, value)
        node.right.parent = node
    return node

def find(node, key):
    if node is None:
        return None
    if key == node.key:
        return node
    if key < node.key:
        return find(node.left, key)
    if key > node.key:
        return find(node.right, key)

def update(node, key, value):
    target = find(node, key)
    if target is not None:
        target.value = value


def display_keys(node, space='\t', level=0):
    # print(node.key if node else None, level)

    # If the node is empty
    if node is None:
        print(space * level + '∅')
        return

        # If the node is a leaf
    if node.left is None and node.right is None:
        print(space * level + str(node.key))
        return

    # If the node has children
    display_keys(node.right, space, level + 1)
    print(space * level + str(node.key))
    display_keys(node.left, space, level + 1)

def list_all(node):
    if node is None:
        return []
    return list_all(node.left) + [(node.key, node.value)] + list_all(node.right)


def make_balanced_bst(data, lo=0, hi=None, parent=None):
    if hi is None:
        hi = len(data) - 1
    if lo > hi:
        return None

    mid = (lo + hi) // 2
    key, value = data[mid]

    root = BSTnode(key, value)
    root.parent = parent
    root.left = make_balanced_bst(data, lo, mid - 1, root)
    root.right = make_balanced_bst(data, mid + 1, hi, root)

    return root

def balance_bst(node):
    return make_balanced_bst(list_all(node))


class TreeMap():
    def __init__(self):
        self.root = None

    def __setitem__(self, key, value):
        node = find(self.root, key)
        if not node:
            self.root = insert(self.root, key, value)
            self.root = balance_bst(self.root)
        else:
            update(self.root, key, value)

    def __getitem__(self, key):
        node = find(self.root, key)
        return node.value if node else None

    def __iter__(self):
        return (x for x in list_all(self.root))

    def search(self, key):
        return find(self.root, key)

    def display(self):
        return display_keys(self.root)

"""treemap = TreeMap()
treemap['1'] = Blogpost(id=1, title='aakash', body='Aakash Rai', date='aakash@example.com')
treemap['2'] = Blogpost(id=2, title='biraj', body='Biraj Das', date='biraj@example.com')
treemap.display()"""