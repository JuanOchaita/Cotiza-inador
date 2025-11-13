
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuración de la conexión a PostgreSQL
DATABASE_URL = "postgresql+psycopg2://myuser:mypassword@localhost:5433/mydb"
engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# Definición del modelo ORM para la tabla "user"
class User(Base):

    __tablename__ = 'user'
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    def __repr__(self):
        return f"<User(id={self.user_id}, email='{self.email}')>"


# Funciones CRUD
def create_user(email: str, password: str):
    """Crea un nuevo usuario"""
    new_user = User(email=email, password=password)
    session.add(new_user)
    session.commit()
    print(f"Usuario creado: {new_user}")
    return new_user

def get_all_users():
    """Obtiene todos los usuarios"""
    users = session.query(User).all()
    print("Usuarios encontrados:", users)
    return users

def get_user_by_email(email: str):
    """Obtiene un usuario por su email"""
    user = session.query(User).filter_by(email=email).first()
    print(f"Usuario con email {email}:", user)
    return user


def get_user_by_email_and_password(email: str, password: str):
    """Obtiene un usuario por email y password"""
    user = session.query(User).filter_by(email=email, password=password).first()
    print(f"Usuario autenticado con email {email}:", user)
    return user

def update_user_email(user_id: int, new_email: str):
    """Actualiza el email de un usuario"""
    user = session.query(User).get(user_id)
    if user:
        user.email = new_email
        session.commit()
        print(f"Usuario actualizado: {user}")
    else:
        print("Usuario no encontrado")
    return user

def delete_user(user_id: int):
    """Elimina un usuario"""
    user = session.query(User).get(user_id)
    if user:
        session.delete(user)
        session.commit()
        print(f"Usuario eliminado: {user}")
    else:
        print("Usuario no encontrado")
    return user

# Test de las funciones CRUD
if __name__ == "__main__":

    create_user("admin", "admin@example.com")
    #print(get_all_users())
    # Buscar usuario por email
    #print(get_user_by_email("alice@example.com"))
    # Actualizar email
    #print(update_user_email(1, "alice_new@example.com"))
    # Eliminar usuario
   #delete_user(7)