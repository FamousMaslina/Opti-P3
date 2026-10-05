import os

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def edit_file(filepath):
    # Load existing content or create new
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            lines = f.readlines()
    else:
        lines = []

    while True:
        clear()
        print(f"Editing: {filepath} — Ctrl+S to save, Ctrl+X to exit\n")

        for idx, line in enumerate(lines):
            print(f"{idx + 1:>3}: {line.rstrip()}")

        try:
            action = input("\n[L]ine to edit (e.g., 2), [A]dd new line, [D]elete, [S]ave, [Q]uit: ").strip().lower()
            if action == 's':
                with open(filepath, 'w') as f:
                    f.writelines(lines)
                print("Saved.")
            elif action == 'q':
                break
            elif action == 'a':
                new_line = input("Enter new line content: ")
                lines.append(new_line + '\n')
            elif action == 'd':
                index = int(input("Line number to delete: ")) - 1
                if 0 <= index < len(lines):
                    del lines[index]
            else:
                index = int(action) - 1
                if 0 <= index < len(lines):
                    new_content = input(f"Edit line {index+1}: ")
                    lines[index] = new_content + '\n'
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    path = input("Enter path to file (relative to root/): ").strip()
    if not path.startswith("/"):
        path = os.path.join(os.path.dirname(__file__), path)
    edit_file(path)