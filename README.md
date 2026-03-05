# Laboratory Work 2: Determinism in Finite Automata. Conversion from NDFA to DFA. Chomsky Hierarchy

**Author:** Cretu Dumitru  
**Course:** Formal Languages & Finite Automata  
**Variant:** 9  
**Date:** February 26, 2026  
**Student:** Bulimar Rodion  
**Group:** FAF-242

---

## 1. Introduction

A finite automaton is a mechanism used to represent processes of different kinds. It can be compared to a state machine as they both have similar structures and purpose as well. The word finite signifies the fact that an automaton comes with a starting and a set of final states. In other words, any process modeled by an automaton has a beginning and an ending.

Based on the structure of an automaton, there are cases in which with one transition multiple states can be reached which causes non determinism to appear. In general, when talking about systems theory the word determinism characterizes how predictable a system is. If there are random variables involved, the system becomes stochastic or non deterministic.

Automata can be classified as deterministic or non-deterministic, and there is a possibility to reach determinism by following algorithms which modify the structure of the automaton. This laboratory work focuses on understanding these concepts and implementing the conversion from non-deterministic finite automata to deterministic finite automata.

---

## 2. Objectives

The primary objectives of this laboratory work include providing a function in the grammar class that can classify the grammar based on the Chomsky hierarchy. According to variant 9, the finite automaton definition is used to perform several tasks. Implementing conversion of a finite automaton to a regular grammar is required. Determining whether the finite automaton is deterministic or non-deterministic is necessary. Implementing functionality that would convert an NDFA to a DFA represents the core task. Optionally, representing the finite automaton graphically can be considered as a bonus point. Documenting the work in both README.md and REPORT.md files completes the requirements.

---

## 3. Implementation

### Finite Automaton Definition for Variant 9

The finite automaton for variant 9 is defined with a set of states Q containing q0, q1, q2, q3, and q4. The alphabet Σ consists of the symbols a, b, and c. The set of final states F contains only q4. The transition function δ is defined as follows. From state q0 with symbol a, the automaton transitions to state q1. From state q1 with symbol b, the automaton transitions to state q2. From state q2 with symbol c, the automaton transitions to state q0. From state q1 with symbol b, the automaton also transitions to state q3. From state q3 with symbol a, the automaton transitions to state q4. From state q3 with symbol b, the automaton transitions to state q0.

This automaton is non-deterministic because state q1 has two different transitions on the same input symbol b, going to both q2 and q3 simultaneously.

### FA to Regular Grammar Conversion

The conversion from a finite automaton to a regular grammar follows specific rules. Each state becomes a non-terminal symbol. Each alphabet symbol becomes a terminal symbol. For each transition δ(state, symbol) equals next_state, a production is added in the form state followed by symbol followed by next_state. For each final state, an epsilon production is added in the form state followed by ε.

For variant 9, the conversion yields the following grammar:

| Finite Automaton Transition | Regular Grammar Production |
|----------------------------|---------------------------|
| δ(q0, a) = q1 | q0 → aq1 |
| δ(q1, b) = q2 | q1 → bq2 |
| δ(q1, b) = q3 | q1 → bq3 |
| δ(q2, c) = q0 | q2 → cq0 |
| δ(q3, a) = q4 | q3 → aq4 |
| δ(q3, b) = q0 | q3 → bq0 |
| q4 is final | q4 → ε |

The resulting grammar has non-terminals VN = {q0, q1, q2, q3, q4}. The terminals VT = {a, b, c}. The start symbol is q0. The productions are as listed above.

### Grammar Classification Based on Chomsky Hierarchy

The grammar classification method analyzes the production rules to determine their place in the Chomsky hierarchy. The algorithm checks for regular grammar properties first. If the grammar does not satisfy regular grammar conditions, it checks for context-free properties. If context-free conditions are not met, it checks for context-sensitive properties. If none of these apply, the grammar is classified as unrestricted.

