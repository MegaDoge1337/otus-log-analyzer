import sys

from src.app.module import HomeworkAnalyzer

if __name__ == "__main__":
    HomeworkAnalyzer().analyze_and_save_report(sys.argv)
