from dataclasses import dataclass

from connector import loadResidents


@dataclass
class Node:
    rid: int

    def __init__(self, rid: int):
        self.rid = rid

    def __eq__(self, other):
        return self.rid == other.rid


@dataclass
class Edge:
    dest: Node
    amount: float

    def __init__(self, dest: Node, amount: float = 0.0):
        self.dest = dest
        self.amount = amount

    def __eq__(self, other):
        return self.dest == other.dest


node_list: [Node] = []
edge_list: [[Edge]] = [[]]


def construct_graph_from_bills(bills):
    global node_list
    node_list = list(map(lambda r: Node(r.rID), loadResidents()))

    for bill in bills:
        process_bill(bill)
    symmetric_edge_elimination()
    transitive_edge_elimination()


def process_bill(bill):
    index = node_list.index(bill)
    # TODO add variable counts of creditors here
    share = bill.amount / len(node_list)
    for i in range(len(node_list)):
        if index == i:
            continue
        edge = Edge(dest=node_list[index], amount=share)
        if edge in edge_list[i]:
            edge_index = edge_list[i].index(edge)
            edge_list[i][edge_index].amount += share
        else:
            edge_list[i].append(edge)


def symmetric_edge_elimination():
    for node_index in range(len(edge_list)):
        edges = find_symmetric_edges(node_index)
        for edge in edges:
            eliminate_symmetric_edges(*edge)


def find_symmetric_edges(src_index: int):
    edges: [(int, int, int, int)] = []
    for src_edge_index in range(len(edge_list[src_index])):
        dest_node = edge_list[src_index][src_edge_index].dest
        dest_index = node_list.index(dest_node)
        if not Edge(node_list[src_index]) in edge_list[dest_index]:
            continue
        dest_edge_index = edge_list[dest_index].index(Edge(node_list[src_index]))
        # edges edge_list[src_index][src_edge_index] and edge_list[dest_index][dest_edge_index] are symmetric!
        edges.append((src_index, src_edge_index, dest_index, dest_edge_index))
    return edges


# noinspection PyUnresolvedReferences
def eliminate_symmetric_edges(src_index, src_edge_index, dest_index, dest_edge_index):
    if edge_list[src_index][src_edge_index].amount < edge_list[dest_index][dest_edge_index].amount:
        edge_list[dest_index][dest_edge_index].amount -= edge_list[src_index][src_edge_index].amount
        edge_list[src_index].pop(src_edge_index)
    else:
        edge_list[src_index][src_edge_index] -= edge_list[dest_index][dest_edge_index].amount
        edge_list[dest_index].pop(dest_edge_index)


def transitive_edge_elimination():  # TODO continue here
    raise NotImplementedError


def test():
    node1 = Node(0)
    node2 = Node(1)
    node3 = Node(2)
    edge1 = Edge(dest=node2, amount=4)
    edge2 = Edge(dest=node3, amount=7)
    edge3 = Edge(dest=node1, amount=12)
    edge4 = Edge(dest=node1, amount=17)

    global node_list, edge_list
    node_list = [node1, node2, node3]
    edge_list = [[edge1], [edge2, edge4], [edge3]]
    symmetric_edge_elimination()


test()
