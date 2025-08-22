# test_classifier.py
from core.classifier import ClassificationEngine

if __name__ == "__main__":
    print("--- Testing ClassificationEngine ---")
    
    # Stwórz pusty model
    engine = ClassificationEngine()
    print("✓ ClassificationEngine created")
    
    # Sprawdź czy może predykować
    can_predict = engine.can_predict()
    print(f"✓ Can predict: {can_predict}")
    print(f"✓ Categories: {engine.categories}")
    print(f"✓ Is trained: {engine.is_trained}")
    
    # To powinno być False - model jest pusty
    if not can_predict:
        print("✓ Correctly shows it cannot predict yet")
    else:
        print("✗ Error: empty model should not be able to predict")



# Test uczenia
    print("\n--- Testing learning ---")
    
    # Pierwszy przykład
    result1 = engine.learn("Invoice from company", "Finanse")
    print(f"✓ First example learned: {result1}")
    print(f"✓ Categories after 1: {engine.categories}")
    print(f"✓ Can predict after 1: {engine.can_predict()}")
    
    # Drugi przykład
    result2 = engine.learn("Meeting notes", "Sluzbowe") 
    print(f"✓ Second example learned: {result2}")
    print(f"✓ Can predict after 2: {engine.can_predict()}")