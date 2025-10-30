from user_orm import main_menu
from collection_orm import get_collections_by_user, collection_menu

if __name__ == "__main__":
    result = main_menu()
    if result:
        user_id, username, email = result
        get_collections_by_user(user_id)
        collection_id = collection_menu(user_id)