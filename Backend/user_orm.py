from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# PostgreSQL connection configuration
DATABASE_URL = "postgresql+psycopg2://myuser:mypassword@localhost:5433/mydb"
engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


# ORM Model
class User(Base):
    __tablename__ = 'user'
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    email = Column(String, unique=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    def __repr__(self):
        #return f"<User(id={self.user_id}, name='{self.name}', email='{self.email}')>"
        return None

# CRUD Functions
def create_user(name: str, email: str):
    """Creates a new user"""
    new_user = User(name=name, email=email)
    session.add(new_user)
    session.commit()
    print(f"User successfully created: {new_user}")
    return new_user


def login_user():
    """Asks for credentials and returns (username, email) if correct, or None if failed."""
    username = input("Enter your username: ").strip()
    email = input("Enter your email: ").strip()

    user = session.query(User).filter_by(name=username, email=email).first()

    if user:
        #print(f"Welcome, {user.name}!")
        return user.name, user.email
    else:
        print("The username or email is incorrect. Returning to the main menu...")
        return None


def main_menu():
    """
    Displays the main menu and manages user actions.
    If the user logs in successfully, returns (username, email).
    If the user exits or fails to log in, returns None.
    """
    Base.metadata.create_all(engine)

    while True:
        print("\n===== MAIN MENU =====")
        print("1. Log in")
        print("2. Create user")
        print("3. Exit")
        option = input("Select an option (1-3): ").strip()

        if option == "1":
            result = login_user()
            if result:
                username, email = result
                #print(f"Successfully logged in as: {username} ({email})")
                return username, email  # ← returns upon successful login

        elif option == "2":
            username = input("Enter a username: ").strip()
            email = input("Enter an email address: ").strip()

            # Validate if it already exists
            existing_user = session.query(User).filter(
                (User.name == username) | (User.email == email)
            ).first()

            if existing_user:
                print("The username or email already exists. Try different data.")
            else:
                create_user(username, email)

        elif option == "3":
            print("Exiting the program...")
            return None  # ← returns None if the user exits

        else:
            print("Invalid option. Please try again.")


# Entry point
if __name__ == "__main__":
    result = main_menu()
    if result:
        username, email = result
        print(f"\nAuthenticated user: {username} ({email})")
    else:
        print("\nProgram ended without login.")
