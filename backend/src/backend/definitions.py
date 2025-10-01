import dagster as dg

@dg.asset
def hello_backend():
    """A simple test asset for the backend"""
    return "Hello from backend!"

@dg.definitions
def defs():
    return dg.Definitions(
        assets=[hello_backend]
    )