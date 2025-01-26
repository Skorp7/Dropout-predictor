import sys
import time

class ProgressLogger:
    def __init__(self, total, bar_width = 50):
        self.total     = total  # Total steps to complete
        self.bar_width = bar_width
        self.current   = 0

    def increase_total(self, increase):
        self.total += increase

    def update(self):
        self.current += 1
        self.print_bar()

    def print_bar(self):
        # Calculate the percentage of completion
        percent = (self.current / self.total) * 100

        if (percent > 100):
            # Be sure percentages does not go over 100 even tough programmer has messed up. :)
            self.current = self.total * 0.99

        # Calculate the number of blocks to display in the progress bar
        block = int(self.bar_width * self.current / self.total)
        # Create the progress bar
        bar = f"[{'#' * block}{'.' * (self.bar_width - block)}] {percent:3.0f}%"
        # Print the progress bar, overwrite the line each time
        sys.stdout.write(f"\r{bar}")
        sys.stdout.flush()

    def finish(self):
        self.current = self.total
        self.print_bar()
