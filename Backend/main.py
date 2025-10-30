from user_orm import main_menu
from collection_orm import get_collections_by_user

if __name__ == "__main__":
    result = main_menu()
    if result:
        user_id, username, email = result
        get_collections_by_user(user_id)
        
from user_orm import main_menu  # debe retornar (user_id, username, email)
from collections_cli import (
    list_collections,
    add_collection,
    delete_collection_by_id,
    delete_collection_by_name,
)
import os, sys

def limpiar(): os.system("cls" if os.name == "nt" else "clear")
def pausar(): input("\nPresiona ENTER para continuar...")

def menu(user_id: int):
    while True:
        limpiar()
        print("""
===========================
   GESTIÓN DE COLECCIONES
===========================
[1] Ver colecciones
[2] Agregar colección
[3] Eliminar colección
[4] Salir
""")
        op = input("Elegí una opción: ").strip()

        if op == "1":
            rows = list_collections(user_id)
            if not rows:
                print("\n(0) colecciones registradas.\n")
            else:
                print("\nID │ NOMBRE │ DESCRIPCIÓN │ FECHA")
                print("--------------------------------------")
                for c in rows:
                    print(f"{c.id:<3}│ {c.name:<15}│ {c.description or '-':<20}│ {c.created_at}")
            pausar()

        elif op == "2":
            name = input("Nombre: ").strip()
            desc = input("Descripción (opcional): ").strip() or None
            add_collection(user_id, name, desc)
            pausar()

        elif op == "3":
            modo = input("¿Eliminar por [1] ID o [2] Nombre?: ").strip()
            if modo == "1":
                try:
                    cid = int(input("ID: ").strip())
                    delete_collection_by_id(user_id, cid)
                except ValueError:
                    print("⚠️ ID inválido.")
            elif modo == "2":
                name = input("Nombre exacto: ").strip()
                delete_collection_by_name(user_id, name)
            else:
                print("⚠️ Opción inválida.")
            pausar()

        elif op == "4":
            print("\nAdiós 👋\n")
            break

        else:
            print("\n⚠️ Opción inválida.")
            pausar()

if __name__ == "__main__":
    try:
        auth = main_menu()  # debe devolver (user_id, username, email)
        if not auth:
            print("\nNo se pudo iniciar sesión. Saliendo…\n")
            sys.exit(1)
        user_id, username, email = auth
        menu(user_id)
    except KeyboardInterrupt:
        print("\n\nInterrumpido por el usuario. Adiós!\n")
        sys.exit(0)