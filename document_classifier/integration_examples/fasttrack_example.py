# integration_examples/fasttrack_example.py
"""
FastTrack Integration Example
Pokazuje jak FastTrack może używać Document Classifier
"""

import requests
import json
from typing import Optional, Dict, Any

class DocumentClassifierClient:
    """Client dla Document Classifier API"""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.system_id = "fasttrack"
    
    def classify_document(self, text: str, confidence_threshold: float = 0.7) -> Dict[str, Any]:
        """Klasyfikuj dokument"""
        
        response = requests.post(f"{self.api_url}/v1/classify", json={
            "text": text,
            "system_id": self.system_id,
            "confidence_threshold": confidence_threshold,
            "context": {
                "source": "fasttrack",
                "user_agent": "FastTrack/1.0"
            }
        })
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Classification failed: {response.text}")
    
    def send_feedback(self, text: str, correct_area: str, predicted_area: str = None, 
                     correct_subarea: str = None, user_id: str = None):
        """Wyślij feedback do systemu"""
        
        response = requests.post(f"{self.api_url}/v1/feedback", json={
            "text": text,
            "correct_area": correct_area,
            "correct_subarea": correct_subarea,
            "predicted_area": predicted_area,
            "system_id": self.system_id,
            "user_id": user_id
        })
        
        return response.json()
    
    def get_categories(self) -> Dict[str, Any]:
        """Pobierz dostępne kategorie"""
        
        response = requests.get(f"{self.api_url}/v1/categories")
        return response.json()
    
    def health_check(self) -> Dict[str, Any]:
        """Sprawdź status systemu"""
        
        response = requests.get(f"{self.api_url}/v1/health")
        return response.json()

# Przykład użycia w FastTrack
class FastTrackDocumentProcessor:
    """Przykład integracji z FastTrack"""
    
    def __init__(self):
        self.classifier = DocumentClassifierClient()
        
        # Mapowanie kategorii FastTrack → Document Classifier
        self.category_mapping = {
            "Finanse": "accounting",
            "Sluzbowe": "hr", 
            "Daily Business": "operations",
            "Prywatne": "personal"
        }
    
    def process_email_attachment(self, email_content: str, user_id: str):
        """Przetwarzaj załącznik email"""
        
        try:
            # Klasyfikuj dokument
            result = self.classifier.classify_document(email_content)
            
            fasttrack_category = self.category_mapping.get(result['area'], 'uncategorized')
            
            return {
                "fasttrack_category": fasttrack_category,
                "confidence": result['confidence'],
                "suggested_area": result['area'],
                "suggested_subarea": result.get('subarea'),
                "auto_assign": result['confidence'] > 0.8  # Auto-assign if high confidence
            }
            
        except Exception as e:
            print(f"Classification error: {e}")
            return {"fasttrack_category": "uncategorized", "error": str(e)}
    
    def handle_user_correction(self, document_text: str, user_selected_category: str, 
                              predicted_category: str, user_id: str):
        """Obsługuj korekty użytkownika"""
        
        # Zmapuj FastTrack kategorię z powrotem na Document Classifier
        reverse_mapping = {v: k for k, v in self.category_mapping.items()}
        correct_area = reverse_mapping.get(user_selected_category, user_selected_category)
        predicted_area = reverse_mapping.get(predicted_category, predicted_category)
        
        # Wyślij feedback
        self.classifier.send_feedback(
            text=document_text,
            correct_area=correct_area,
            predicted_area=predicted_area,
            user_id=user_id
        )

# Przykład workflow w FastTrack
def fasttrack_workflow_example():
    """Przykład kompletnego workflow"""
    
    processor = FastTrackDocumentProcessor()
    
    # 1. Nowy dokument w FastTrack
    document_text = "Invoice #12345 from ABC Company for office supplies totaling $1,247.89"
    user_id = "john.doe@company.com"
    
    # 2. Automatyczna klasyfikacja
    classification = processor.process_email_attachment(document_text, user_id)
    
    print("Auto-classification result:")
    print(json.dumps(classification, indent=2))
    
    # 3. Jeśli user skoryguje kategorię
    if classification.get("auto_assign") == False:  # Low confidence
        # User wybiera kategorię w FastTrack UI
        user_selected = "accounting"  # FastTrack category
        
        # Wyślij feedback
        processor.handle_user_correction(
            document_text=document_text,
            user_selected_category=user_selected,
            predicted_category=classification.get("fasttrack_category"),
            user_id=user_id
        )
        
        print("Feedback sent to improve model")

if __name__ == "__main__":
    # Test integracji
    client = DocumentClassifierClient()
    
    # Health check
    health = client.health_check()
    print("System health:", health)
    
    # Test klasyfikacji
    test_text = "Meeting notes from quarterly review with team leads"
    result = client.classify_document(test_text)
    print("\nClassification result:")
    print(json.dumps(result, indent=2))
    
    # Przykład workflow
    fasttrack_workflow_example()