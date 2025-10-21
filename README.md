# Day-based-probability-tracker
Day based probability checker is a python desktop application that visualizes how likely a number (1-65) can be "reached/selected" by multiplying the days of a month(1-31) by positive integers.

## ✨ Features
- Tkinter GUI with random heading
- Dropdown selector (1–65)
- Probability output (decimal + %)
- Insights: most/least likely numbers
- Optional matplotlib bar chart
- Dark mode toggle
- Export all results to CSV

## 🧮 Logic
Each number N (1–65) is “reachable” if there exists a day D (1–31)
and an integer M such that D × M = N.  
Probability = (reachable days) / 31.

## 🧱 Installation
```bash
git clone https://github.com/yourusername/day-based-probability-checker.git
cd day-based-probability-checker
python day_based_probability_checker.py
