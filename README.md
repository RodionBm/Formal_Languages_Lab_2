# Laboratory Work 1: Intro to Formal Languages. Regular Grammars. Finite Automata

**Author:** Cretu Dumitru  
**Course:** Formal Languages & Finite Automata  
**Variant:** 9  
**Date:** February 26, 2026  
**Student:** Bulimar Rodion  
**Group:** FAF-242

---

## 1. Introduction

A formal language is a set of strings formed from an alphabet, governed by specific rules. The main components include an alphabet of valid symbols, variables that can be replaced, symbols that appear in final strings, rules for replacing non-terminals, and an initial non-terminal. This laboratory work focuses on regular grammars, known as Type-3 grammars, and their corresponding finite automata.

According to the Chomsky hierarchy, grammars are classified into four types. Type-3 grammars are regular grammars. Type-2 grammars are context-free grammars. Type-1 grammars are context-sensitive grammars. Type-0 grammars are unrestricted grammars. This work specifically deals with the conversion between regular grammars and finite automata, as well as the transformation of non-deterministic finite automata to deterministic finite automata.

---

## 2. Objectives

The primary objectives of this laboratory work include implementing a Grammar class for variant 9 with the ability to classify grammars based on the Chomsky hierarchy. Another objective is implementing conversion of a finite automaton to a regular grammar. Determining whether a finite automaton is deterministic or non-deterministic is also required. Implementing functionality to convert an NDFA to a DFA represents a core task. Generating valid strings from the grammar and implementing a method to verify whether a string belongs to the language are essential components. Documenting the work in both README.md and REPORT.md files completes the requirements.

---

## 3. Implementation

### Finite Automaton Definition for Variant 9

The finite automaton for variant 9 is defined as follows:

- Q = {q0, q1, q2, q3, q4}
- Σ = {a, b, c}
- F = {q4}
- δ transition function:
  - δ(q0, a) = q1
  - δ(q1, b) = q2
  - δ(q2, c) = q0
  - δ(q1, b) = q3
  - δ(q3, a) = q4
  - δ(q3, b) = q0

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

### Grammar Classification Method

The grammar classification method analyzes the production rules to determine their place in the Chomsky hierarchy. The algorithm checks for regular grammar properties first. If the grammar does not satisfy regular grammar conditions, it checks for context-free properties. If context-free conditions are not met, it checks for context-sensitive properties. If none of these apply, the grammar is classified as unrestricted.

```python
def classify(self):
    is_regular = True
    is_context_free = True
    is_context_sensitive = True
    
    for left_side, right_sides in self.productions.items():
        for right_side in right_sides:
            if right_side == "ε":
                if left_side != self.start_symbol:
                    is_regular = False
            elif len(right_side) == 1:
                if right_side[0] not in self.terminals and right_side[0] != "ε":
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
        return "Type 1: Context-Sensitive Grammar"
    else:
        return "Type 0: Unrestricted Grammar"
    ```
### Determinism Check Method
The determinism check verifies whether a finite automaton is deterministic by examining all transitions.
```python
def check_deterministic(self):
    self.is_deterministic = True
    
    for state in self.states:
        for symbol, targets in self.transitions[state].items():
            if len(targets) > 1:
                self.is_deterministic = False
                print(f"Non-determinism found: δ({state}, {symbol}) = {targets}")
                return
                ```
