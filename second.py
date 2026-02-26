from typing import Set, Dict, List, Tuple, Optional
from collections import defaultdict
import itertools

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
                            nonterminal = right_side[len(t) :]
                            break

                    if terminal is None:
                        is_regular = False
                    else:
                        if nonterminal == "":
                            pass
                        else:
                            if nonterminal not in self.non_terminals:
                                is_regular = False
                
                if (
                    is_context_sensitive
                    and right_side != "ε"
                    and len(right_side) < len(left_side)
                ):
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
        
        print("\n Task 5: Chomsky Hierarchy Classification")
        print("-" * 40)
        print(f"Original Grammar Classification: {grammar.classify()}")
        
        print("\n Verification")
        print("-" * 40)
        print(f"Original FA: {len(fa.states)} states")
        print(f"Converted DFA: {len(dfa.states)} states")
        print(f" Conversion successful!")
        
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

if __name__ == "__main__":
    Main.run()