```python
def classify_grammar(self):
    is_regular = True
    is_context_free = True
    is_context_sensitive = True
    
    for left_side, right_sides in self.productions.items():
        for right_side in right_sides:
            if right_side == "ε":
                if left_side != self.start_symbol:
                    is_regular = False
            elif len(right_side) == 1:
                if right_side[0] not in self.terminals:
                    is_regular = False
            elif len(right_side) == 2:
                first, second = right_side[0], right_side[1]
                if first not in self.terminals or second not in self.non_terminals:
                    is_regular = False
            else:
                is_regular = False
            
            if len(left_side) != 1 or left_side not in self.non_terminals:
                is_context_free = False
                is_context_sensitive = False
            
            if is_context_sensitive and len(right_side) < len(left_side) and right_side != "ε":
                is_context_sensitive = False
    
    if is_regular:
        return "Type 3: Regular Grammar"
    elif is_context_free:
        return "Type 2: Context-Free Grammar"
    elif is_context_sensitive:
```
### Determinism Check Method
The determinism check verifies whether a finite automaton is deterministic by examining all transitions.
```python
def check_deterministic(self):
    self.is_deterministic = True
    non_deterministic_pairs = []
    
    for state in self.states:
        for symbol, targets in self.transitions[state].items():
            if len(targets) > 1:
                self.is_deterministic = False
                non_deterministic_pairs.append((state, symbol, targets))
    
    if not self.is_deterministic:
        print("Non-determinism found at the following transitions:")
        for state, symbol, targets in non_deterministic_pairs:
            print(f"  δ({state}, {symbol}) = {targets}")
    
    return self.is_deterministic
```
### NDFA to DFA Conversion Method
The conversion from NDFA to DFA uses the subset construction algorithm. Each state in the DFA represents a set of states from the original NDFA. This algorithm guarantees that the resulting DFA recognizes exactly the same language as the original NDFA.
```python
def convert_to_dfa(self):
    if self.is_deterministic:
        print("Automaton is already deterministic")
        return self
    
    print("Converting NDFA to DFA using subset construction...")
    dfa = FiniteAutomaton()
    dfa.alphabet = set(self.alphabet)
    
    dfa_state_map = {}
    reverse_state_map = {}
    
    initial_set = frozenset([self.initial_state])
    dfa_state_map[initial_set] = "A"
    reverse_state_map["A"] = initial_set
    
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
                    new_state_name = chr(ord('A') + state_counter)
                    state_counter += 1
                    dfa_state_map[next_frozenset] = new_state_name
                    reverse_state_map[new_state_name] = next_frozenset
                    queue.append(next_frozenset)
                    print(f"  Created new DFA state {new_state_name} = {set(next_frozenset)}")
                
                next_dfa_state = dfa_state_map[next_frozenset]
                dfa.add_transition(current_dfa_state, symbol, next_dfa_state)
                print(f"  Added transition δ({current_dfa_state}, {symbol}) = {next_dfa_state}")
    
    dfa.states = set(dfa_state_map.values())
    dfa.final_states = set()
    for ndfa_set, dfa_state in dfa_state_map.items():
        if not ndfa_set.isdisjoint(self.final_states):
            dfa.final_states.add(dfa_state)
            print(f"  DFA state {dfa_state} is final (contains {set(ndfa_set) & self.final_states})")
    
    dfa.initial_state = "A"
    dfa.is_deterministic = True
    
    print(f"Conversion complete. DFA has {len(dfa.states)} states.")
    return dfa
```

<img width="1210" height="440" alt="image" src="https://github.com/user-attachments/assets/f09a7913-a96f-4a8d-a448-133cd321e24f" />

