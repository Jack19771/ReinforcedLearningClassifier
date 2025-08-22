# console_app.py
from core.document_service import DocumentService
from core.starter_data import load_starter_data

def show_startup_menu(service):
    """Menu startowe z opcją ładowania danych"""
    print("\n=== STARTUP OPTIONS ===")
    
    # Sprawdź czy już są jakieś dane
    total_docs = len(service.db.get_all_documents())
    if total_docs > 0:
        print(f"Found {total_docs} existing documents in database.")
        choice = input("Continue with existing data? (y/n): ").strip().lower()
        if choice == 'y':
            return
    
    print("1. Load starter data (40 examples)")
    print("2. Start with empty database")
    
    choice = input("Choose option (1 or 2): ").strip()
    
    if choice == "1":
        load_starter_data(service.db, service.classifier)
        print("✓ Starter data loaded! You can now use AUTO mode.")
        service.set_mode("auto")  # Przełącz na auto mode
    else:
        print("✓ Starting with empty database in LEARNING mode.")

def main():
    print("=== Document Classifier ===")
    
    service = DocumentService()
    
    # Pokaż menu startowe
    show_startup_menu(service)
    
    while True:
        print(f"\n{'='*40}")
        print(f"Current mode: {service.get_mode().upper()}")
        
        # Reszta kodu bez zmian...
        print("Commands: 'mode auto', 'mode learning', 'stats', 'quit'")
        text = input("Enter document text (or command): ").strip()
        
        if text.lower() == 'quit':
            print("Goodbye!")
            break
            
        # Dodaj komendę stats
        if text.lower() == 'stats':
            categories = service.db.get_categories()
            unique_areas = len(set(cat[0] for cat in categories))
            total_docs = len(service.db.get_all_documents())
            print(f"📊 Total areas: {unique_areas}, Total documents: {total_docs}")
            print(f"📊 Can predict: {service.classifier.can_predict()}")
            continue
            
        # Zmiana trybu
        if text.lower() == 'mode auto':
            if service.classifier.can_predict():
                service.set_mode("auto")
                print("✓ Switched to AUTO mode")
            else:
                print("✗ Need at least 2 categories to use AUTO mode")
            continue
            
        if text.lower() == 'mode learning':
            service.set_mode("learning")
            print("✓ Switched to LEARNING mode")
            continue
            
        if not text:
            print("Please enter some text.")
            continue
            
        # LEARNING MODE - bez zmian
        if service.get_mode() == "learning":
            area = input("What Area is this? ").strip()
            if area:
                subarea = input("SubArea (optional, press Enter to skip): ").strip()
                subarea = subarea if subarea else None
                
                service.db.save_document(text, area, subarea)
                service.classifier.learn(text, area)
                
                print(f"✓ Learned: '{text[:50]}...' → {area}")
                if subarea:
                    print(f"  SubArea: {subarea}")
                
                categories = service.db.get_categories()
                unique_areas = len(set(cat[0] for cat in categories))
                total_docs = len(service.db.get_all_documents())
                print(f"✓ Total areas: {unique_areas}, Total documents: {total_docs}")
                
                if service.classifier.can_predict():
                    print("💡 Tip: You can now use 'mode auto' for automatic classification!")
            else:
                print("Area cannot be empty.")
                
        # AUTO MODE - bez zmian        
        elif service.get_mode() == "auto":
            if service.classifier.can_predict():
                result = service.classifier.predict(text)
                if result:
                    print(f"🤖 Classified as: {result['area']} (confidence: {result['confidence']:.2f})")
                    
                    feedback = input("Is this correct? (y/n): ").strip().lower()
                    if feedback == 'n':
                        correct_area = input("What should it be? ").strip()
                        if correct_area:
                            service.db.save_document(text, correct_area)
                            service.classifier.learn(text, correct_area)
                            print(f"✓ Thanks! Learned: {correct_area}")
                else:
                    print("Unable to classify. Switching to learning mode.")
                    service.set_mode("learning")
            else:
                print("Model not ready. Switching to learning mode.")
                service.set_mode("learning")

if __name__ == "__main__":
    main()