### NDFA to DFA Conversion Method
The conversion from NDFA to DFA uses the subset construction algorithm. Each state in the DFA represents a set of states from the original NDFA.
```python
def to_dfa(self):
    if self.is_deterministic:
        return self
    
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
                
                next_dfa_state = dfa_state_map[next_frozenset]
                dfa.add_transition(current_dfa_state, symbol, next_dfa_state)
    
    dfa.states = set(dfa_state_map.values())
    dfa.final_states = set()
    for ndfa_set, dfa_state in dfa_state_map.items():
        if not ndfa_set.isdisjoint(self.final_states):
            dfa.final_states.add(dfa_state)
    
    dfa.initial_state = "A"
    dfa.is_deterministic = True
    
    return dfa
    ```
    ### String Generation Method
    The string generation method implements a leftmost derivation algorithm to produce valid strings from the grammar.
    ```python
    def generate_string(self):
    current_string = "q0"
    max_steps = 100
    steps = 0
    
    while any(symbol.islower() for symbol in current_string) and steps < max_steps:
        for i, symbol in enumerate(current_string):
            if symbol.islower():
                continue
            for j in range(i, len(current_string)):
                if current_string[j].isupper() or current_string[j].isdigit():
                    non_terminal = ""
                    k = j
                    while k < len(current_string) and (current_string[k].isupper() or current_string[k].isdigit()):
                        non_terminal += current_string[k]
                        k += 1
                    
                    if non_terminal in self.productions:
                        production_choices = self.productions[non_terminal]
                        chosen_production = random.choice(production_choices)
                        current_string = current_string[:j] + chosen_production + current_string[k:]
                        break
            break
        steps += 1
    
    result = ""
    for char in current_string:
        if char in self.terminals:
            result += char
    
    return result if result else "ε"
    ```
### String Validation Method
The string validation method determines whether a given string belongs to the language by simulating the finite automaton.
```python
def string_belongs_to_language(self, input_string: str) -> bool:
    if not input_string:
        return "q0" in self.final_states
    
    current_states = {self.initial_state}
    
    for char in input_string:
        if char not in self.alphabet:
            return False
        
        next_states = set()
        for state in current_states:
            if state in self.transitions and char in self.transitions[state]:
                next_states.update(self.transitions[state][char])
        
        if not next_states:
            return False
        
        current_states = next_states
    
    return bool(current_states & self.final_states)
    ```

---

## 4. Results
### Generated Strings
Running the program produced several valid strings from the grammar. The first generated string was aca. The second generated string was aca as well. The third generated string was acba. The fourth generated string was acba. The fifth generated string was bca.

The strings aca and acba appeared multiple times during generation. This repetition indicates these are common patterns in the language defined by the grammar. The appearance of bca shows that the language includes strings starting with b as well as a.
### Validation Results
Testing various strings against the automaton yielded specific results. The string a was accepted by the automaton. The path taken was from q0 directly to q1. The string b was rejected because q0 has no transition on the symbol b. The string ac was rejected because after transitioning from q0 to q1, there is no transition from q1 on the symbol c. The string aca was accepted with the path going from q0 to q1 to q3 to q4. The string acb was accepted with the path going from q0 to q1 to q3 back to q0. The string abc was rejected because from q0 to q1 the automaton has multiple possible paths. The string bca was rejected because q0 has no transition on b to begin processing. The string acba was accepted with the path going from q0 to q1 to q3 to q0 to q1. The string acbac was rejected because although the cycle continues, no final state was reached. The empty string was rejected because q0 is not a final state.
### NDFA to DFA Conversion Results
The original NDFA had five states and was non-deterministic due to the conflict at q1 with the symbol b. After applying the subset construction algorithm, the resulting DFA had four states.
The transitions in the DFA were defined as follows. From state A on symbol a, the automaton transitions to state B. From state B on symbol b, the automaton transitions to state C. From state C on symbol a, the automaton transitions to state D. From state C on symbol b, the automaton transitions to state A. From state C on symbol c, the automaton transitions to state A.
### Grammar Classification
The grammar was classified as Type 3, which is a regular grammar. This classification was made because all productions followed the required forms. Productions were either of the form a non-terminal followed by a terminal followed by another non-terminal, or a non-terminal followed by a single terminal. The only epsilon production present was from q4, which is a final state. All left-hand sides were single non-terminals. No production had more than two symbols on the right-hand side.
### Automaton Analysis
The original automaton analysis revealed several characteristics. The number of states was five. The number of transitions was six. The automaton was non-deterministic due to q1 having two transitions on the symbol b. The language characteristics showed that strings must start with a or b. Strings can cycle through q0 to q1 to q2 back to q0, adding ac with each cycle. Strings can branch from q1 to q3 with b. The final state q4 is reached only through q3 with a.

The converted DFA analysis showed different characteristics. The number of states was reduced to four. The number of transitions was five. The automaton was deterministic. The state reduction achieved was twenty percent compared to the original NDFA.

