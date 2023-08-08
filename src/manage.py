from manager import Manager

from src.app import server

manager = Manager()


@manager.command
def api():
    server.run(api=True)


@manager.command
def consume():
    server.run(consume=True)


# TODO add command for migrations apply rollback
def server_manager():
    manager.main()
