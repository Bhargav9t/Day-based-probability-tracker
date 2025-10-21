"""
Day-Based Probability Checker GUI

Features:
- Tkinter GUI with a random heading generated from keywords
- Dropdown to select numbers 1-65
- Button to check probability (number of days that can reach the number / 31)
- Label shows decimal and percentage
- Insight panel with most/least likely numbers
- Optional: embedded bar chart (requires matplotlib), dark mode toggle, export to CSV

Save this file as day_based_probability_checker.py and run with:
    python day_based_probability_checker.py

Matplotlib is optional (for the bar chart). If not installed the app still runs without the chart.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random
import csv
import sys

# Try to import matplotlib for optional bar chart
HAS_MPL = True
try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
except Exception:
    HAS_MPL = False


def compute_reachable_counts(max_number=65):
    """Compute how many of the days 1..31 can reach each number 1..max_number
    by multiplying the day by positive integers until the product exceeds max_number.
    Returns: dict number -> set(days)
    """
    reachable = {n: set() for n in range(1, max_number + 1)}
    for day in range(1, 32):  # days 1..31
        multiple = 1
        while True:
            val = day * multiple
            if val > max_number:
                break
            reachable[val].add(day)
            multiple += 1
    return reachable


# Precompute
MAX_NUMBER = 65
REACHABLE = compute_reachable_counts(MAX_NUMBER)
COUNTS = {n: len(REACHABLE[n]) for n in range(1, MAX_NUMBER + 1)}

# Insights
MOST_LIKELY_NUMBER = 60  # as given in the prompt
MOST_LIKELY_DAYS = COUNTS.get(MOST_LIKELY_NUMBER, 0)
LEAST_LIKELY = [1, 37, 41, 43, 47, 53, 59, 61]
LEAST_LIKELY_PROB = 1 / 31


class DayProbabilityApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Day-Based Probability Checker")
        self.geometry('820x640')
        self.resizable(False, False)

        # Styles
        self.style = ttk.Style(self)
        self.dark_mode = tk.BooleanVar(value=False)
        self._apply_style()

        self._build_ui()

    def _apply_style(self):
        if self.dark_mode.get():
            bg = '#1e1e1e'
            fg = '#e6e6e6'
            entry_bg = '#2a2a2a'
        else:
            bg = '#f5f7fa'
            fg = '#1b1b1b'
            entry_bg = '#ffffff'

        self.configure(bg=bg)
        self.style.configure('TFrame', background=bg)
        self.style.configure('TLabel', background=bg, foreground=fg, font=(None, 10))
        self.style.configure('Header.TLabel', font=('Segoe UI', 18, 'bold'))
        self.style.configure('TButton', font=('Segoe UI', 10))
        self.style.configure('TCombobox', fieldbackground=entry_bg, background=entry_bg)

    def _random_heading(self):
        keywords = ['Java', 'day', 'number', 'probability', 'checker']
        templates = [
            "{0} Day Number Probability Checker",
            "{0} {1} Probability — Number Checker",
            "Smart {0} {2} Probability Checker",
            "{2} {1} {0} Probability Tool",
            "{0} {1} → {2}: Probability Checker",
        ]
        t = random.choice(templates)
        # shuffle keywords slightly for variety
        shuffled = keywords.copy()
        random.shuffle(shuffled)
        # The template expects positions 0..2 (use shuffled)
        return t.format(shuffled[0], shuffled[1], shuffled[2])

    def _build_ui(self):
        top_frame = ttk.Frame(self)
        top_frame.place(x=12, y=12, width=796, height=110)

        heading = ttk.Label(top_frame, text=self._random_heading(), style='Header.TLabel')
        heading.pack(anchor='w', pady=(6, 0))

        subtitle = ttk.Label(top_frame, text='Select a number (1–65) to see its probability based on days 1–31.')
        subtitle.pack(anchor='w', pady=(4, 10))

        # Controls
        controls = ttk.Frame(self)
        controls.place(x=12, y=130, width=380, height=140)

        ttk.Label(controls, text='Choose number:').grid(row=0, column=0, sticky='w', padx=6, pady=8)
        self.choice_var = tk.IntVar(value=60)
        self.number_combo = ttk.Combobox(controls, values=list(range(1, MAX_NUMBER + 1)), width=10, state='readonly')
        self.number_combo.set(60)
        self.number_combo.grid(row=0, column=1, padx=6, pady=8)

        self.check_btn = ttk.Button(controls, text='Check Probability', command=self.check_probability)
        self.check_btn.grid(row=1, column=0, columnspan=2, pady=6, padx=6, sticky='we')

        self.export_btn = ttk.Button(controls, text='Export All to CSV', command=self.export_csv)
        self.export_btn.grid(row=2, column=0, columnspan=2, pady=6, padx=6, sticky='we')

        # Dark mode toggle
        dm = ttk.Checkbutton(controls, text='Dark mode', variable=self.dark_mode, command=self.toggle_dark)
        dm.grid(row=0, column=2, padx=10)

        # Result display
        result_frame = ttk.Frame(self)
        result_frame.place(x=410, y=130, width=398, height=140)
        ttk.Label(result_frame, text='Result:', font=('Segoe UI', 12, 'bold')).pack(anchor='w', pady=(6, 0), padx=6)
        self.result_label = ttk.Label(result_frame, text='Choose a number then click "Check Probability"', wraplength=380)
        self.result_label.pack(anchor='w', padx=6, pady=(6, 0))

        # Insights / info panel
        info_frame = ttk.Frame(self)
        info_frame.place(x=12, y=290, width=796, height=120)
        ttk.Label(info_frame, text='Insights:', font=('Segoe UI', 12, 'bold')).pack(anchor='w', pady=(6, 0), padx=6)

        insight_text = tk.Text(info_frame, height=4, wrap='word', bd=0)
        insight_text.pack(fill='both', expand=True, padx=6, pady=6)
        insight_text.insert('end', self._build_insights())
        insight_text.configure(state='disabled')

        # Optional chart area
        chart_frame = ttk.Frame(self)
        chart_frame.place(x=12, y=420, width=796, height=200)
        ttk.Label(chart_frame, text='Probability Distribution (1–65):', font=('Segoe UI', 11, 'bold')).pack(anchor='w', pady=(4, 0), padx=6)

        if HAS_MPL:
            self._draw_chart(chart_frame)
        else:
            note = ttk.Label(chart_frame, text='Matplotlib not installed — bar chart disabled. Install matplotlib to enable visualization.')
            note.pack(anchor='w', padx=6, pady=12)

    def _build_insights(self):
        lines = []
        # Most likely
        ml_count = COUNTS.get(MOST_LIKELY_NUMBER, 0)
        ml_prob = ml_count / 31 if 31 else 0
        lines.append(f"Most likely number: {MOST_LIKELY_NUMBER} (reachable by {ml_count} different days → probability ≈ {ml_prob:.5f} or {ml_prob*100:.2f}%)")
        # Least likely
        ll_str = ', '.join(str(x) for x in LEAST_LIKELY)
        lines.append(f"Least likely numbers: {ll_str} (each reachable by 1 day → probability ≈ {LEAST_LIKELY_PROB:.5f} or {LEAST_LIKELY_PROB*100:.2f}%)")
        # Extra summary
        distinct_counts = sorted(set(COUNTS.values()), reverse=True)
        lines.append(f"Unique reach counts across numbers: {distinct_counts[:8]} (top values shown)")
        return '\n'.join(lines)

    def check_probability(self):
        try:
            selection = int(self.number_combo.get())
        except Exception:
            messagebox.showerror('Invalid', 'Please select a number between 1 and 65.')
            return
        days = REACHABLE.get(selection, set())
        count = len(days)
        prob = count / 31
        prob_pct = prob * 100
        days_sorted = sorted(days)

        text = f"Number {selection} is reachable by {count} day(s) out of 31.\n"
        text += f"Probability: {prob:.5f} (≈ {prob_pct:.2f}%)\n"
        text += f"Days: {days_sorted if days_sorted else '—'}"

        self.result_label.config(text=text)

    def export_csv(self):
        # Let user choose file
        fp = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV files','*.csv'),('All files','*.*')], title='Save probabilities to CSV')
        if not fp:
            return
        try:
            with open(fp, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Number', 'Reachable_Days_Count', 'Probability_decimal', 'Probability_percent', 'Reachable_Days'])
                for n in range(1, MAX_NUMBER + 1):
                    days = sorted(REACHABLE[n])
                    count = len(days)
                    prob = count / 31
                    writer.writerow([n, count, f"{prob:.5f}", f"{prob*100:.2f}%", ' '.join(map(str, days))])
            messagebox.showinfo('Saved', f'CSV exported to: {fp}')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to save CSV: {e}')

    def _draw_chart(self, parent):
        # Create a simple bar chart showing probabilities
        fig = Figure(figsize=(9.2, 2.6), dpi=100)
        ax = fig.add_subplot(111)
        numbers = list(range(1, MAX_NUMBER + 1))
        probs = [COUNTS[n]/31 for n in numbers]
        ax.bar(numbers, probs)
        ax.set_xlabel('Number')
        ax.set_ylabel('Probability')
        ax.set_xlim(0.5, MAX_NUMBER + 0.5)
        ax.set_ylim(0, max(probs) * 1.08)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        widget = canvas.get_tk_widget()
        widget.pack(fill='both', expand=True, padx=6, pady=6)

    def toggle_dark(self):
        self._apply_style()
        # redraw all widgets' background where needed
        for child in self.winfo_children():
            try:
                child.configure(bg=self['bg'])
            except Exception:
                pass


if __name__ == '__main__':
    app = DayProbabilityApp()
    app.mainloop()
