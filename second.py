from typing import Set, Dict, List, Tuple, Optional
from collections import defaultdict
import itertools
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx


class FiniteAutomaton:

    def __init__(self):
        self.states: Set[str] = set()
        self.alphabet: Set[str] = set()
        self.transitions: Dict[str, Dict[str, Set[str]]] = defaultdict(lambda: defaultdict(set))
        self.initial_state: str = ""
        self.final_states: Set[str] = set()
        self.is_deterministic: bool = True

    @classmethod
    def create_variant9(cls):
        fa = cls()

        fa.states = {"q0", "q1", "q2", "q3", "q4"}
        fa.alphabet = {"a", "b", "c"}
        fa.final_states = {"q4"}
        fa.initial_state = "q0"

        fa.add_transition("q0", "a", "q1")
        fa.add_transition("q1", "b", "q2")
        fa.add_transition("q1", "b", "q3")
        fa.add_transition("q2", "c", "q0")
        fa.add_transition("q3", "a", "q4")
        fa.add_transition("q3", "b", "q0")

        fa.check_deterministic()
        return fa

    def add_transition(self, from_state: str, symbol: str, to_state: str):
        if from_state not in self.states:
            self.states.add(from_state)
        if to_state not in self.states:
            self.states.add(to_state)
        if symbol not in self.alphabet:
            self.alphabet.add(symbol)
        self.transitions[from_state][symbol].add(to_state)

    def check_deterministic(self):
        self.is_deterministic = True
        for state in self.states:
            for symbol, targets in self.transitions[state].items():
                if len(targets) > 1:
                    self.is_deterministic = False
                    return

    def to_regular_grammar(self):
        grammar = RegularGrammar()
        grammar.non_terminals = set(self.states)
        grammar.terminals = set(self.alphabet)
        grammar.start_symbol = self.initial_state
        grammar.productions = {}

        for state in self.states:
            productions = []
            for symbol, targets in self.transitions[state].items():
                for target_state in targets:
                    productions.append(symbol + target_state)
            if state in self.final_states:
                productions.append("ε")
            grammar.productions[state] = productions

        return grammar

    def to_dfa(self):
        if self.is_deterministic:
            print("Automaton is already deterministic")
            return self

        dfa = FiniteAutomaton()
        dfa.alphabet = set(self.alphabet)

        dfa_state_map = {}
        reverse_state_map = {}

        initial_set = frozenset([self.initial_state])
        dfa_state_map[initial_set] = "A"
        reverse_state_map["A"] = initial_set
        dfa.states.add("A")

        queue = [initial_set]
        state_counter = 1

        while queue:
            current_set = queue.pop(0)
            current_dfa_state = dfa_state_map[current_set]

            for symbol in self.alphabet:
                next_set = set()
                for ndfa_state in current_set:
                    if symbol in self.transitions[ndfa_state]:
                        next_set.update(self.transitions[ndfa_state][symbol])

                if next_set:
                    next_frozenset = frozenset(next_set)
                    if next_frozenset not in dfa_state_map:
                        new_state_name = chr(ord('A') + (state_counter % 26))
                        if state_counter >= 26:
                            new_state_name += str(state_counter // 26)
                        state_counter += 1
                        dfa_state_map[next_frozenset] = new_state_name
                        reverse_state_map[new_state_name] = next_frozenset
                        queue.append(next_frozenset)
                        dfa.states.add(new_state_name)

                    next_dfa_state = dfa_state_map[next_frozenset]
                    dfa.add_transition(current_dfa_state, symbol, next_dfa_state)

        dfa.final_states = set(
            dfa_state
            for ndfa_set, dfa_state in dfa_state_map.items()
            if not ndfa_set.isdisjoint(self.final_states)
        )

        dfa.initial_state = "A"
        dfa.is_deterministic = True
        return dfa

    def print_automaton(self):
        print("Finite Automaton:")
        print(f"States: {sorted(self.states)}")
        print(f"Alphabet: {sorted(self.alphabet)}")
        print(f"Initial State: {self.initial_state}")
        print(f"Final States: {sorted(self.final_states)}")
        print(f"Deterministic: {self.is_deterministic}")
        print("Transitions:")
        for state in sorted(self.states):
            for symbol in sorted(self.alphabet):
                if symbol in self.transitions[state]:
                    targets = sorted(self.transitions[state][symbol])
                    print(f"  δ({state}, {symbol}) = {targets}")

    def print_table(self, title: str = "Transition Table"):
        symbols = sorted(self.alphabet)
        print(f"\n{title}")
        print(f"{'State':<20}" + "".join(f"{s:<15}" for s in symbols))
        for state in sorted(self.states):
            prefix = ("*" if state in self.final_states else "") + \
                     ("->" if state == self.initial_state else "")
            row = f"{prefix + state:<20}"
            for sym in symbols:
                targets = sorted(self.transitions.get(state, {}).get(sym, set()))
                row += f"{str(targets if targets else '-'):<15}"
            print(row)

    def draw(self, filename: str = "fa.png", title: str = "Finite Automaton"):
        trans_plain: Dict[str, Dict[str, List[str]]] = {}
        for state in self.states:
            trans_plain[state] = {}
            for symbol, targets in self.transitions[state].items():
                trans_plain[state][symbol] = sorted(targets)

        G = nx.MultiDiGraph()
        for state in trans_plain:
            G.add_node(state)

        edge_labels: Dict[tuple, str] = {}
        for state, sym_map in trans_plain.items():
            for symbol, targets in sym_map.items():
                for target in targets:
                    G.add_edge(state, target)
                    key = (state, target)
                    edge_labels[key] = edge_labels.get(key, "") + symbol + ","

        edge_labels = {k: v.rstrip(",") for k, v in edge_labels.items()}

        pos = nx.spring_layout(G, seed=42, k=2)

        fig, ax = plt.subplots(figsize=(9, 6))
        ax.set_title(title, fontsize=13)
        ax.axis("off")

        node_colors = []
        for node in G.nodes():
            if node in self.final_states:
                node_colors.append("#90ee90")
            elif node == self.initial_state:
                node_colors.append("#add8e6")
            else:
                node_colors.append("#ffffff")

        nx.draw_networkx_nodes(G, pos, node_size=1800, node_color=node_colors,
                               edgecolors="black", linewidths=1.5, ax=ax)
        nx.draw_networkx_labels(G, pos, font_size=11, ax=ax)
        nx.draw_networkx_edges(G, pos, ax=ax, arrows=True,
                               arrowstyle="-|>", arrowsize=20,
                               connectionstyle="arc3,rad=0.15",
                               edge_color="gray", width=1.5)

        for (u, v), label in edge_labels.items():
            x = (pos[u][0] + pos[v][0]) / 2
            y = (pos[u][1] + pos[v][1]) / 2 + 0.1
            ax.text(x, y, label, fontsize=9, ha="center",
                    bbox=dict(boxstyle="round,pad=0.2", fc="lightyellow", ec="gray"))

        legend = [
            mpatches.Patch(color="#add8e6", label="Start state"),
            mpatches.Patch(color="#90ee90", label="Final state"),
            mpatches.Patch(color="white",   label="Normal state"),
        ]
        ax.legend(handles=legend, loc="upper left", fontsize=9)

        plt.tight_layout()
        plt.savefig(filename, dpi=150)
        plt.close()
        print(f"Graph saved to {filename}")


class RegularGrammar:

    def __init__(self):
        self.non_terminals: Set[str] = set()
        self.terminals: Set[str] = set()
        self.start_symbol: str = ""
        self.productions: Dict[str, List[str]] = {}

    def classify(self):
        is_regular = True
        is_context_free = True
        is_context_sensitive = True

        for left_side, right_sides in self.productions.items():
            if left_side not in self.non_terminals:
                is_context_free = False
                is_context_sensitive = False

            for right_side in right_sides:
                if right_side == "ε":
                    pass
                else:
                    terminal = None
                    nonterminal = None
                    for t in self.terminals:
                        if right_side.startswith(t):
                            terminal = t
                            nonterminal = right_side[len(t):]
                            break

                    if terminal is None:
                        is_regular = False
                    else:
                        if nonterminal != "" and nonterminal not in self.non_terminals:
                            is_regular = False

                if (is_context_sensitive and right_side != "ε"
                        and len(right_side) < len(left_side)):
                    is_context_sensitive = False

        if is_regular:
            return "Type 3: Regular Grammar"
        elif is_context_free:
            return "Type 2: Context-Free Grammar"
        elif is_context_sensitive:
            return "Type 1: Context-Sensitive Grammar"
        else:
            return "Type 0: Unrestricted Grammar"

    def print_grammar(self):
        print("\nRegular Grammar:")
        print(f"Non-terminals: {sorted(self.non_terminals)}")
        print(f"Terminals: {sorted(self.terminals)}")
        print(f"Start Symbol: {self.start_symbol}")
        print("Productions:")
        for lhs in sorted(self.productions.keys()):
            rhs_list = sorted(self.productions[lhs])
            print(f"  {lhs} -> {', '.join(rhs_list)}")
        print(f"Grammar Classification: {self.classify()}")


class Main:

    @staticmethod
    def run():
        print("=" * 50)
        print("Formal Languages & Finite Automata Laboratory")
        print("=" * 50)
        print("\n Task 1: Creating Finite Automaton for Variant 9")
        print("-" * 40)
        fa = FiniteAutomaton.create_variant9()
        fa.print_automaton()
        fa.print_table("Transition Table (NDFA)")
        print("\n Task 2: Converting FA to Regular Grammar")
        print("-" * 40)
        grammar = fa.to_regular_grammar()
        grammar.print_grammar()
        print("\n Task 3: Determinism Check")
        print("-" * 40)
        print(f"The automaton is {'deterministic' if fa.is_deterministic else 'non-deterministic'}")
        if not fa.is_deterministic:
            print("Reason: Multiple transitions from q1 on symbol 'b'")
            print("  δ(q1, b) = {'q2', 'q3'}")
        print("\n Task 4: Converting NDFA to DFA")
        print("-" * 40)
        dfa = fa.to_dfa()
        dfa.print_automaton()
        dfa.print_table("Transition Table (DFA)")
        print("\n Task 5: Chomsky Hierarchy Classification")
        print("-" * 40)
        print(f"Original Grammar Classification: {grammar.classify()}")
        print("\n Verification")
        print("-" * 40)
        print(f"Original FA: {len(fa.states)} states")
        print(f"Converted DFA: {len(dfa.states)} states")
        print(" Conversion successful!")
        print("\n Detailed Analysis:")
        print("-" * 40)
        print("Original NDFA characteristics:")
        print("  - Non-deterministic due to q1 having two transitions on 'b'")
        print("  - Contains a cycle: q0 → q1 → q2 → q0")
        print("  - Final state q4 reachable through q3")
        print("\nDFA conversion results:")
        print(f"  - DFA has {len(dfa.states)} states: {sorted(dfa.states)}")
        print(f"  - Final states in DFA: {sorted(dfa.final_states)}")
        print("  - DFA is deterministic (each state has at most one transition per symbol)")
        print("\n Task 6 (d): Graphical Representation")
        print("-" * 40)
        fa.draw(filename="fa_original.png", title="Original NDFA (Variant 9)")
        dfa.draw(filename="fa_dfa.png", title="DFA after Subset Construction")


if __name__ == "__main__":
    Main.run()
