# integration_examples/outlook_example.py
"""
Outlook/Email Integration Example
Automatyczne tagowanie emaili
"""

import requests
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailClassifier:
    """Klasyfikator emaili"""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.system_id = "outlook"
    
    def classify_email(self, subject: str, body: str, sender: str = None):
        """Klasyfikuj email na podstawie tematu i treści"""
        
        # Połącz temat i treść
        full_text = f"Subject: {subject}\n\n{body}"
        
        response = requests.post(f"{self.api_url}/v1/classify", json={
            "text": full_text,
            "system_id": self.system_id,
            "context": {
                "email_sender": sender,
                "has_subject": bool(subject),
                "content_length": len(body)
            }
        })
        
        if response.status_code == 200:
            result = response.json()
            return {
                "category": result['area'],
                "subcategory": result.get('subarea'),
                "confidence": result['confidence'],
                "outlook_folder": self.map_to_outlook_folder(result['area']),
                "tags": self.generate_outlook_tags(result)
            }
        else:
            return {"error": response.text}
    
    def map_to_outlook_folder(self, area: str) -> str:
        """Mapuj kategorię na folder Outlook"""
        
        folder_mapping = {
            "Finanse": "Invoices & Bills",
            "Sluzbowe": "Work & HR", 
            "Daily Business": "Projects",
            "Prywatne": "Personal"
        }
        
        return folder_mapping.get(area, "Uncategorized")
    
    def generate_outlook_tags(self, classification_result: dict) -> list:
        """Generuj tagi dla Outlook"""
        
        tags = [classification_result['area']]
        
        if classification_result.get('subarea'):
            tags.append(classification_result['subarea'])
        
        # Dodaj tag na podstawie confidence
        if classification_result['confidence'] > 0.9:
            tags.append("Auto-Classified")
        elif classification_result['confidence'] < 0.7:
            tags.append("Needs-Review")
        
        return tags

# Przykład Outlook Add-in JavaScript
outlook_addin_js = """
// Outlook Add-in JavaScript example
Office.onReady((info) => {
    if (info.host === Office.HostType.Outlook) {
        console.log("Document Classifier Add-in loaded");
    }
});

// Classify current email
function classifyCurrentEmail() {
    Office.context.mailbox.item.body.getAsync(
        Office.CoercionType.Text,
        function(result) {
            if (result.status === Office.AsyncResultStatus.Succeeded) {
                const body = result.value;
                const subject = Office.context.mailbox.item.subject;
                
                // Call Document Classifier API
                fetch('http://localhost:8000/v1/classify', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        text: `Subject: ${subject}\\n\\n${body}`,
                        system_id: 'outlook',
                        context: {
                            source: 'outlook_addin'
                        }
                    })
                })
                .then(response => response.json())
                .then(data => {
                    // Apply classification
                    applyClassificationToEmail(data);
                })
                .catch(error => {
                    console.error('Classification error:', error);
                });
            }
        }
    );
}

function applyClassificationToEmail(classification) {
    // Add category to email
    const category = {
        displayName: classification.area,
        color: getColorForCategory(classification.area)
    };
    
    Office.context.mailbox.item.categories.addAsync([category]);
    
    // Show result to user
    Office.context.ui.displayDialogAsync(
        `Email classified as: ${classification.area} (${Math.round(classification.confidence * 100)}% confidence)`
    );
}
"""

if __name__ == "__main__":
    # Test email classification
    classifier = EmailClassifier()
    
    # Przykład emaila
    test_email = {
        "subject": "Invoice INV-2024-001 Payment Due",
        "body": "Dear Sir/Madam, Please find attached invoice INV-2024-001 for the amount of $1,500. Payment is due within 30 days.",
        "sender": "billing@supplier.com"
    }
    
    result = classifier.classify_email(**test_email)
    print("Email classification:")
    print(json.dumps(result, indent=2))