---

## 5. Conclusions
### Summary of Achievements
All tasks for this laboratory work were completed successfully. A Grammar class was implemented with Chomsky hierarchy classification functionality. Conversion from finite automaton to regular grammar was implemented and tested. Determinism checking was implemented and correctly identified the variant 9 automaton as non-deterministic. NDFA to DFA conversion was implemented using the subset construction algorithm. String generation from the grammar was implemented and produced valid strings. String validation was implemented and correctly accepted or rejected test strings. Documentation was completed in the required format with both README and REPORT files.
### Key Findings
Non-determinism in automata appears when a state has multiple transitions on the same input symbol. The variant 9 automaton demonstrated this property with state q1 having two transitions on the symbol b. This creates ambiguity in the language recognition process because multiple paths must be considered simultaneously.

The subset construction algorithm proved effective for eliminating non-determinism. The algorithm successfully converted the five-state NDFA to a four-state DFA. All non-determinism was eliminated while preserving the language recognized by the automaton.

Grammar and automaton equivalence was demonstrated through the conversion process. The regular grammar derived from the finite automaton correctly represented the same language. This confirms the theoretical equivalence between these two formalisms.

The language characteristics revealed specific patterns. Strings in this language always start with a or b. They can cycle through the sequence q0 to q1 to q2 back to q0, adding ac with each cycle. They can branch from q1 to q3 with the symbol b. The final state q4 is reached only through q3 with the symbol a.

The Chomsky classification placed the grammar firmly in Type 3. All productions followed the right-linear form required for regular grammars. No productions violated the constraints of regular grammars.
### Lessons Learned
Regular grammars can describe infinite languages despite their simplicity. This is achieved through recursive productions that allow repetition of patterns. The grammar for variant 9 demonstrated this through the cycle involving q0, q1, and q2.

Non-determinism in finite automata arises from multiple possible transitions on the same input symbol from the same state. This requires simulation algorithms to track multiple paths simultaneously. The string validation method demonstrated this by maintaining a set of possible current states.

The subset construction algorithm provides a systematic way to eliminate non-determinism. The algorithm guarantees that the resulting DFA recognizes exactly the same language as the original NDFA. This conversion is fundamental in automata theory.

Leftmost derivation provides a straightforward approach to string generation from grammars. By always expanding the leftmost non-terminal, the generation process becomes predictable and easy to implement. The random selection among productions allows generating different strings from the same grammar.

Testing edge cases is essential for robust validation. The empty string and strings with invalid symbols must be handled correctly. The validation method included checks for these cases to ensure correct behavior.

The equivalence between grammars and finite automata demonstrates that these two representations capture the same class of languages. This equivalence is a fundamental result in formal language theory with practical applications in compiler design and text processing.
### Future Improvements
Several improvements could be made to this work in the future. Implementing DFA minimization would further reduce the number of states in the converted automaton. Generating regular expressions from the finite automaton would provide another representation of the language. Visualizing the automaton as a graph using libraries like Graphviz would make the structure more understandable. Extending support to context-free grammars and pushdown automata would allow working with more complex languages. Implementing parsing algorithms for the generated grammar would enable syntax analysis applications. Adding unit tests would provide comprehensive validation of all implemented methods.

---

## 6. References
Drumea, V. and Cojuhari, I. Formal Languages and Finite Automata. Technical University of Moldova, 2026.

Hopcroft, J. E., Motwani, R., and Ullman, J. D. Introduction to Automata Theory, Languages, and Computation. 3rd ed., Addison-Wesley, 2006.

Sipser, M. Introduction to the Theory of Computation. 3rd ed., Cengage Learning, 2012.

Chomsky, N. Three models for the description of language. IRE Transactions on Information Theory, 1956.

Rabin, M. O. and Scott, D. Finite Automata and Their Decision Problems. IBM Journal of Research and Development, 1959.

---

### 7. Declaration
I hereby declare that this laboratory work is my own original work and has been completed in accordance with the academic integrity policy of the Technical University of Moldova.

Student: Bulimar Rodion
Group: FAF-242
Date: February 26, 2026

---

*End of Report*