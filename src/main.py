from app.module import func, err


if __name__ == "__main__":
    print(func())
    try:
        print(err())
    except RuntimeError as e:
        print(f"Caught an error: {e}")
