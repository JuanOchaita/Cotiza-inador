from user_orm import main_menu

if __name__ == "__main__":
    result = main_menu()
    if result:
        username, email = result
        print(f"Logging: {username} ({email})")