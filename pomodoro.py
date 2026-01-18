#!/usr/bin/env python3
"""
Pomodoro Focus Timer for Sophia
Track your study sessions across different categories:
- English Learning
- Chinese Learning
- University Study
- Online Business
"""

import json
import time
import os
from datetime import datetime, timedelta

# Configuration
FOCUS_MINUTES = 25  # Standard pomodoro: 25 minutes
BREAK_MINUTES = 5   # Short break: 5 minutes
STATS_FILE = "pomodoro_stats.json"

# Categories
CATEGORIES = [
    "English Learning",
    "Chinese Learning",
    "University Study",
    "Online Business"
]

def clear_screen():
    """Clear terminal screen."""
    os.system('clear' if os.name != 'nt' else 'cls')

def load_stats():
    """Load stats from JSON file."""
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, 'r') as f:
            return json.load(f)
    return {"sessions": [], "total_by_category": {cat: 0 for cat in CATEGORIES}}

def save_stats(stats):
    """Save stats to JSON file."""
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=2)

def format_time(seconds):
    """Format seconds as MM:SS."""
    mins, secs = divmod(seconds, 60)
    return f"{mins:02d}:{secs:02d}"

def countdown_timer(minutes, category, is_break=False):
    """Run countdown timer with display."""
    total_seconds = int(minutes * 60)
    session_type = "Break" if is_break else "Focus"

    print(f"\n{'=' * 40}")
    if is_break:
        print(f"  BREAK TIME - Relax for {minutes} minutes")
    else:
        print(f"  FOCUS: {category}")
        print(f"  Duration: {minutes} minutes")
    print(f"{'=' * 40}")
    print("\nPress Ctrl+C anytime to end early\n")

    try:
        for remaining in range(total_seconds, 0, -1):
            if is_break:
                print(f"\r  BREAK - Time remaining: {format_time(remaining)}  ", end="", flush=True)
            else:
                print(f"\r  {category.upper()} - Time remaining: {format_time(remaining)}  ", end="", flush=True)
            time.sleep(1)

        print(f"\r  Time remaining: 00:00  ")
        print("\n" + "=" * 40)

        if is_break:
            print("  Break over! Ready for another session?")
        else:
            print("  Session complete! Great work!")
        print("=" * 40)

        # Play sound (bell)
        print("\a")  # Terminal bell
        return True, minutes

    except KeyboardInterrupt:
        elapsed = total_seconds - remaining
        elapsed_mins = elapsed // 60
        print(f"\n\n  Stopped early. Completed: {format_time(elapsed)}")
        return False, elapsed_mins

def run_pomodoro(category, stats):
    """Run a full pomodoro session."""
    clear_screen()
    print("\n" + "=" * 40)
    print(f"  YOUR {category.upper()} POMODORO STARTING!")
    print("=" * 40)
    print(f"\n  Get ready to focus on: {category}")
    duration_secs = int(FOCUS_MINUTES * 60)
    if duration_secs < 60:
        print(f"  Duration: {duration_secs} seconds")
    else:
        print(f"  Duration: {int(FOCUS_MINUTES)} minute(s)")
    input("\n  Press Enter when you're ready to start...")

    # Focus session
    completed, minutes = countdown_timer(FOCUS_MINUTES, category)

    if minutes > 0:
        # Record session
        session = {
            "category": category,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M"),
            "minutes": minutes,
            "completed": completed
        }
        stats["sessions"].append(session)

        # Update totals
        if category not in stats["total_by_category"]:
            stats["total_by_category"][category] = 0
        stats["total_by_category"][category] += minutes

        save_stats(stats)
        print(f"\n  +{minutes} minutes added to {category}")

    if completed:
        input("\nPress Enter to start break...")
        countdown_timer(BREAK_MINUTES, category, is_break=True)

        # After break, offer to switch category or end
        return choose_next_action(stats)

    return False  # Return to main menu

