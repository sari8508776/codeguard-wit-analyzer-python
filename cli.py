import click
from core import WitManager

@click.group()
def main():
    pass

@main.command()
def init():
    wit = WitManager(".")
    wit.init()

@main.command()
@click.argument('path', default='.')
def add(path):
    wit = WitManager(".")
    wit.add(path)

@main.command()
@click.argument('message')
def commit(message):
    wit = WitManager(".")
    wit.commit(message)

@main.command()
def status():
    wit = WitManager(".")
    print(wit.status())

@main.command()
@click.argument('commit_id')
def checkout(commit_id):
    wit = WitManager(".")
    wit.checkout(commit_id)

@main.command()
def push():
    wit = WitManager(".")
    wit.push()

if __name__ == "__main__":
    main()