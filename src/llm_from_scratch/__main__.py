import argparse

from llm_from_scratch.app import TrainingApp


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Learn how neural networks work, one experiment at a time.",
    )
    parser.parse_args()

    app = TrainingApp()
    app.run()


if __name__ == "__main__":
    main()
