import data.database as database


def reset_tables() -> None:
    database.delete_tables()
    database.create_tables()


def display_tables() -> None:
    projects = database.get_all_projects()
    pomos = database.get_all_pomodoros()

    print("PROJECTS:")
    for project in projects:
        print(project)

    print("\nPOMODOROS:")
    for pomo in pomos:
        print(f"Project: {pomo[0]} | Time: {pomo[1]}, Length: {pomo[2]}")


if __name__ == "__main__":
    display_tables()
