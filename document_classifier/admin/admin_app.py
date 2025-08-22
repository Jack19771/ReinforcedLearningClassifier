# admin/admin_app.py
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import sys
import os
from fastapi import UploadFile, File
from fastapi.responses import Response
import csv
import io
from typing import List

# Dodaj ścieżkę do core
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.document_service import DocumentService

app = FastAPI(title="Document Classifier Admin")

# Templates
templates = Jinja2Templates(directory="admin/templates")

# Global service
service = DocumentService()

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    """Dashboard główny"""
    
    # Pobierz statystyki
    categories = service.db.get_categories()
    documents = service.db.get_all_documents()
    
    stats = {
        'total_documents': len(documents),
        'total_areas': len(set(cat[0] for cat in categories)),
        'mode': service.get_mode(),
        'can_predict': service.classifier.can_predict()
    }
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "stats": stats,
        "documents": documents[:10],  # Tylko 10 ostatnich
        "categories": categories
    })


@app.post("/api/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    """Upload CSV file with documents for training"""
    
    # Validate file type
    if not file.filename.lower().endswith('.csv'):
        return {
            "success": False,
            "message": "Please upload a CSV file",
            "total_rows": 0,
            "imported_rows": 0,
            "errors": ["Invalid file type. Only CSV files are allowed."],
            "preview": []
        }
    
    # Validate file size (10MB limit)
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        return {
            "success": False,
            "message": "File too large. Maximum size is 10MB.",
            "total_rows": 0,
            "imported_rows": 0,
            "errors": ["File size exceeds 10MB limit"],
            "preview": []
        }
    
    try:
        # Decode content
        csv_content = content.decode('utf-8-sig')  # Handle BOM
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        
        # Convert to list to get total count
        rows = []
        for row in csv_reader:
            rows.append(row)
        
        total_rows = len(rows)
        imported_rows = 0
        errors = []
        preview = []
        
        if total_rows == 0:
            return {
                "success": False,
                "message": "CSV file is empty or has no data rows",
                "total_rows": 0,
                "imported_rows": 0,
                "errors": ["No data rows found in CSV file"],
                "preview": []
            }
        
        # Validate CSV structure
        if not rows:
            return {
                "success": False,
                "message": "Could not read CSV data",
                "total_rows": 0,
                "imported_rows": 0,
                "errors": ["Failed to parse CSV file"],
                "preview": []
            }
        
        # Check required columns
        first_row_keys = [key.strip().lower() for key in rows[0].keys()]
        required_columns = ['text', 'area']
        
        missing_columns = []
        for col in required_columns:
            if col not in first_row_keys:
                missing_columns.append(col)
        
        if missing_columns:
            available_columns = ", ".join(first_row_keys)
            return {
                "success": False,
                "message": f"Missing required columns: {', '.join(missing_columns)}",
                "total_rows": total_rows,
                "imported_rows": 0,
                "errors": [
                    f"Required columns: {', '.join(required_columns)}",
                    f"Available columns: {available_columns}",
                    "Column names are case-insensitive"
                ],
                "preview": []
            }
        
        # Create column mapping (case-insensitive)
        column_mapping = {}
        original_keys = list(rows[0].keys())
        for original_key in original_keys:
            clean_key = original_key.strip().lower()
            if clean_key in ['text', 'area', 'subarea']:
                column_mapping[clean_key] = original_key
        
        # Process each row
        for i, row in enumerate(rows):
            try:
                # Extract data using column mapping
                text = row.get(column_mapping.get('text', ''), '').strip()
                area = row.get(column_mapping.get('area', ''), '').strip()
                subarea = row.get(column_mapping.get('subarea', ''), '').strip() or None
                
                # Validate row data
                if not text:
                    errors.append(f"Row {i+2}: Missing or empty 'text' field")
                    continue
                
                if not area:
                    errors.append(f"Row {i+2}: Missing or empty 'area' field")
                    continue
                
                if len(text) < 5:
                    errors.append(f"Row {i+2}: Text too short (minimum 5 characters)")
                    continue
                
                if len(text) > 10000:
                    errors.append(f"Row {i+2}: Text too long (maximum 10,000 characters)")
                    continue
                
                # Save to database
                service.db.save_document(text, area, subarea)
                imported_rows += 1
                
                # Add to preview (first 5 successful rows)
                if len(preview) < 5:
                    preview.append({
                        "row": i+2,  # +2 because CSV row numbers start from 2 (after header)
                        "text": text[:100] + "..." if len(text) > 100 else text,
                        "area": area,
                        "subarea": subarea
                    })
                
            except Exception as e:
                errors.append(f"Row {i+2}: Error processing - {str(e)}")
        
        # Determine success
        success = imported_rows > 0
        
        if success:
            success_rate = round((imported_rows / total_rows) * 100, 1)
            message = f"Successfully imported {imported_rows} of {total_rows} documents ({success_rate}%)"
        else:
            message = "No documents were imported due to validation errors"
        
        return {
            "success": success,
            "message": message,
            "total_rows": total_rows,
            "imported_rows": imported_rows,
            "errors": errors,
            "preview": preview
        }
        
    except UnicodeDecodeError:
        return {
            "success": False,
            "message": "Could not read CSV file. Please ensure it's saved in UTF-8 encoding.",
            "total_rows": 0,
            "imported_rows": 0,
            "errors": ["File encoding error. Save CSV as UTF-8."],
            "preview": []
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error processing CSV file: {str(e)}",
            "total_rows": 0,
            "imported_rows": 0,
            "errors": [str(e)],
            "preview": []
        }




# API endpoints dla AJAX
@app.post("/api/load-starter-data")
def load_starter_data_endpoint():
    """Załaduj przykładowe dane"""
    from core.starter_data import load_starter_data
    
    load_starter_data(service.db, service.classifier)
    service.set_mode("auto")
    
    return {"success": True, "message": "Starter data loaded successfully"}

@app.post("/api/mode/{new_mode}")
def change_mode_endpoint(new_mode: str):
    """Zmień tryb pracy"""
    
    if new_mode not in ["learning", "auto"]:
        return {"success": False, "message": "Invalid mode"}
    
    if new_mode == "auto" and not service.classifier.can_predict():
        return {"success": False, "message": "Cannot switch to auto mode - model not ready"}
    
    service.set_mode(new_mode)
    return {"success": True, "message": f"Mode changed to {new_mode}"}

from collections import Counter
from datetime import datetime, timedelta
import sqlite3

@app.get("/api/real-stats")
def get_real_stats():
    """Pobierz prawdziwe statystyki z bazy"""
    
    # Podstawowe dane
    categories = service.db.get_categories()
    documents = service.db.get_all_documents()
    
    # Grupowanie po Areas
    area_counts = Counter()
    for cat in categories:
        area_counts[cat[0]] += 1
    
    # Dokumenty w czasie (ostatnie 7 dni)
    timeline_data = []
    for i in range(7):
        date = datetime.now() - timedelta(days=6-i)
        date_str = date.strftime('%Y-%m-%d')
        
        # Policz dokumenty z tego dnia
        count = 0
        for doc in documents:
            if doc[4].startswith(date_str):
                count += 1
        
        timeline_data.append({
            'date': date.strftime('%a'),
            'count': count
        })
    
    # Dokładne percentages kategorii
    total_docs = len(documents)
    category_percentages = {}
    if total_docs > 0:
        for area, count in area_counts.items():
            category_percentages[area] = round((count / total_docs) * 100, 1)
    
    # SubArea statystyki
    subarea_counts = Counter()
    for cat in categories:
        if cat[1]:  # Jeśli ma SubArea
            subarea_counts[f"{cat[0]} → {cat[1]}"] += 1
    
    return {
        "basic_stats": {
            "total_documents": total_docs,
            "total_areas": len(area_counts),
            "total_subareas": len(subarea_counts),
            "mode": service.get_mode(),
            "can_predict": service.classifier.can_predict()
        },
        "category_distribution": dict(area_counts),
        "category_percentages": category_percentages,
        "timeline_data": timeline_data,
        "subarea_stats": dict(subarea_counts),
        "recent_documents": [
            {
                "id": doc[0],
                "text": doc[1][:100] + "..." if len(doc[1]) > 100 else doc[1],
                "area": doc[2],
                "subarea": doc[3] or "",
                "created": doc[4]
            }
            for doc in documents[:10]
        ]
    }

@app.get("/api/model-performance")
def get_model_performance():
    """Prawdziwe metryki modelu (mock na razie)"""
    
    if not service.classifier.can_predict():
        return {
            "accuracy": 0,
            "precision": 0,
            "recall": 0,
            "f1_score": 0,
            "training_examples": len(service.classifier.training_texts),
            "categories_learned": len(service.classifier.categories)
        }
    
    # Na razie mock - później można dodać prawdziwe metryki
    training_count = len(service.classifier.training_texts)
    categories_count = len(service.classifier.categories)
    
    # Prosta heurystyka na podstawie ilości danych
    base_accuracy = min(50 + (training_count * 2), 95)
    
    return {
        "accuracy": round(base_accuracy, 1),
        "precision": round(base_accuracy * 0.95, 1),
        "recall": round(base_accuracy * 0.92, 1),
        "f1_score": round(base_accuracy * 0.93, 1),
        "training_examples": training_count,
        "categories_learned": categories_count
    }

@app.get("/api/csv-template")
async def download_csv_template():
    """Download CSV template for import"""
    
    csv_content = """text,area,subarea
"Invoice from ABC Company for office supplies totaling $1,247.89",Finanse,Faktury
"Meeting notes from quarterly planning session with department heads",Sluzbowe,Spotkania
"Grocery shopping list: milk bread eggs cheese and vegetables",Prywatne,Zakupy
"Daily standup completed user authentication module working on database",Daily Business,Standup
"Performance review feedback and goals for next evaluation period",Sluzbowe,HR
"Receipt for business lunch with client at downtown restaurant $87.50",Finanse,Wydatki
"Reminder to pick up dry cleaning on Saturday and call dentist",Prywatne,Zadania
"Code review comments addressed deploying hotfix this afternoon",Daily Business,Development
"Team building event scheduled for next Friday at conference center",Sluzbowe,Wydarzenia
"Bank statement shows monthly subscription charges for various services",Finanse,Wyciagi"""
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=document_classifier_template.csv"}
    )


@app.post("/api/train-model")
async def train_model():
    """Trigger model training after CSV import"""
    
    try:
        # Get all documents from database
        documents = service.db.get_all_documents()
        
        if len(documents) < 2:
            return {
                "success": False,
                "message": "Need at least 2 documents to train model"
            }
        
        # Count documents per category
        area_counts = {}
        for doc in documents:
            area = doc[2]  # area is at index 2
            area_counts[area] = area_counts.get(area, 0) + 1
        
        # Check if we have at least 2 categories
        if len(area_counts) < 2:
            return {
                "success": False,
                "message": f"Need at least 2 different categories to train. Found: {list(area_counts.keys())}"
            }
        
        # Reset classifier and retrain
        from core.classifier import ClassificationEngine
        service.classifier = ClassificationEngine()
        
        # Train on all documents
        trained_count = 0
        for doc in documents:
            text = doc[1]   # text at index 1
            area = doc[2]   # area at index 2
            service.classifier.learn(text, area)
            trained_count += 1
        
        # Switch to auto mode if model can predict
        if service.classifier.can_predict():
            service.set_mode("auto")
        
        return {
            "success": True,
            "message": f"Model trained successfully on {trained_count} documents",
            "trained_documents": trained_count,
            "categories": list(service.classifier.categories),
            "categories_count": len(service.classifier.categories),
            "can_predict": service.classifier.can_predict(),
            "mode": service.get_mode(),
            "category_distribution": area_counts
        }
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Training error: {error_details}")  # Log to console
        
        return {
            "success": False,
            "message": f"Training failed: {str(e)}",
            "error_details": str(e)
        }



if __name__ == "__main__":
    import uvicorn
    os.chdir(os.path.dirname(os.path.dirname(__file__)))  # Zmień working directory
    uvicorn.run(app, host="0.0.0.0", port=8001)