# core/classifier.py  
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import pickle
import os

class ClassificationEngine:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.model = MultinomialNB()
        self.is_trained = False
        self.categories = set()
        self.training_texts = []
        self.training_labels = []
    
    def can_predict(self):
        """Sprawdza czy model może już klasyfikować"""
        return self.is_trained and len(self.categories) >= 2

    def learn(self, text, area):
        """Douczanie modelu na nowym przykładzie"""
        self.categories.add(area)
        self.training_texts.append(text)
        self.training_labels.append(area)
        
        # Jeśli mamy przynajmniej 2 kategorie, trenuj model
        if len(self.categories) >= 2:
            self._retrain_model()
            self.is_trained = True
            return True
        
        return False
    
    def _retrain_model(self):
        """Przetrenuj model na wszystkich przykładach"""
        if len(self.training_texts) >= 2:
            X = self.vectorizer.fit_transform(self.training_texts)
            self.model.fit(X, self.training_labels)
    
    def predict(self, text):
        """Klasyfikuj tekst"""
        if not self.can_predict():
            return None
        
        X = self.vectorizer.transform([text])
        prediction = self.model.predict(X)[0]
        
        # Dodaj confidence score
        probabilities = self.model.predict_proba(X)[0]
        max_prob = max(probabilities)
        
        return {
            'area': prediction,
            'confidence': max_prob
        }