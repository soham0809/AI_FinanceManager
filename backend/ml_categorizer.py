"""
Machine Learning-based Transaction Categorizer
Uses scikit-learn for intelligent expense categorization
"""

import pickle
import os
import re
from typing import List, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import pandas as pd
import numpy as np

class MLCategorizer:
    def __init__(self):
        self.model = None
        self.categories = [
            'Food & Dining',
            'Shopping',
            'Transportation',
            'Entertainment',
            'Healthcare',
            'Education',
            'Utilities',
            'Fuel',
            'Financial',
            'Others'
        ]
        self.model_path = 'categorizer_model.pkl'
        self._load_or_train_model()
    
    def _get_training_data(self) -> Tuple[List[str], List[str]]:
        """Generate comprehensive training data for Indian context"""
        training_data = [
            # Food & Dining
            ('SWIGGY BANGALORE', 'Food & Dining'),
            ('ZOMATO MUMBAI', 'Food & Dining'),
            ('DOMINOS PIZZA', 'Food & Dining'),
            ('MCDONALDS INDIA', 'Food & Dining'),
            ('KFC RESTAURANT', 'Food & Dining'),
            ('PIZZA HUT', 'Food & Dining'),
            ('SUBWAY SANDWICHES', 'Food & Dining'),
            ('CAFE COFFEE DAY', 'Food & Dining'),
            ('STARBUCKS COFFEE', 'Food & Dining'),
            ('HALDIRAMS', 'Food & Dining'),
            ('BARBEQUE NATION', 'Food & Dining'),
            ('FOOD COURT', 'Food & Dining'),
            ('RESTAURANT BILL', 'Food & Dining'),
            ('FOOD DELIVERY', 'Food & Dining'),
            ('GROCERY STORE', 'Food & Dining'),
            ('SUPERMARKET', 'Food & Dining'),
            
            # Shopping
            ('AMAZON PAY INDIA', 'Shopping'),
            ('FLIPKART SELLER', 'Shopping'),
            ('MYNTRA FASHION', 'Shopping'),
            ('AJIO RETAIL', 'Shopping'),
            ('NYKAA BEAUTY', 'Shopping'),
            ('BIG BAZAAR', 'Shopping'),
            ('RELIANCE RETAIL', 'Shopping'),
            ('SHOPPERS STOP', 'Shopping'),
            ('LIFESTYLE STORES', 'Shopping'),
            ('WESTSIDE STORE', 'Shopping'),
            ('PANTALOONS', 'Shopping'),
            ('BRAND FACTORY', 'Shopping'),
            ('MALL PURCHASE', 'Shopping'),
            ('ONLINE SHOPPING', 'Shopping'),
            ('RETAIL STORE', 'Shopping'),
            ('CLOTHING STORE', 'Shopping'),
            
            # Transportation
            ('UBER TRIP', 'Transportation'),
            ('OLA CABS', 'Transportation'),
            ('RAPIDO BIKE', 'Transportation'),
            ('AUTO RICKSHAW', 'Transportation'),
            ('METRO CARD', 'Transportation'),
            ('BUS TICKET', 'Transportation'),
            ('TRAIN TICKET', 'Transportation'),
            ('IRCTC BOOKING', 'Transportation'),
            ('REDBUS TRAVEL', 'Transportation'),
            ('MAKEMYTRIP', 'Transportation'),
            ('GOIBIBO FLIGHT', 'Transportation'),
            ('TAXI FARE', 'Transportation'),
            ('PARKING FEE', 'Transportation'),
            ('TOLL CHARGES', 'Transportation'),
            ('TRAVEL BOOKING', 'Transportation'),
            
            # Entertainment
            ('NETFLIX INDIA', 'Entertainment'),
            ('AMAZON PRIME', 'Entertainment'),
            ('HOTSTAR DISNEY', 'Entertainment'),
            ('SPOTIFY MUSIC', 'Entertainment'),
            ('YOUTUBE PREMIUM', 'Entertainment'),
            ('BOOKMYSHOW', 'Entertainment'),
            ('PAYTM MOVIES', 'Entertainment'),
            ('CINEMA HALL', 'Entertainment'),
            ('MOVIE TICKET', 'Entertainment'),
            ('GAMING STORE', 'Entertainment'),
            ('ENTERTAINMENT PARK', 'Entertainment'),
            ('CONCERT TICKET', 'Entertainment'),
            ('SPORTS EVENT', 'Entertainment'),
            
            # Healthcare
            ('APOLLO PHARMACY', 'Healthcare'),
            ('FORTIS HOSPITAL', 'Healthcare'),
            ('MAX HEALTHCARE', 'Healthcare'),
            ('PRACTO CONSULT', 'Healthcare'),
            ('PHARMEASY', 'Healthcare'),
            ('1MG MEDICINES', 'Healthcare'),
            ('NETMEDS PHARMACY', 'Healthcare'),
            ('MEDICAL STORE', 'Healthcare'),
            ('HOSPITAL BILL', 'Healthcare'),
            ('DOCTOR FEES', 'Healthcare'),
            ('LAB TEST', 'Healthcare'),
            ('DENTAL CLINIC', 'Healthcare'),
            ('HEALTH CHECKUP', 'Healthcare'),
            
            # Education
            ('BYJUS CLASSES', 'Education'),
            ('UNACADEMY', 'Education'),
            ('VEDANTU LEARNING', 'Education'),
            ('COURSERA COURSE', 'Education'),
            ('UDEMY LEARNING', 'Education'),
            ('SCHOOL FEES', 'Education'),
            ('COLLEGE FEES', 'Education'),
            ('TUITION FEES', 'Education'),
            ('BOOK STORE', 'Education'),
            ('LIBRARY FINE', 'Education'),
            ('EXAM FEES', 'Education'),
            ('CERTIFICATION', 'Education'),
            
            # Utilities
            ('ELECTRICITY BILL', 'Utilities'),
            ('WATER BILL', 'Utilities'),
            ('GAS BILL', 'Utilities'),
            ('INTERNET BILL', 'Utilities'),
            ('MOBILE RECHARGE', 'Utilities'),
            ('AIRTEL PAYMENT', 'Utilities'),
            ('JIO RECHARGE', 'Utilities'),
            ('VI VODAFONE', 'Utilities'),
            ('BSNL PAYMENT', 'Utilities'),
            ('DTH RECHARGE', 'Utilities'),
            ('BROADBAND BILL', 'Utilities'),
            ('UTILITY PAYMENT', 'Utilities'),
            
            # Fuel
            ('HP PETROL PUMP', 'Fuel'),
            ('INDIAN OIL', 'Fuel'),
            ('BPCL PUMP', 'Fuel'),
            ('SHELL PETROL', 'Fuel'),
            ('RELIANCE PETROL', 'Fuel'),
            ('PETROL PUMP', 'Fuel'),
            ('DIESEL FUEL', 'Fuel'),
            ('GAS STATION', 'Fuel'),
            ('FUEL PAYMENT', 'Fuel'),
            
            # Financial
            ('SBI BANK', 'Financial'),
            ('HDFC BANK', 'Financial'),
            ('ICICI BANK', 'Financial'),
            ('AXIS BANK', 'Financial'),
            ('KOTAK BANK', 'Financial'),
            ('PAYTM WALLET', 'Financial'),
            ('PHONEPE UPI', 'Financial'),
            ('GPAY PAYMENT', 'Financial'),
            ('BANK TRANSFER', 'Financial'),
            ('LOAN EMI', 'Financial'),
            ('CREDIT CARD', 'Financial'),
            ('INVESTMENT', 'Financial'),
            ('MUTUAL FUND', 'Financial'),
            ('INSURANCE', 'Financial'),
            
            # Others
            ('UNKNOWN MERCHANT', 'Others'),
            ('CASH WITHDRAWAL', 'Others'),
            ('ATM CHARGES', 'Others'),
            ('SERVICE CHARGES', 'Others'),
            ('MISCELLANEOUS', 'Others'),
        ]
        
        vendors, categories = zip(*training_data)
        return list(vendors), list(categories)
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess vendor text for better feature extraction"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove common suffixes
        text = re.sub(r'\s+(?:via|using|on|for|at|with|by)\s+.*$', '', text)
        text = re.sub(r'\s+upi.*$', '', text)
        text = re.sub(r'\s+\d{2}-\w{3}-\d{2}.*$', '', text)
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _train_model(self) -> Pipeline:
        """Train the ML categorization model"""
        vendors, categories = self._get_training_data()
        
        # Preprocess vendor names
        processed_vendors = [self._preprocess_text(vendor) for vendor in vendors]
        
        # Create pipeline with TF-IDF and Naive Bayes
        model = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, 2),
                stop_words='english',
                lowercase=True
            )),
            ('classifier', MultinomialNB(alpha=0.1))
        ])
        
        # Split data for validation
        X_train, X_test, y_train, y_test = train_test_split(
            processed_vendors, categories, test_size=0.2, random_state=42, stratify=categories
        )
        
        # Train the model
        model.fit(X_train, y_train)
        
        # Evaluate model
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"Model trained with accuracy: {accuracy:.2f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
        return model
    
    def _save_model(self, model: Pipeline):
        """Save the trained model to disk"""
        try:
            with open(self.model_path, 'wb') as f:
                pickle.dump(model, f)
            print(f"Model saved to {self.model_path}")
        except Exception as e:
            print(f"Failed to save model: {e}")
    
    def _load_model(self) -> Optional[Pipeline]:
        """Load the trained model from disk"""
        try:
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    model = pickle.load(f)
                print(f"Model loaded from {self.model_path}")
                return model
        except Exception as e:
            print(f"Failed to load model: {e}")
        return None
    
    def _load_or_train_model(self):
        """Load existing model or train a new one"""
        self.model = self._load_model()
        
        if self.model is None:
            print("Training new categorization model...")
            self.model = self._train_model()
            self._save_model(self.model)
    
    def predict_category(self, vendor: str) -> Tuple[str, float]:
        """Predict category for a vendor with confidence score"""
        if self.model is None:
            return 'Others', 0.0
        
        try:
            processed_vendor = self._preprocess_text(vendor)
            
            # Get prediction and probabilities
            prediction = self.model.predict([processed_vendor])[0]
            probabilities = self.model.predict_proba([processed_vendor])[0]
            
            # Get confidence score (max probability)
            confidence = max(probabilities)
            
            return prediction, confidence
        except Exception as e:
            print(f"Prediction error: {e}")
            return 'Others', 0.0
    
    def get_category_probabilities(self, vendor: str) -> dict:
        """Get probabilities for all categories"""
        if self.model is None:
            return {}
        
        try:
            processed_vendor = self._preprocess_text(vendor)
            probabilities = self.model.predict_proba([processed_vendor])[0]
            
            # Get class labels
            classes = self.model.named_steps['classifier'].classes_
            
            # Create probability dictionary
            prob_dict = dict(zip(classes, probabilities))
            
            # Sort by probability
            return dict(sorted(prob_dict.items(), key=lambda x: x[1], reverse=True))
        except Exception as e:
            print(f"Error getting probabilities: {e}")
            return {}
    
    def retrain_with_feedback(self, vendor: str, correct_category: str):
        """Retrain model with user feedback (for future enhancement)"""
        # This would be implemented to continuously improve the model
        # with user corrections and feedback
        pass
    
    def get_model_info(self) -> dict:
        """Get information about the trained model"""
        if self.model is None:
            return {"status": "No model loaded"}
        
        return {
            "status": "Model loaded",
            "categories": self.categories,
            "features": self.model.named_steps['tfidf'].get_feature_names_out()[:20].tolist(),
            "model_type": "TF-IDF + Naive Bayes"
        }

# Global ML categorizer instance
ml_categorizer = MLCategorizer()
