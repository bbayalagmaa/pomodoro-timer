# Pomodoro Focus Timer

A Python-based Pomodoro timer for tracking study sessions across different categories.

## Features

- **4 Study Categories**: English Learning, Chinese Learning, University Study, Online Business
- **25-minute focus sessions** with 5-minute breaks
- **Live countdown timer** in terminal
- **Switch categories** after each break
- **Statistics tracking**: Total time per category, daily sessions, weekly report
- **Persistent storage**: All sessions saved to JSON file

## How to Use

1. Run the script:
   ```bash
   python3 pomodoro.py
   ```

2. Choose a category (1-4) to start studying

3. Press Enter when ready to begin the 25-minute focus session

4. After focus time ends, take a 5-minute break

5. After break, choose your next category or end the session

6. View your statistics anytime with option 5

## Controls

- **1-4**: Select study category
- **5**: View statistics
- **6**: Exit
- **0**: End study session (after break)
- **Ctrl+C**: Stop timer early

## Statistics

The timer tracks:
- Total time spent on each category
- Today's sessions
- Weekly summary

All data is saved to `pomodoro_stats.json`.

## Requirements

- Python 3.x
- No external dependencies

## Author

Created by Sophia (bbayalagmaa) for AI Class Assignment