def choose_next_action(stats):
    """Let user choose next category or end session after break."""
    print("\n" + "=" * 40)
    print("  WHAT'S NEXT?")
    print("=" * 40)
    print("\n  Choose your next focus:\n")

    for i, category in enumerate(CATEGORIES, 1):
        print(f"  {i}. {category}")

    print(f"\n  0. End Study Session")
    print("\n" + "-" * 40)

    try:
        choice = input("  Enter your choice: ").strip()
        choice = int(choice)

        if choice == 0:
            return False  # End session, go to main menu
        elif 1 <= choice <= len(CATEGORIES):
            category = CATEGORIES[choice - 1]
            run_pomodoro(category, stats)
            return True
        else:
            print("  Invalid choice. Returning to menu.")
            return False
    except (ValueError, EOFError):
        return False

def show_stats(stats):
    """Display statistics."""
    clear_screen()
    print("\n" + "=" * 50)
    print("  POMODORO STATISTICS")
    print("=" * 50)

    # Total by category
    print("\n  TOTAL TIME BY CATEGORY:")
    print("-" * 50)

    total_all = 0
    for category in CATEGORIES:
        mins = stats["total_by_category"].get(category, 0)
        total_all += mins
        hours = mins // 60
        remaining_mins = mins % 60
        bar = "" * (mins // 10)  # Visual bar

        if hours > 0:
            print(f"  {category:20} {hours}h {remaining_mins}m  {bar}")
        else:
            print(f"  {category:20} {mins}m  {bar}")

    print("-" * 50)
    total_hours = total_all // 60
    total_mins = total_all % 60
    print(f"  {'TOTAL':20} {total_hours}h {total_mins}m")

    # Today's sessions
    today = datetime.now().strftime("%Y-%m-%d")
    today_sessions = [s for s in stats["sessions"] if s["date"] == today]

    if today_sessions:
        print("\n  TODAY'S SESSIONS:")
        print("-" * 50)
        for s in today_sessions:
            status = "Complete" if s["completed"] else "Partial"
            print(f"  {s['time']} | {s['category']:20} | {s['minutes']}m | {status}")

        today_total = sum(s["minutes"] for s in today_sessions)
        print(f"\n  Today's total: {today_total} minutes ({len(today_sessions)} sessions)")

    # Weekly report
    week_ago = datetime.now() - timedelta(days=7)
    week_sessions = [s for s in stats["sessions"]
                     if datetime.strptime(s["date"], "%Y-%m-%d") >= week_ago]

    if week_sessions:
        print("\n  THIS WEEK:")
        print("-" * 50)
        week_total = sum(s["minutes"] for s in week_sessions)
        week_hours = week_total // 60
        week_mins = week_total % 60
        print(f"  Total: {week_hours}h {week_mins}m ({len(week_sessions)} sessions)")

        # By category this week
        week_by_cat = {}
        for s in week_sessions:
            cat = s["category"]
            week_by_cat[cat] = week_by_cat.get(cat, 0) + s["minutes"]

        for cat, mins in sorted(week_by_cat.items(), key=lambda x: -x[1]):
            print(f"  - {cat}: {mins}m")

    input("\nPress Enter to continue...")

def main_menu():
    """Display main menu and get choice."""
    clear_screen()
    print("\n" + "=" * 40)
    print("  POMODORO FOCUS TIMER")
    print("  For Sophia's Study Sessions")
    print("=" * 40)
    print("\n  Choose your focus category:\n")

    for i, category in enumerate(CATEGORIES, 1):
        print(f"  {i}. {category}")

    print(f"\n  {len(CATEGORIES) + 1}. View Statistics")
    print(f"  {len(CATEGORIES) + 2}. Exit")

    print("\n" + "-" * 40)

    try:
        choice = input("  Enter your choice: ").strip()
        return int(choice)
    except (ValueError, EOFError):
        return 0

def main():
    """Main program loop."""
    stats = load_stats()

    while True:
        choice = main_menu()

        if 1 <= choice <= len(CATEGORIES):
            category = CATEGORIES[choice - 1]
            run_pomodoro(category, stats)
        elif choice == len(CATEGORIES) + 1:
            show_stats(stats)
        elif choice == len(CATEGORIES) + 2:
            clear_screen()
            print("\n  Keep up the great work, Sophia!")
            print("  See you next study session!\n")
            break
        else:
            print("\n  Invalid choice. Please try again.")
            time.sleep(1)

if __name__ == "__main__":
    main()
