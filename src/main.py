from src.config.settings import PROJECT_NAME, VERSION, ENVIRONMENT


def main():
    print("=" * 60)
    print(PROJECT_NAME)
    print("=" * 60)
    print(f"Version      : {VERSION}")
    print(f"Environment  : {ENVIRONMENT}")
    print("System initialization successful!")
    print("=" * 60)


if __name__ == "__main__":
    main()