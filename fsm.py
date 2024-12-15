import tkinter as tk
from tkinter import messagebox
from graphviz import Digraph
import os
from collections import defaultdict

# Function to generate FSM diagram
def generate_fsm_diagram(states, transitions, start_state, accept_states, filename='fsm_diagram'):
    try:
        dot = Digraph()
        dot.attr(rankdir='LR')  # Set graph layout to horizontal (Left-to-Right)

        # Add nodes for all states
        for state in states:
            if state in accept_states:
                dot.node(state, shape='doublecircle')  # Accepting states have double circles
            else:
                dot.node(state)

        # Add an invisible start node pointing to the start state
        dot.node('start', shape='none')
        dot.edge('start', start_state)

        # Add edges for transitions
        for transition in transitions:
            src, sym, dest = transition.split(',')
            dot.edge(src, dest, label=sym)

        # Render the diagram
        dot.render(filename, format='png', cleanup=True)
    except Exception as e:
        messagebox.showerror("Error", f"Could not generate FSM diagram: {e}")

def simulate_dfsm():
    try:
        states = state_entry.get().split(',')
        alphabet = alphabet_entry.get().split(',')
        start_state = start_state_entry.get()
        accept_states = accept_state_entry.get().split(',')
        transitions = transition_entry.get().split(';')
        input_string = input_string_entry.get()

        for trans in transitions:
            if len(trans.split(',')) != 3:
                messagebox.showerror("Error", "Transitions must be in 'state,symbol,next_state' format.")
                return

        transition_dict = {}
        for trans in transitions:
            src, sym, dest = trans.split(',')
            transition_dict[(src, sym)] = dest

        if os.path.exists('fsm_diagram.png'):
            os.remove('fsm_diagram.png')  
        generate_fsm_diagram(states, transitions, start_state, accept_states)

        if os.path.exists('fsm_diagram.png'):
            img = tk.PhotoImage(file='fsm_diagram.png')
            fsm_diagram_label.config(image=img)
            fsm_diagram_label.image = img

        current_state = start_state
        for char in input_string:
            if (current_state, char) in transition_dict:
                current_state = transition_dict[(current_state, char)]
            else:
                dfsm_result_label.config(text="Result: String Rejected", fg="red")
                return

        if current_state in accept_states:
            dfsm_result_label.config(text="Result: String Accepted", fg="green")
        else:
            dfsm_result_label.config(text="Result: String Rejected", fg="red")
    except Exception as e:
        messagebox.showerror("Error", f"DFSM Simulation failed: {e}")

def nfa_to_dfa():
    try:
        nfa_states = nfa_state_entry.get().split(',')
        alphabet = nfa_alphabet_entry.get().split(',')
        nfa_start_state = nfa_start_state_entry.get()
        nfa_accept_states = nfa_accept_state_entry.get().split(',')
        nfa_transitions = nfa_transition_entry.get().split(';')

        nfa_transition_dict = defaultdict(set)
        for trans in nfa_transitions:
            src, sym, dest = trans.split(',')
            nfa_transition_dict[(src, sym)].add(dest)

        dfa_states = []
        dfa_transitions = []
        dfa_accept_states = set()

        trap_state = 'trap'
        dfa_states.append(trap_state)

        state_map = {}
        queue = [frozenset([nfa_start_state])]
        state_map[frozenset([nfa_start_state])] = 'q0'
        dfa_states.append('q0')

        if any(state in nfa_accept_states for state in [nfa_start_state]):
            dfa_accept_states.add('q0')

        while queue:
            current_set = queue.pop(0)
            current_label = state_map[current_set]

            for symbol in alphabet:
                next_set = frozenset(
                    dest
                    for nfa_state in current_set
                    for dest in nfa_transition_dict.get((nfa_state, symbol), set())
                )

                if not next_set:
                    dfa_transitions.append(f"{current_label},{symbol},{trap_state}")
                    continue

                if next_set not in state_map:
                    new_state_label = f'q{len(state_map)}'
                    state_map[next_set] = new_state_label
                    queue.append(next_set)
                    dfa_states.append(new_state_label)

                    if any(state in nfa_accept_states for state in next_set):
                        dfa_accept_states.add(new_state_label)

                next_label = state_map[next_set]
                dfa_transitions.append(f"{current_label},{symbol},{next_label}")

        for state in dfa_states:
            for symbol in alphabet:
                if not any(trans.startswith(f"{state},{symbol},") for trans in dfa_transitions):
                    dfa_transitions.append(f"{state},{symbol},{trap_state}")

        if os.path.exists('dfa_diagram.png'):
            os.remove('dfa_diagram.png') 
        
        generate_fsm_diagram(dfa_states, dfa_transitions, 'q0', dfa_accept_states, 'dfa_diagram')

        if os.path.exists('dfa_diagram.png'):
            img = tk.PhotoImage(file='dfa_diagram.png')
            dfa_diagram_label.config(image=img)
            dfa_diagram_label.image = img

        dfa_result_label.config(text=f"Converted DFA: {len(dfa_states)} states (including trap state)", fg="blue",bg='white')

    except Exception as e:
        messagebox.showerror("Error", f"NFA to DFA conversion failed: {e}")

# GUI Setup
root = tk.Tk()
root.title("Finite State Machine Simulator and Converter")
root.geometry("1600x800")  # Increased width to accommodate both sections

# Configure grid for layout
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

# Left Frame: DFSM Simulation
input_frame = tk.Frame(root, padx=10, pady=10, bg="#000000", relief="groove", bd=2)
input_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

