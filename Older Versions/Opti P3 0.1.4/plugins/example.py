import psutil
import random

def cpu_usage():
    print(f"CPU Usage: {psutil.cpu_percent()}%")

def memory_usage():
    memory = psutil.virtual_memory()
    print(f"Memory Usage: {memory.percent}% (Available: {memory.available // (1024 ** 2)} MB)")

def guess_number_game():
    number = random.randint(1, 100)
    attempts = 0
    while True:
        guess = input("Guess the number (between 1 and 100): ")
        attempts += 1
        if not guess.isdigit():
            print("Please enter a valid number.")
            continue
        guess = int(guess)
        if guess < number:
            print("Too low!")
        elif guess > number:
            print("Too high!")
        else:
            print(f"Congratulations! You've guessed the number in {attempts} attempts.")
            break

commands = {
    'cpu': cpu_usage,
    'memory': memory_usage,
    'guess': guess_number_game
}

info = {
    'title': 'Example',
    'version': '1.0',
    'author': 'Your Name',
    'description': 'Lorem Ipsun or whatever. Requries psutil.',
    'commands': ', '.join(commands.keys())
}