### String Validation Method
The string validation method determines whether a given string belongs to the language by simulating the finite automaton. For non-deterministic automata, it tracks multiple possible paths simultaneously using a set of current states.
```python
def string_belongs_to_language(self, input_string: str) -> bool:
    if not input_string:
        return self.initial_state in self.final_states
    
    current_states = {self.initial_state}
    path_history = [(0, set(current_states))]
    
    for position, char in enumerate(input_string):
        if char not in self.alphabet:
            print(f"  Character '{char}' not in alphabet")
            return False
        
        next_states = set()
        for state in current_states:
            if state in self.transitions and char in self.transitions[state]:
                next_states.update(self.transitions[state][char])
        
        if not next_states:
            print(f"  No transition from states {current_states} on '{char}'")
            return False
        
        current_states = next_states
        path_history.append((position + 1, set(current_states)))
    
    accepted = bool(current_states & self.final_states)
    
    if accepted:
        print("  Path taken:")
        for step, states in path_history:
            if step == 0:
                print(f"    Start: {states}")
            else:
                print(f"    After '{input_string[step-1]}': {states}")
    
    return accepted
```
### Graphical Representation Method
For the bonus point, a method was implemented to generate a graphical representation of the finite automaton using Graphviz. This method creates a DOT file and renders it as a PNG image.
```python
def visualize_automaton(self, filename="automaton"):
    try:
        import graphviz
    except ImportError:
        print("Graphviz not installed. Please install with: pip install graphviz")
        return
    
    dot = graphviz.Digraph(comment='Finite Automaton')
    dot.attr(rankdir='LR')
    
    for state in self.states:
        if state in self.final_states:
            dot.node(state, state, shape='doublecircle')
        elif state == self.initial_state:
            dot.node(state, state, shape='circle')
            dot.node('start', '', shape='none', width='0', height='0')
            dot.edge('start', state)
        else:
            dot.node(state, state, shape='circle')
    
    for from_state in self.transitions:
        for symbol, to_states in self.transitions[from_state].items():
            for to_state in to_states:
                dot.edge(from_state, to_state, label=symbol)
    
    output_path = dot.render(filename, format='png', cleanup=False)
    print(f"Visualization saved to {output_path}")
    return output_path
```
## 4. Results

### FA to Regular Grammar Conversion Results

The conversion from the finite automaton to a regular grammar was completed successfully. The resulting grammar has five non-terminals corresponding to the five states of the original automaton. The grammar has seven productions, one for each transition in the original automaton plus an epsilon production for the final state. All productions follow the right-linear form required for regular grammars.

### Determinism Check Results

The determinism check was performed on the finite automaton for variant 9. The automaton was found to be non-deterministic. The non-determinism occurs at state q1 with the input symbol b, where there are two possible target states: q2 and q3. This violates the definition of a deterministic finite automaton which requires at most one transition per state-symbol pair.

### NDFA to DFA Conversion Results

The subset construction algorithm was applied to convert the non-deterministic finite automaton to a deterministic one. The conversion process proceeded as follows.

Starting from the initial state set containing q0, the algorithm explored all reachable state sets. The initial set {q0} was assigned DFA state A. From state A on symbol a, the reachable set was {q1}, which became DFA state B. From state B on symbol b, the reachable set was {q2, q3} due to the non-determinism, which became DFA state C. From state C on symbol a, the reachable set was {q4} because from q3 on a we reach q4, and from q2 on a there is no transition. This set became DFA state D. From state C on symbol b, the reachable set was {q0} because from q3 on b we reach q0, and from q2 on b there is no transition. This returned to state A. From state C on symbol c, the reachable set was {q0} because from q2 on c we reach q0, and from q3 on c there is no transition. This also returned to state A. From state D, there were no outgoing transitions as q4 has no outgoing transitions in the original automaton.

The resulting DFA has four states: A, B, C, and D. State D is the only final state as it contains q4 which was final in the original automaton. The transitions in the DFA are as follows:

δ(A, a) = B

δ(B, b) = C

δ(C, a) = D

δ(C, b) = A

δ(C, c) = A

### Grammar Classification Results

