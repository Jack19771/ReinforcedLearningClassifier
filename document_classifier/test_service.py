# test_service.py
from core.document_service import DocumentService

if __name__ == "__main__":
    print("--- Testing DocumentService ---")
    
    # Stwórz serwis
    service = DocumentService()
    print("✓ DocumentService created")
    
    # Sprawdź tryb
    mode = service.get_mode()
    print(f"✓ Default mode: {mode}")
    
    # Zmień tryb
    result1 = service.set_mode("auto")
    print(f"✓ Set to auto: {result1}")
    print(f"✓ Current mode: {service.get_mode()}")
    
    # Nieprawidłowy tryb
    result2 = service.set_mode("invalid")
    print(f"✓ Invalid mode rejected: {result2}")
    print(f"✓ Mode unchanged: {service.get_mode()}")
    
    # Sprawdź czy ma dostęp do bazy i klasyfikatora
    print(f"✓ Has database: {service.db is not None}")
    print(f"✓ Has classifier: {service.classifier is not None}")