# test_database.py
import os
from .database_pg import DatabaseManager

# Test czy działa
if __name__ == "__main__":
    # Usuń starą bazę jeśli istnieje
    if os.path.exists("data/classifier.db"):
        os.remove("data/classifier.db")
    
    # Stwórz DatabaseManager
    db = DatabaseManager()
    print("✓ Database created successfully!")
    
    # Sprawdź czy tabele istnieją
    import sqlite3
    with sqlite3.connect("data/classifier.db") as conn:
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"✓ Tables created: {tables}")


# Test zapisywania dokumentu
    print("\n--- Testing document saving ---")
    
    # Zapisz przykładowy dokument
    db.save_document(
        text="Invoice from ABC Company for $500", 
        area="Finanse", 
        subarea="Faktury"
    )
    print("✓ Document saved!")
    
    # Sprawdź czy zapisało się w bazie
    with sqlite3.connect("data/classifier.db") as conn:
        cursor = conn.execute("SELECT * FROM documents")
        docs = cursor.fetchall()
        print(f"✓ Documents in database: {len(docs)}")
        if docs:
            print(f"  First document: {docs[0]}")


# Test odczytywania dokumentów
    print("\n--- Testing data retrieval ---")
    
    # Dodaj jeszcze jeden dokument
    db.save_document(
        text="Meeting notes about project timeline", 
        area="Sluzbowe", 
        subarea="Spotkania"
    )
    
    # Pobierz wszystkie dokumenty
    all_docs = db.get_all_documents()
    print(f"✓ Total documents: {len(all_docs)}")
    
    # Pobierz kategorie
    categories = db.get_categories()
    print(f"✓ Categories found: {categories}")
    
    # Wyświetl wszystkie dokumenty
    print("\n--- All documents ---")
    for doc in all_docs:
        print(f"  {doc[0]}: {doc[2]}/{doc[3]} - '{doc[1][:50]}...'")     