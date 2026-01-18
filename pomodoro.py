#!/usr/bin/env python3
"""
Pomodoro Focus Timer for Sofia
Track your study sessions across customizable categories.
"""

import json
import time
import os
from datetime import datetime, timedelta

# Configuration
FOCUS_MINUTES = 25  # Standard pomodoro: 25 minutes
BREAK_MINUTES = 5   # Short break: 5 minutes
STATS_FILE = "pomodoro_stats.json"

# Default categories (used only on first run)
DEFAULT_CATEGORIES = [
    "English Learning",
    "Chinese Learning",
    "University Study",
    "Online Business"
]

def clear_screen():
    """Clear terminal screen."""
    os.system('clear' if os.name != 'nt' else 'cls')

def load_data():
    """Load stats and categories from JSON file."""
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, 'r') as f:
            data = json.load(f)
            # Ensure categories exist in data
            if "categories" not in data:
                data["categories"] = DEFAULT_CATEGORIES.copy()
            return data
    return {
        "sessions": [],
        "total_by_category": {},
        "categories": DEFAULT_CATEGORIES.copy()
    }

def save_data(data):
    """Save stats and categories to JSON file."""
    with open(STATS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def format_time(seconds):
    """Format seconds as MM:SS."""
    mins, secs = divmod(seconds, 60)
    return f"{mins:02d}:{secs:02d}"

def countdown_timer(minutes, category, is_break=False):
    """Run countdown timer with display."""
    total_seconds = int(minutes * 60)

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

        print("\a")  # Terminal bell
        return True, minutes

    except KeyboardInterrupt:
        elapsed = total_seconds - remaining
        elapsed_mins = elapsed // 60
        print(f"\n\n  Stopped early. Completed: {format_time(elapsed)}")
        return False, elapsed_mins

def run_pomodoro(category, data):
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

    completed, minutes = countdown_timer(FOCUS_MINUTES, category)

    if minutes > 0:
        session = {
            "category": category,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M"),
            "minutes": minutes,
            "completed": completed
        }
        data["sessions"].append(session)

        if category not in data["total_by_category"]:
            data["total_by_category"][category] = 0
        data["total_by_category"][category] += minutes

        save_data(data)
        print(f"\n  +{minutes} minutes added to {category}")

    if completed:
        input("\nPress Enter to start break...")
        countdown_timer(BREAK_MINUTES, category, is_break=True)
        return choose_next_action(data)

    return False

def choose_next_action(data):
    """Let user choose next category or end session after break."""
    categories = data["categories"]

    print("\n" + "=" * 40)
    print("  WHAT'S NEXT?")
    print("=" * 40)
    print("\n  Choose your next focus:\n")

    for i, category in enumerate(categories, 1):
        print(f"  {i}. {category}")

    print(f"\n  0. End Study Session")
    print("\n" + "-" * 40)

    try:
        choice = input("  Enter your choice: ").strip()
        choice = int(choice)

        if choice == 0:
            return False
        elif 1 <= choice <= len(categories):
            category = categories[choice - 1]
            run_pomodoro(category, data)
            return True
        else:
            print("  Invalid choice. Returning to menu.")
            return False
    except (ValueError, EOFError):
        return False

def show_stats(data):
    """Display statistics."""
    categories = data["categories"]

    clear_screen()
    print("\n" + "=" * 50)
    print("  POMODORO STATISTICS")
    print("=" * 50)

    print("\n  TOTAL TIME BY CATEGORY:")
    print("-" * 50)

    total_all = 0
    for category in categories:
        mins = data["total_by_category"].get(category, 0)
        total_all += mins
        hours = mins // 60
        remaining_mins = mins % 60

        if hours > 0:
            print(f"  {category:20} {hours}h {remaining_mins}m")
        else:
            print(f"  {category:20} {mins}m")

    # Also show stats for deleted categories that have data
    for category, mins in data["total_by_category"].items():
        if category not in categories and mins > 0:
            total_all += mins
            hours = mins // 60
            remaining_mins = mins % 60
            if hours > 0:
                print(f"  {category:20} {hours}h {remaining_mins}m (archived)")
            else:
                print(f"  {category:20} {mins}m (archived)")

    print("-" * 50)
    total_hours = total_all // 60
    total_mins = total_all % 60
    print(f"  {'TOTAL':20} {total_hours}h {total_mins}m")

    today = datetime.now().strftime("%Y-%m-%d")
    today_sessions = [s for s in data["sessions"] if s["date"] == today]

    if today_sessions:
        print("\n  TODAY'S SESSIONS:")
        print("-" * 50)
        for s in today_sessions:
            status = "Complete" if s["completed"] else "Partial"
            print(f"  {s['time']} | {s['category']:20} | {s['minutes']}m | {status}")

        today_total = sum(s["minutes"] for s in today_sessions)
        print(f"\n  Today's total: {today_total} minutes ({len(today_sessions)} sessions)")

    week_ago = datetime.now() - timedelta(days=7)
    week_sessions = [s for s in data["sessions"]
                     if datetime.strptime(s["date"], "%Y-%m-%d") >= week_ago]

    if week_sessions:
        print("\n  THIS WEEK:")
        print("-" * 50)
        week_total = sum(s["minutes"] for s in week_sessions)
        week_hours = week_total // 60
        week_mins = week_total % 60
        print(f"  Total: {week_hours}h {week_mins}m ({len(week_sessions)} sessions)")

        week_by_cat = {}
        for s in week_sessions:
            cat = s["category"]
            week_by_cat[cat] = week_by_cat.get(cat, 0) + s["minutes"]

        for cat, mins in sorted(week_by_cat.items(), key=lambda x: -x[1]):
            print(f"  - {cat}: {mins}m")

    input("\nPress Enter to continue...")

def manage_categories(data):
    """Manage categories - add, edit, delete."""
    while True:
        categories = data["categories"]

        clear_screen()
        print("\n" + "=" * 40)
        print("  MANAGE CATEGORIES")
        print("=" * 40)
        print("\n  Current categories:\n")

        for i, category in enumerate(categories, 1):
            print(f"  {i}. {category}")

        print("\n" + "-" * 40)
        print("  Options:")
        print("  A. Add new category")
        print("  E. Edit category")
        print("  D. Delete category")
        print("  0. Back to main menu")
        print("-" * 40)

        choice = input("\n  Enter your choice: ").strip().upper()

        if choice == "A":
            add_category(data)
        elif choice == "E":
            edit_category(data)
        elif choice == "D":
            delete_category(data)
        elif choice == "0":
            break
        else:
            print("  Invalid choice.")
            time.sleep(1)

def add_category(data):
    """Add a new category."""
    print("\n  ADD NEW CATEGORY")
    print("-" * 40)

    name = input("  Enter category name (or 0 to cancel): ").strip()

    if name == "0" or not name:
        return

    if name in data["categories"]:
        print(f"  '{name}' already exists!")
        time.sleep(1)
        return

    data["categories"].append(name)
    save_data(data)
    print(f"\n  Added: {name}")
    time.sleep(1)

def edit_category(data):
    """Edit an existing category."""
    categories = data["categories"]

    if not categories:
        print("  No categories to edit.")
        time.sleep(1)
        return

    print("\n  EDIT CATEGORY")
    print("-" * 40)

    try:
        num = input("  Enter category number to edit (or 0 to cancel): ").strip()
        if num == "0":
            return

        idx = int(num) - 1
        if 0 <= idx < len(categories):
            old_name = categories[idx]
            new_name = input(f"  New name for '{old_name}' (or 0 to cancel): ").strip()

            if new_name == "0" or not new_name:
                return

            if new_name in categories:
                print(f"  '{new_name}' already exists!")
                time.sleep(1)
                return

            # Update category name
            categories[idx] = new_name

            # Update stats to new name
            if old_name in data["total_by_category"]:
                data["total_by_category"][new_name] = data["total_by_category"].pop(old_name)

            # Update session history
            for session in data["sessions"]:
                if session["category"] == old_name:
                    session["category"] = new_name

            save_data(data)
            print(f"\n  Renamed: {old_name} -> {new_name}")
            time.sleep(1)
        else:
            print("  Invalid number.")
            time.sleep(1)
    except ValueError:
        print("  Invalid input.")
        time.sleep(1)

def delete_category(data):
    """Delete a category."""
    categories = data["categories"]

    if not categories:
        print("  No categories to delete.")
        time.sleep(1)
        return

    if len(categories) == 1:
        print("  Cannot delete the last category. Add another first.")
        time.sleep(1)
        return

    print("\n  DELETE CATEGORY")
    print("-" * 40)

    try:
        num = input("  Enter category number to delete (or 0 to cancel): ").strip()
        if num == "0":
            return

        idx = int(num) - 1
        if 0 <= idx < len(categories):
            name = categories[idx]
            confirm = input(f"  Delete '{name}'? (y/n): ").strip().lower()

            if confirm == "y":
                categories.pop(idx)
                save_data(data)
                print(f"\n  Deleted: {name}")
                print("  (Stats are kept in archive)")
            else:
                print("  Cancelled.")
            time.sleep(1)
        else:
            print("  Invalid number.")
            time.sleep(1)
    except ValueError:
        print("  Invalid input.")
        time.sleep(1)

def reset_stats(data):
    """Reset all statistics."""
    clear_screen()
    print("\n" + "=" * 40)
    print("  RESET STATISTICS")
    print("=" * 40)
    print("\n  This will delete ALL your session history")
    print("  and time tracking data.")
    print("\n  Your categories will be kept.")
    print("\n" + "-" * 40)

    confirm = input("\n  Are you sure? Type 'yes' to confirm: ").strip().lower()

    if confirm == "yes":
        data["sessions"] = []
        data["total_by_category"] = {}
        save_data(data)
        print("\n  Statistics have been reset!")
        print("  Starting fresh. Good luck!")
    else:
        print("\n  Cancelled. Your data is safe.")

    time.sleep(2)

def main_menu(data):
    """Display main menu and get choice."""
    categories = data["categories"]

    clear_screen()
    print("\n" + "=" * 40)
    print("  POMODORO FOCUS TIMER")
    print("  For Sofia's Study Sessions")
    print("=" * 40)
    print("\n  Choose your focus category:\n")

    for i, category in enumerate(categories, 1):
        print(f"  {i}. {category}")

    print(f"\n  S. View Statistics")
    print(f"  M. Manage Categories")
    print(f"  R. Reset Statistics")
    print(f"  Q. Exit")

    print("\n" + "-" * 40)

    try:
        choice = input("  Enter your choice: ").strip().upper()
        return choice
    except EOFError:
        return "Q"

def main():
    """Main program loop."""
    data = load_data()

    while True:
        categories = data["categories"]
        choice = main_menu(data)

        # Check if it's a number (category selection)
        try:
            num = int(choice)
            if 1 <= num <= len(categories):
                category = categories[num - 1]
                run_pomodoro(category, data)
            else:
                print("\n  Invalid choice. Please try again.")
                time.sleep(1)
        except ValueError:
            # It's a letter command
            if choice == "S":
                show_stats(data)
            elif choice == "M":
                manage_categories(data)
            elif choice == "R":
                reset_stats(data)
            elif choice == "Q":
                clear_screen()
                print("\n  Keep up the great work, Sofia!")
                print("  See you next study session!\n")
                break
            else:
                print("\n  Invalid choice. Please try again.")
                time.sleep(1)

if __name__ == "__main__":
    main()
