from vault import create_vault, vault_exists, add_entry, list_entries, get_entry, delete_entry


def menu():
    while True:
        print("\n1. List entries")
        print("2. Add entry")
        print("3. Get entry")
        print("4. Delete entry")
        print("5. Exit\n")

        try:
            choice = int(input("Your choice: "))
        except ValueError:
            print("Invalid choice")
            continue

        if choice == 1:
            list_entries()
        elif choice == 2:
            add_entry()
        elif choice == 3:
            get_entry()
        elif choice == 4:
            delete_entry()
        elif choice == 5:
            break
        else:
            print("Invalid choice")

    print("Thank you for using Espresso!")


if __name__ == "__main__":
    if not vault_exists():
        create_vault()

    menu()
