import click
from core import WitManager
from ui import Ui

class Cli(Ui):
    def run(self):
        main()

@click.group()
def main():
    pass

@main.command()
def init():
    WitManager().init()

@main.command()
@click.argument('path', default='.')
def add(path):
    WitManager().add(path)

@main.command()
@click.argument('message')
def commit(message):
    WitManager().commit(message)

@main.command()
def log():
    WitManager().log()

@main.command()
def status():
    print(WitManager().status())

@main.command()
@click.argument('commit_id')
def checkout(commit_id):
    WitManager().checkout(commit_id)

@main.command()
def push():
    WitManager().push()

if __name__ == "__main__":
    Cli().run()
