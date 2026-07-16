from .migrations import run_migrations


def initialize_database():
    run_migrations()