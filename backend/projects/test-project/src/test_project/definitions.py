import dagster as dg

@dg.asset
def hello_world():
    """A simple test asset"""
    return "Hello, Dagster!"

@dg.definitions
def defs():
    return dg.Definitions(
        assets=[hello_world]
    )