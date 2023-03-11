from pyformlang.finite_automaton import EpsilonNFA
from scipy import sparse
from scipy.sparse import dok_matrix, kron


class BooleanAdjacencyMatrix:
    def __init__(self, nfa: EpsilonNFA = None):
        self.adj_matrices = {}
        self.num_states = 0
        self.start_states = dok_matrix((1, 0), dtype=bool)
        self.final_states = dok_matrix((1, 0), dtype=bool)
        if nfa:
            self._build_adjacency_matrices(nfa)

    def _build_adjacency_matrices(self, nfa: EpsilonNFA) -> None:
        num_states = len(nfa.states)
        self.num_states = num_states
        states = {state: ind for ind, state in enumerate(nfa.states)}
        for start, final_dict in nfa.to_dict().items():
            for label, final_states in final_dict.items():
                if not isinstance(final_states, set):
                    final_states = {final_states}
                for final in final_states:
                    if label not in self.adj_matrices:
                        self.adj_matrices[label] = dok_matrix(
                            (num_states, num_states), dtype=bool
                        )
                    self.adj_matrices[label][states[start], states[final]] = True
        self.start_states = dok_matrix((1, num_states), dtype=bool)
        self.final_states = dok_matrix((1, num_states), dtype=bool)
        self.start_states[0, [states[i] for i in nfa.start_states]] = True
        self.final_states[0, [states[i] for i in nfa.final_states]] = True

    def to_nfa(self) -> EpsilonNFA:
        res = EpsilonNFA()
        for label in self.adj_matrices:
            for start, final in zip(*self.adj_matrices[label].nonzero()):
                res.add_transition(start, label, final)
        for i in self.start_states.nonzero()[1]:
            res.add_start_state(i)
        for i in self.final_states.nonzero()[1]:
            res.add_final_state(i)
        return res

    def get_intersection(
        self, other: "BooleanAdjacencyMatrix"
    ) -> "BooleanAdjacencyMatrix":
        intersected_matrix = BooleanAdjacencyMatrix()
        cross_labels = self.adj_matrices.keys() & other.adj_matrices.keys()
        for label in cross_labels:
            intersected_matrix.adj_matrices[label] = kron(
                self.adj_matrices[label], other.adj_matrices[label]
            )

        intersected_matrix.num_states = self.num_states * other.num_states
        intersected_matrix.start_states = kron(self.start_states, other.start_states)
        intersected_matrix.final_states = kron(self.final_states, other.final_states)
        return intersected_matrix

    def get_transitive_closure(self) -> dok_matrix:
        tc_matrix = sum(self.adj_matrices.values())
        prev = 0
        while tc_matrix.count_nonzero() != prev:
            prev = tc_matrix.count_nonzero()
            tc_matrix += tc_matrix @ tc_matrix
        return tc_matrix
