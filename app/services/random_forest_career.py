"""
Random Forest Career Path Forecasting System for Objective 1
Implements Random Forest algorithm for predicting career success scores
"""

from typing import Dict, List, Any, Tuple, Optional
import numpy as np
import json
import pickle
import os
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class RandomForestCareerPredictor:
    """Random Forest model for career path forecasting"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.career_labels = [
            "data_science", "systems_engineering", "software_engineering", 
            "ui_ux", "product_management", "cybersecurity", "cloud_engineering",
            "devops", "business_analyst", "project_manager"
        ]
        self.is_trained = False
        
        # Model hyperparameters
        self.n_estimators = 100
        self.max_depth = 10
        self.min_samples_split = 5
        self.min_samples_leaf = 2
        self.random_state = 42
        
    def create_feature_vector(self, grades_data: List[Dict[str, Any]], 
                            archetype_scores: Dict[str, float]) -> np.ndarray:
        """
        Create feature vector from student data for Random Forest
        
        Args:
            grades_data: List of course grades
            archetype_scores: RIASEC archetype percentages
            
        Returns:
            Feature vector for Random Forest
        """
        features = []
        
        # 1. Academic Performance Features (0-7)
        if grades_data:
            grades = [g.get('grade', 0) for g in grades_data if g.get('grade', 0) > 0]
            if grades:
                features.extend([
                    np.mean(grades),  # Average grade
                    np.std(grades),   # Grade consistency
                    np.min(grades),   # Best performance
                    np.max(grades),   # Worst performance
                    len([g for g in grades if g <= 1.5]),  # Excellent grades count
                    len([g for g in grades if g <= 2.0]),  # Good grades count
                    len(grades)  # Total subjects
                ])
            else:
                features.extend([0] * 7)
        else:
            features.extend([0] * 7)
        
        # 2. RIASEC Archetype Features (8-13)
        riasec_order = ['realistic', 'investigative', 'artistic', 'social', 'enterprising', 'conventional']
        for archetype in riasec_order:
            features.append(archetype_scores.get(archetype, 0.0))
        
        # 3. Subject Category Performance (14-19)
        subject_categories = self._categorize_subjects(grades_data)
        for category in ['programming', 'mathematics', 'systems', 'design', 'management', 'general']:
            features.append(subject_categories.get(category, 0.0))
        
        # 4. Academic Progression Features (20-22)
        progression_features = self._calculate_progression_features(grades_data)
        features.extend([
            progression_features['improvement_trend'],
            progression_features['consistency_score'],
            progression_features['challenge_level']
        ])
        
        # 5. Course Difficulty Features (23-25)
        difficulty_features = self._calculate_difficulty_features(grades_data)
        features.extend([
            difficulty_features['advanced_courses_avg'],
            difficulty_features['core_courses_avg'],
            difficulty_features['elective_courses_avg']
        ])
        
        return np.array(features, dtype=np.float32)
    
    def _categorize_subjects(self, grades_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Categorize subjects and calculate average performance per category"""
        categories = {
            'programming': [],
            'mathematics': [],
            'systems': [],
            'design': [],
            'management': [],
            'general': []
        }
        
        for course in grades_data:
            course_code = course.get('course_code', '').upper()
            grade = course.get('grade', 0)
            
            if grade <= 0:
                continue
                
            # Programming courses
            if any(keyword in course_code for keyword in ['ICC', 'EIT', 'CSC']) and \
               any(keyword in course_code for keyword in ['0102', '0103', '0104', '0211', '0323']):
                categories['programming'].append(grade)
            
            # Mathematics courses
            elif any(keyword in course_code for keyword in ['CET', 'MMW', 'EIT 0221']):
                categories['mathematics'].append(grade)
            
            # Systems courses
            elif any(keyword in course_code for keyword in ['EIT 0212', 'EIT 0222', 'EIT 0312', 'EIT 0321', 'EIT 0322']):
                categories['systems'].append(grade)
            
            # Design courses
            elif any(keyword in course_code for keyword in ['EIT 0121', 'EIT 0123', 'AAP']):
                categories['design'].append(grade)
            
            # Management courses
            elif any(keyword in course_code for keyword in ['CAP', 'IIP', 'NSTP', 'PCM']):
                categories['management'].append(grade)
            
            # General courses
            else:
                categories['general'].append(grade)
        
        # Calculate averages
        category_averages = {}
        for category, grades in categories.items():
            if grades:
                # Convert to performance score (lower grade = better performance)
                performance_scores = [max(0, (5.0 - grade) / 4.0) for grade in grades]
                category_averages[category] = np.mean(performance_scores)
            else:
                category_averages[category] = 0.0
        
        return category_averages
    
    def _calculate_progression_features(self, grades_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate academic progression features"""
        if not grades_data:
            return {'improvement_trend': 0.0, 'consistency_score': 0.0, 'challenge_level': 0.0}
        
        # Sort by course code to get chronological order
        sorted_grades = sorted(grades_data, key=lambda x: x.get('course_code', ''))
        grades = [g.get('grade', 0) for g in sorted_grades if g.get('grade', 0) > 0]
        
        if len(grades) < 2:
            return {'improvement_trend': 0.0, 'consistency_score': 0.0, 'challenge_level': 0.0}
        
        # Improvement trend (negative slope = improvement)
        x = np.arange(len(grades))
        slope = np.polyfit(x, grades, 1)[0]
        improvement_trend = -slope  # Negative slope = improvement
        
        # Consistency score (lower std = more consistent)
        consistency_score = 1.0 / (np.std(grades) + 0.1)  # Add small value to avoid division by zero
        
        # Challenge level (average of grades, lower = more challenging)
        challenge_level = np.mean(grades)
        
        return {
            'improvement_trend': improvement_trend,
            'consistency_score': consistency_score,
            'challenge_level': challenge_level
        }
    
    def _calculate_difficulty_features(self, grades_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate course difficulty features"""
        advanced_courses = []
        core_courses = []
        elective_courses = []
        
        for course in grades_data:
            course_code = course.get('course_code', '').upper()
            grade = course.get('grade', 0)
            
            if grade <= 0:
                continue
            
            # Advanced courses (3rd and 4th year)
            if any(keyword in course_code for keyword in ['EIT 03', 'EIT 04', 'CAP', 'IIP']):
                advanced_courses.append(grade)
            
            # Core courses (1st and 2nd year fundamentals)
            elif any(keyword in course_code for keyword in ['ICC 01', 'EIT 01', 'EIT 02', 'CET 01']):
                core_courses.append(grade)
            
            # Elective courses
            elif 'ELECTIVE' in course_code:
                elective_courses.append(grade)
        
        def calculate_avg_performance(grades_list):
            if not grades_list:
                return 0.0
            performance_scores = [max(0, (5.0 - grade) / 4.0) for grade in grades_list]
            return np.mean(performance_scores)
        
        return {
            'advanced_courses_avg': calculate_avg_performance(advanced_courses),
            'core_courses_avg': calculate_avg_performance(core_courses),
            'elective_courses_avg': calculate_avg_performance(elective_courses)
        }
    
    def generate_synthetic_training_data(self, n_samples: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate synthetic training data for Random Forest model
        
        Args:
            n_samples: Number of synthetic samples to generate
            
        Returns:
            X: Feature matrix, y: Target career scores
        """
        np.random.seed(42)
        X = []
        y = []
        
        for _ in range(n_samples):
            # Generate synthetic student data
            grades_data = self._generate_synthetic_grades()
            archetype_scores = self._generate_synthetic_archetypes()
            
            # Create feature vector
            features = self.create_feature_vector(grades_data, archetype_scores)
            X.append(features)
            
            # Generate synthetic career scores based on features
            career_scores = self._generate_synthetic_career_scores(features, archetype_scores)
            y.append(career_scores)
        
        return np.array(X), np.array(y)
    
    def _generate_synthetic_grades(self) -> List[Dict[str, Any]]:
        """Generate synthetic course grades"""
        courses = [
            'ICC 0101', 'ICC 0102', 'ICC 0103', 'ICC 0104', 'ICC 0105',
            'EIT 0121', 'EIT 0122', 'EIT 0123', 'EIT 0211', 'EIT 0212A',
            'EIT 0221', 'EIT 0222', 'EIT 0311', 'EIT 0312', 'EIT 0321',
            'EIT 0322', 'EIT 0323', 'CAP 0101', 'CAP 0102', 'IIP 0101A'
        ]
        
        grades_data = []
        for course in courses:
            # Generate realistic grade distribution
            if np.random.random() < 0.9:  # 90% chance of having the course
                grade = np.random.normal(2.0, 0.8)  # Mean 2.0, std 0.8
                grade = max(1.0, min(5.0, grade))  # Clamp between 1.0-5.0
                grades_data.append({
                    'course_code': course,
                    'grade': round(grade, 1),
                    'units': 3
                })
        
        return grades_data
    
    def _generate_synthetic_archetypes(self) -> Dict[str, float]:
        """Generate synthetic RIASEC archetype scores"""
        # Generate random archetype scores
        scores = np.random.dirichlet([1, 1, 1, 1, 1, 1]) * 100
        
        return {
            'realistic': scores[0],
            'investigative': scores[1],
            'artistic': scores[2],
            'social': scores[3],
            'enterprising': scores[4],
            'conventional': scores[5]
        }
    
    def _generate_synthetic_career_scores(self, features: np.ndarray, 
                                        archetype_scores: Dict[str, float]) -> List[float]:
        """Generate synthetic career scores based on features and archetypes"""
        # Base career scores influenced by archetypes and academic performance
        base_scores = np.random.uniform(0.3, 0.8, len(self.career_labels))
        
        # Adjust based on archetype alignment
        archetype_weights = {
            'data_science': ['investigative', 'conventional'],
            'systems_engineering': ['realistic', 'investigative'],
            'software_engineering': ['investigative', 'conventional'],
            'ui_ux': ['artistic', 'social'],
            'product_management': ['enterprising', 'social'],
            'cybersecurity': ['investigative', 'conventional'],
            'cloud_engineering': ['realistic', 'investigative'],
            'devops': ['realistic', 'conventional'],
            'business_analyst': ['investigative', 'conventional'],
            'project_manager': ['enterprising', 'social']
        }
        
        for i, career in enumerate(self.career_labels):
            if career in archetype_weights:
                for archetype in archetype_weights[career]:
                    base_scores[i] += archetype_scores.get(archetype, 0) * 0.002
        
        # Adjust based on academic performance
        avg_grade = features[0] if len(features) > 0 else 2.0
        performance_factor = max(0, (5.0 - avg_grade) / 4.0)
        base_scores *= (0.5 + performance_factor * 0.5)
        
        # Normalize to 0-1 range
        base_scores = np.clip(base_scores, 0, 1)
        
        return base_scores.tolist()
    
    def train_model(self, X: np.ndarray = None, y: np.ndarray = None, 
                   use_synthetic: bool = True) -> Dict[str, Any]:
        """
        Train Random Forest model
        
        Args:
            X: Feature matrix (optional, will generate synthetic if not provided)
            y: Target career scores (optional, will generate synthetic if not provided)
            use_synthetic: Whether to use synthetic data for training
            
        Returns:
            Training results and metrics
        """
        if X is None or y is None or use_synthetic:
            print("🔄 Generating synthetic training data...")
            X, y = self.generate_synthetic_training_data(1000)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train Random Forest
        print("🌲 Training Random Forest model...")
        self.model = RandomForestRegressor(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            min_samples_split=self.min_samples_split,
            min_samples_leaf=self.min_samples_leaf,
            random_state=self.random_state,
            n_jobs=-1
        )
        
        self.model.fit(X_train_scaled, y_train)
        self.is_trained = True
        
        # Evaluate model
        y_pred = self.model.predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # Feature importance
        feature_importance = self.model.feature_importances_
        
        print(f"✅ Model trained successfully!")
        print(f"📊 R² Score: {r2:.3f}")
        print(f"📊 MSE: {mse:.3f}")
        
        return {
            'r2_score': r2,
            'mse': mse,
            'feature_importance': feature_importance.tolist(),
            'n_samples': len(X),
            'n_features': X.shape[1]
        }
    
    def predict_career_scores(self, grades_data: List[Dict[str, Any]], 
                            archetype_scores: Dict[str, float]) -> Dict[str, float]:
        """
        Predict career scores using trained Random Forest model
        
        Args:
            grades_data: List of course grades
            archetype_scores: RIASEC archetype percentages
            
        Returns:
            Dictionary of career scores
        """
        if not self.is_trained:
            print("⚠️ Model not trained. Training with synthetic data...")
            self.train_model()
        
        # Create feature vector
        features = self.create_feature_vector(grades_data, archetype_scores)
        features_scaled = self.scaler.transform(features.reshape(1, -1))
        
        # Predict career scores
        career_scores = self.model.predict(features_scaled)[0]
        
        # Convert to dictionary
        result = {}
        for i, career in enumerate(self.career_labels):
            result[career] = float(career_scores[i])
        
        return result
    
    def save_model(self, filepath: str) -> bool:
        """Save trained model to file"""
        if not self.is_trained:
            return False
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'career_labels': self.career_labels,
            'hyperparameters': {
                'n_estimators': self.n_estimators,
                'max_depth': self.max_depth,
                'min_samples_split': self.min_samples_split,
                'min_samples_leaf': self.min_samples_leaf,
                'random_state': self.random_state
            },
            'trained_at': datetime.now().isoformat()
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        return True
    
    def load_model(self, filepath: str) -> bool:
        """Load trained model from file"""
        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_names = model_data['feature_names']
            self.career_labels = model_data['career_labels']
            self.is_trained = True
            
            return True
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False

# Helper function for easy integration
def predict_career_scores_random_forest(grades_data: List[Dict[str, Any]], 
                                     archetype_scores: Dict[str, float]) -> Dict[str, float]:
    """
    Predict career scores using Random Forest (Objective 1)
    
    Args:
        grades_data: List of course grades
        archetype_scores: RIASEC archetype percentages
        
    Returns:
        Dictionary of career scores
    """
    predictor = RandomForestCareerPredictor()
    
    # Try to load existing model, otherwise train new one
    model_path = 'models/random_forest_career.pkl'
    if not predictor.load_model(model_path):
        print("🔄 Training new Random Forest model...")
        predictor.train_model()
        
        # Save the trained model
        os.makedirs('models', exist_ok=True)
        predictor.save_model(model_path)
    
    return predictor.predict_career_scores(grades_data, archetype_scores)