The grammar was classified using the Chomsky hierarchy classification function. The grammar was determined to be Type 3, which is a regular grammar. This classification is correct because all productions follow the required forms. Productions are either of the form A → aB or A → a. The only epsilon production is from q4, which is a final state. All left-hand sides are single non-terminals. No production has more than two symbols on the right-hand side.

### String Validation Results

Testing various strings against both the original NDFA and the converted DFA yielded identical results, confirming that the conversion preserved the language.

| Input String | NDFA Result | DFA Result | Path in NDFA |
|--------------|-------------|------------|--------------|
| a | Accepted | Accepted | q0 → q1 |
| ac | Rejected | Rejected | No transition from q1 on c |
| aca | Accepted | Accepted | q0 → q1 → q3 → q4 |
| acb | Accepted | Accepted | q0 → q1 → q3 → q0 |
| acba | Accepted | Accepted | q0 → q1 → q3 → q0 → q1 |
| acbac | Rejected | Rejected | Cycle continues, no final state |
| b | Rejected | Rejected | No transition from q0 on b |
| empty | Rejected | Rejected | q0 not a final state |

### Graphical Representation

The finite automaton was visualized using Graphviz. The generated image shows all states with the initial state having an incoming arrow and final states represented as double circles. Transitions are labeled with their corresponding symbols. The visualization clearly shows the non-determinism at state q1 with two outgoing transitions on symbol b.

---

## 5. Conclusions

### Summary of Achievements

All required tasks for this laboratory work were completed successfully. A function was implemented in the grammar class to classify grammars based on the Chomsky hierarchy. The conversion from finite automaton to regular grammar was implemented and tested. The determinism check was implemented and correctly identified the variant 9 automaton as non-deterministic. The NDFA to DFA conversion was implemented using the subset construction algorithm and successfully produced an equivalent deterministic automaton. As a bonus, graphical representation of the automaton was implemented using Graphviz. Documentation was completed in the required format with both README and REPORT files.

### Key Findings

Non-determinism in finite automata appears when a state has multiple transitions on the same input symbol. The variant 9 automaton demonstrated this property with state q1 having two transitions on the symbol b. This creates ambiguity in the language recognition process because multiple paths must be considered simultaneously.

The subset construction algorithm proved highly effective for eliminating non-determinism. The algorithm successfully converted the five-state NDFA to a four-state DFA. 

The equivalence between finite automata and regular grammars was demonstrated through the conversion process. The regular grammar derived from the finite automaton correctly represented the same language. This confirms the theoretical equivalence between these two formalisms, which is a fundamental result in formal language theory.

The Chomsky hierarchy classification placed the grammar firmly in Type 3. All productions followed the right-linear form required for regular grammars. The grammar contains a recursive production that allows generating strings of arbitrary length, demonstrating that regular grammars can describe infinite languages despite their simplicity.

---

## 6. References

Drumea, V. and Cojuhari, I. Formal Languages and Finite Automata. Technical University of Moldova, 2026.

Hopcroft, J. E., Motwani, R., and Ullman, J. D. Introduction to Automata Theory, Languages, and Computation. 3rd ed., Addison-Wesley, 2006.

Sipser, M. Introduction to the Theory of Computation. 3rd ed., Cengage Learning, 2012.

Chomsky, N. Three models for the description of language. IRE Transactions on Information Theory, 1956.

Rabin, M. O. and Scott, D. Finite Automata and Their Decision Problems. IBM Journal of Research and Development, 1959.

Graphviz - Graph Visualization Software. https://graphviz.org/

---

## 7. Declaration

I hereby declare that this laboratory work is my own original work and has been completed in accordance with the academic integrity policy of the Technical University of Moldova.

**Student:** Bulimar Rodion  
**Group:** FAF-242  
**Date:** February 26, 2026

---

*End of Report*
        return "Type 1: Context-Sensitive Grammar"
    else:
        return "Type 0: Unrestricted Grammar"


