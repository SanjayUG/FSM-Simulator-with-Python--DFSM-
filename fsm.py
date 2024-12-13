import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
import networkx as nx
from io import BytesIO
from PIL import Image, ImageTk

def generate_fsm_diagram(states, transitions, start_state, accept_states):
    try:
        G = nx.DiGraph()

        # Add nodes for all states
        for state in states:
            G.add_node(state, shape='doublecircle' if state in accept_states else 'circle')

        # Add an invisible start node pointing to the start state
        G.add_node("start", shape='none')
        G.add_edge("start", start_state)

        # Add edges for transitions
        for transition in transitions:
            src, sym, dest = transition.split(',')
            G.add_edge(src, dest, label=sym)

        # Draw the graph
        pos = nx.spring_layout(G)  # Layout algorithm for positioning nodes
        plt.figure(figsize=(8, 6))

        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=2000, alpha=0.9)
        nx.draw_networkx_labels(G, pos, font_size=10, font_color='black')

        # Draw edges
        nx.draw_networkx_edges(G, pos, arrowstyle='-|>', arrowsize=15, edge_color='black')

        # Add edge labels
        edge_labels = nx.get_edge_attributes(G, 'label')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

        # Save the diagram to an in-memory file
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plt.close()

        # Return the buffer for rendering in the GUI
        return buffer
    except Exception as e:
        messagebox.showerror("Error", f"Could not generate FSM diagram: {e}")
        return None

def simulate_dfsm():
    try:
        # Parse input
        states = state_entry.get().split(',')
        alphabet = alphabet_entry.get().split(',')
        start_state = start_state_entry.get()
        accept_states = accept_state_entry.get().split(',')
        transitions = transition_entry.get().split(';')
        input_string = input_string_entry.get()

        # Create a transition dictionary
        transition_dict = {}
        for trans in transitions:
            src, sym, dest = trans.split(',')
            if (src, sym) not in transition_dict:
                transition_dict[(src, sym)] = dest

        # Generate FSM diagram
        buffer = generate_fsm_diagram(states, transitions, start_state, accept_states)
        if buffer:
            img = Image.open(buffer)
            img_tk = ImageTk.PhotoImage(img)
            fsm_diagram_label.config(image=img_tk)
            fsm_diagram_label.image = img_tk

        # Simulate the DFSM
        current_state = start_state
        for char in input_string:
            if (current_state, char) in transition_dict:
                current_state = transition_dict[(current_state, char)]
            else:
                result_label.config(text="Result: String Rejected", fg="red")
                return

        # Check if the final state is accepting
        if current_state in accept_states:
            result_label.config(text="Result: String Accepted", fg="green")
        else:
            result_label.config(text="Result: String Rejected", fg="red")
    except Exception as e:
        messagebox.showerror("Error", f"Simulation failed: {e}")

# GUI Setup
root = tk.Tk()
root.title("Deterministic Finite State Machine (DFSM) Simulator")
root.geometry("1000x700")

# Frames for Input and Output
input_frame = tk.Frame(root, padx=15, pady=15, bg="lightblue", relief="groove", bd=2)
input_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

output_frame = tk.Frame(root, padx=15, pady=15, bg="lightgrey", relief="groove", bd=2)
output_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=2)
root.grid_rowconfigure(0, weight=1)

# Input Section
input_title = tk.Label(input_frame, text="Input Configuration", font=("Arial", 16, "bold"), bg="lightblue")
input_title.grid(row=0, column=0, columnspan=2, pady=10)

state_label = tk.Label(input_frame, text="States (comma-separated):", bg="lightblue")
state_label.grid(row=1, column=0, sticky="w", pady=5)
state_entry = tk.Entry(input_frame, width=40)
state_entry.grid(row=1, column=1, pady=5)

alphabet_label = tk.Label(input_frame, text="Alphabet (comma-separated):", bg="lightblue")
alphabet_label.grid(row=2, column=0, sticky="w", pady=5)
alphabet_entry = tk.Entry(input_frame, width=40)
alphabet_entry.grid(row=2, column=1, pady=5)

start_state_label = tk.Label(input_frame, text="Start State:", bg="lightblue")
start_state_label.grid(row=3, column=0, sticky="w", pady=5)
start_state_entry = tk.Entry(input_frame, width=40)
start_state_entry.grid(row=3, column=1, pady=5)

accept_state_label = tk.Label(input_frame, text="Accepting States (comma-separated):", bg="lightblue")
accept_state_label.grid(row=4, column=0, sticky="w", pady=5)
accept_state_entry = tk.Entry(input_frame, width=40)
accept_state_entry.grid(row=4, column=1, pady=5)

transition_label = tk.Label(input_frame, text="Transitions (state,symbol,next_state;...):", bg="lightblue")
transition_label.grid(row=5, column=0, sticky="w", pady=5)
transition_entry = tk.Entry(input_frame, width=40)
transition_entry.grid(row=5, column=1, pady=5)

input_string_label = tk.Label(input_frame, text="Input String to Verify:", bg="lightblue")
input_string_label.grid(row=6, column=0, sticky="w", pady=5)
input_string_entry = tk.Entry(input_frame, width=40)
input_string_entry.grid(row=6, column=1, pady=5)

simulate_button = tk.Button(input_frame, text="Simulate DFSM", command=simulate_dfsm, bg="darkblue", fg="white", font=("Arial", 12))
simulate_button.grid(row=7, column=0, columnspan=2, pady=15)

# Output Section
output_title = tk.Label(output_frame, text="FSM Visualization & Result", font=("Arial", 16, "bold"), bg="lightgrey")
output_title.grid(row=0, column=0, pady=10)

fsm_diagram_label = tk.Label(output_frame, bg="lightgrey")
fsm_diagram_label.grid(row=1, column=0, pady=20)

result_label = tk.Label(output_frame, text="Result: Waiting for Simulation", font=("Arial", 14), bg="lightgrey")
result_label.grid(row=2, column=0, pady=20)

root.mainloop()
