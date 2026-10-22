def main() -> None:
    """Start the Needle extraction API server."""
    from needle_api.app import run_app

    run_app()


if __name__ == "__main__":
    main()
