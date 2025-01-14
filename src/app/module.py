import time


def func():
    return {"num": 42, "ts": int(time.time())}


def err():
    raise RuntimeError(
        "Oops i did it again"
        "I played with your heart "
        "Got lost in the game "
        "Oh baby, baby..."
    )