# Right Frame: NFA to DFA Conversion
nfa_frame = tk.Frame(root, padx=10, pady=10, bg="#585f63", relief="groove", bd=2)
nfa_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

# DFSM Simulation Section (Left Frame)
input_title = tk.Label(input_frame, text="DFSM Simulation", font=("Arial", 14, "bold"), bg="#000000", fg='white')
input_title.grid(row=0, column=0, columnspan=2, pady=10)

state_label = tk.Label(input_frame, text="Enter States (comma-separated):", bg="#000000", fg='white')
state_label.grid(row=1, column=0, sticky="w", pady=5)
state_entry = tk.Entry(input_frame, width=30)
state_entry.grid(row=1, column=1, pady=5)

alphabet_label = tk.Label(input_frame, text="Enter Alphabet (comma-separated):", bg="#000000" ,fg='white')
alphabet_label.grid(row=2, column=0, sticky="w", pady=5)
alphabet_entry = tk.Entry(input_frame, width=30)
alphabet_entry.grid(row=2, column=1, pady=5)

start_state_label = tk.Label(input_frame, text="Enter Start State:", bg="#000000", fg='white')
start_state_label.grid(row=3, column=0, sticky="w", pady=5)
start_state_entry = tk.Entry(input_frame, width=30)
start_state_entry.grid(row=3, column=1, pady=5)

accept_state_label = tk.Label(input_frame, text="Enter Accepting States (comma-separated):", bg="#000000", fg='white')
accept_state_label.grid(row=4, column=0, sticky="w", pady=5)
accept_state_entry = tk.Entry(input_frame, width=30)
accept_state_entry.grid(row=4, column=1, pady=5)

transition_label = tk.Label(input_frame, text="Enter Transitions (state,symbol,next_state;...):", bg="#000000", fg='white')
transition_label.grid(row=5, column=0, sticky="w", pady=5)
transition_entry = tk.Entry(input_frame, width=30)
transition_entry.grid(row=5, column=1, pady=5)

input_string_label = tk.Label(input_frame, text="Enter String to Verify:",bg='#000000', fg='white')
input_string_label.grid(row=6, column=0, sticky="w", pady=5)
input_string_entry = tk.Entry(input_frame, width=30)
input_string_entry.grid(row=6, column=1, pady=5)

simulate_button = tk.Button(input_frame, text="Simulate DFSM", command=simulate_dfsm, bg="white", fg="black")
simulate_button.grid(row=7, column=0, columnspan=2, pady=10)

fsm_diagram_label = tk.Label(input_frame, bg="#000000")
fsm_diagram_label.grid(row=8, column=0, columnspan=2, pady=10)

dfsm_result_label = tk.Label(input_frame, text="DFSM Result:", font=("Arial", 12), bg="white")
dfsm_result_label.grid(row=9, column=0, columnspan=2, pady=10)

# NFA to DFA Conversion Section (Right Frame)
nfa_title = tk.Label(nfa_frame, text="NFA to DFA Conversion", font=("Arial", 14, "bold"), bg="#585f63",fg='white')
nfa_title.grid(row=0, column=0, columnspan=2, pady=10)

nfa_state_label = tk.Label(nfa_frame, text="NFA States (comma-separated):", bg="#585f63",fg='white')
nfa_state_label.grid(row=1, column=0, sticky="w", pady=5)
nfa_state_entry = tk.Entry(nfa_frame, width=30)
nfa_state_entry.grid(row=1, column=1, pady=5)

nfa_alphabet_label = tk.Label(nfa_frame, text="NFA Alphabet (comma-separated):", bg="#585f63",fg='white')
nfa_alphabet_label.grid(row=2, column=0, sticky="w", pady=5)
nfa_alphabet_entry = tk.Entry(nfa_frame, width=30)
nfa_alphabet_entry.grid(row=2, column=1, pady=5)

nfa_start_state_label = tk.Label(nfa_frame, text="NFA Start State:", bg="#585f63",fg='white')
nfa_start_state_label.grid(row=3, column=0, sticky="w", pady=5)
nfa_start_state_entry = tk.Entry(nfa_frame, width=30)
nfa_start_state_entry.grid(row=3, column=1, pady=5)

nfa_accept_state_label = tk.Label(nfa_frame, text="NFA Accepting States (comma-separated):", bg="#585f63",fg='white')
nfa_accept_state_label.grid(row=4, column=0, sticky="w", pady=5)
nfa_accept_state_entry = tk.Entry(nfa_frame, width=30)
nfa_accept_state_entry.grid(row=4, column=1, pady=5)

nfa_transition_label = tk.Label(nfa_frame, text="NFA Transitions (state,symbol,next_state;...):", bg="#585f63",fg='white')
nfa_transition_label.grid(row=5, column=0, sticky="w", pady=5)
nfa_transition_entry = tk.Entry(nfa_frame, width=30)
nfa_transition_entry.grid(row=5, column=1, pady=5)

convert_button = tk.Button(nfa_frame, text="Convert NFA to DFA", command=nfa_to_dfa, bg="white", fg="black")
convert_button.grid(row=6, column=0, columnspan=2, pady=10)

dfa_diagram_label = tk.Label(nfa_frame, bg="#585f63")
dfa_diagram_label.grid(row=7, column=0, columnspan=2, pady=10)

dfa_result_label = tk.Label(nfa_frame, text="DFA Conversion Result:", font=("Arial", 12), bg="#585f63",fg='white')
dfa_result_label.grid(row=8, column=0, columnspan=2, pady=10)

# Run the main loop
root.mainloop()