"""
K-means RIASEC Archetype Classification System
Implements K-means clustering for student archetype classification as requested by client
"""

from typing import Dict, List, Any, Tuple
import numpy as np
import json
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import warnings
warnings.filterwarnings('ignore')

class KMeansRIASECClassifier:
    """K-means clustering for RIASEC archetype classification"""
    
    def __init__(self):
        self.kmeans_model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.n_clusters = 6  # 6 RIASEC archetypes
        self.random_state = 42
        
        # RIASEC archetype labels
        self.riasec_labels = [
            'realistic', 'investigative', 'artistic', 
            'social', 'enterprising', 'conventional'
        ]
        
        # RIASEC archetype definitions
        self.riasec_definitions = {
            'realistic': {
                'name': 'Applied Practitioner',
                'description': 'Practical, hands-on, technical problem-solving',
                'traits': ['hands-on', 'technical', 'practical', 'systematic']
            },
            'investigative': {
                'name': 'Analytical Thinker', 
                'description': 'Logical, analytical, research-oriented, problem-solving',
                'traits': ['analytical', 'logical', 'research', 'problem-solving']
            },
            'artistic': {
                'name': 'Creative Innovator',
                'description': 'Creative, innovative, design-oriented, expressive',
                'traits': ['creative', 'innovative', 'design', 'expressive']
            },
            'social': {
                'name': 'Collaborative Supporter',
                'description': 'People-oriented, helpful, communicative, team-focused',
                'traits': ['people-oriented', 'helpful', 'communicative', 'teamwork']
            },
            'enterprising': {
                'name': 'Strategic Leader',
                'description': 'Leadership, management, entrepreneurial, goal-oriented',
                'traits': ['leadership', 'management', 'entrepreneurial', 'goal-oriented']
            },
            'conventional': {
                'name': 'Methodical Organizer',
                'description': 'Organized, detail-oriented, systematic, structured',
                'traits': ['organized', 'detail-oriented', 'systematic', 'structured']
            }
        }
    
    def create_feature_vector(self, grades_data: List[Dict[str, Any]]) -> np.ndarray:
        """
        Create feature vector from grades data for K-means clustering
        
        Args:
            grades_data: List of course grades with course_code and grade fields
            
        Returns:
            Feature vector for K-means clustering
        """
        features = []
        
        if not grades_data:
            # Return zero vector if no grades
            return np.zeros(20, dtype=np.float32)
        
        # Extract grades
        grades = [g.get('grade', 0) for g in grades_data if g.get('grade', 0) > 0]
        
        if not grades:
            return np.zeros(20, dtype=np.float32)
        
        # 1. Basic Academic Performance Features (0-4)
        features.extend([
            np.mean(grades),                    # Average grade
            np.std(grades),                     # Grade consistency
            np.min(grades),                     # Best performance
            np.max(grades),                     # Worst performance
            len([g for g in grades if g <= 1.5])  # Excellent grades count
        ])
        
        # 2. Subject Category Performance (5-10)
        subject_categories = self._categorize_subjects(grades_data)
        for category in ['programming', 'mathematics', 'systems', 'design', 'management', 'general']:
            features.append(subject_categories.get(category, 0.0))
        
        # 3. Academic Progression Features (11-13)
        progression_features = self._calculate_progression_features(grades_data)
        features.extend([
            progression_features['improvement_trend'],
            progression_features['consistency_score'],
            progression_features['challenge_level']
        ])
        
        # 4. Course Difficulty Features (14-16)
        difficulty_features = self._calculate_difficulty_features(grades_data)
        features.extend([
            difficulty_features['advanced_courses_avg'],
            difficulty_features['core_courses_avg'],
            difficulty_features['elective_courses_avg']
        ])
        
        # 5. Grade Distribution Features (17-19)
        grade_distribution = self._calculate_grade_distribution(grades)
        features.extend([
            grade_distribution['excellent_ratio'],
            grade_distribution['good_ratio'],
            grade_distribution['pass_ratio']
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
        consistency_score = 1.0 / (np.std(grades) + 0.1)
        
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
    
    def _calculate_grade_distribution(self, grades: List[float]) -> Dict[str, float]:
        """Calculate grade distribution features"""
        if not grades:
            return {'excellent_ratio': 0.0, 'good_ratio': 0.0, 'pass_ratio': 0.0}
        
        total = len(grades)
        excellent = len([g for g in grades if g <= 1.5])
        good = len([g for g in grades if g <= 2.0])
        pass_grade = len([g for g in grades if g <= 3.0])
        
        return {
            'excellent_ratio': excellent / total,
            'good_ratio': good / total,
            'pass_ratio': pass_grade / total
        }
    
    def generate_synthetic_training_data(self, n_samples: int = 1000) -> np.ndarray:
        """
        Generate synthetic training data for K-means model
        
        Args:
            n_samples: Number of synthetic samples to generate
            
        Returns:
            Feature matrix for training
        """
        np.random.seed(42)
        X = []
        
        for _ in range(n_samples):
            # Generate synthetic grades data
            grades_data = self._generate_synthetic_grades()
            
            # Create feature vector
            features = self.create_feature_vector(grades_data)
            X.append(features)
        
        return np.array(X)
    
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
            if np.random.random() < 0.9:  # 90% chance of having the course
                grade = np.random.normal(2.0, 0.8)  # Mean 2.0, std 0.8
                grade = max(1.0, min(5.0, grade))  # Clamp between 1.0-5.0
                grades_data.append({
                    'course_code': course,
                    'grade': round(grade, 1),
                    'units': 3
                })
        
        return grades_data
    
    def train_model(self, X: np.ndarray = None, use_synthetic: bool = True) -> Dict[str, Any]:
        """
        Train K-means model for RIASEC classification
        
        Args:
            X: Feature matrix (optional, will generate synthetic if not provided)
            use_synthetic: Whether to use synthetic data for training
            
        Returns:
            Training results and metrics
        """
        if X is None or use_synthetic:
            print("🔄 Generating synthetic training data for K-means...")
            X = self.generate_synthetic_training_data(1000)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train K-means
        print("🎯 Training K-means model for RIASEC classification...")
        self.kmeans_model = KMeans(
            n_clusters=self.n_clusters,
            random_state=self.random_state,
            n_init=10,
            max_iter=300
        )
        
        self.kmeans_model.fit(X_scaled)
        self.is_trained = True
        
        # Evaluate model
        labels = self.kmeans_model.labels_
        silhouette_avg = silhouette_score(X_scaled, labels)
        
        print(f"✅ K-means model trained successfully!")
        print(f"📊 Silhouette Score: {silhouette_avg:.3f}")
        print(f"📊 Number of clusters: {self.n_clusters}")
        
        return {
            'silhouette_score': silhouette_avg,
            'n_clusters': self.n_clusters,
            'n_samples': len(X),
            'n_features': X.shape[1]
        }
    
    def predict_archetype(self, grades_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Predict RIASEC archetype using K-means clustering
        
        Args:
            grades_data: List of course grades
            
        Returns:
            Complete archetype analysis with scores and primary archetype
        """
        if not self.is_trained:
            print("⚠️ Model not trained. Training with synthetic data...")
            self.train_model()
        
        # Create feature vector
        features = self.create_feature_vector(grades_data)
        features_scaled = self.scaler.transform(features.reshape(1, -1))
        
        # Predict cluster
        cluster_id = self.kmeans_model.predict(features_scaled)[0]
        
        # Calculate distances to all cluster centers
        distances = self.kmeans_model.transform(features_scaled)[0]
        
        # Convert distances to probabilities (closer = higher probability)
        # Use softmax to convert distances to probabilities
        max_distance = np.max(distances)
        scores = max_distance - distances  # Invert distances
        scores = np.exp(scores - np.max(scores))  # Softmax
        scores = scores / np.sum(scores)  # Normalize
        
        # Map cluster IDs to RIASEC labels
        archetype_scores = {}
        for i, archetype in enumerate(self.riasec_labels):
            archetype_scores[archetype] = float(scores[i] * 100)
        
        # Get primary archetype
        primary_archetype = self.riasec_labels[cluster_id]
        primary_definition = self.riasec_definitions[primary_archetype]
        
        # Sort archetypes by score for ranking
        sorted_archetypes = sorted(archetype_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Generate insights
        insights = self._generate_archetype_insights(archetype_scores, grades_data)
        
        return {
            'primary_archetype': primary_archetype,
            'archetype_name': primary_definition['name'],
            'archetype_description': primary_definition['description'],
            'archetype_traits': primary_definition['traits'],
            'archetype_scores': archetype_scores,
            'archetype_ranking': sorted_archetypes,
            'insights': insights,
            'total_courses_analyzed': len(grades_data),
            'analysis_method': 'kmeans_clustering',
            'cluster_id': int(cluster_id)
        }
    
    def _generate_archetype_insights(self, archetype_scores: Dict[str, float], grades_data: List[Dict[str, Any]]) -> List[str]:
        """Generate insights based on K-means archetype analysis"""
        insights = []
        
        # Find top 3 archetypes
        top_archetypes = sorted(archetype_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Primary archetype insight
        primary = top_archetypes[0]
        primary_name = self.riasec_definitions[primary[0]]['name']
        insights.append(f"Your primary learning archetype is {primary_name} ({primary[1]:.1f}%), indicating strong {self.riasec_definitions[primary[0]]['description'].lower()} tendencies.")
        
        # Secondary archetype insight
        if len(top_archetypes) > 1 and top_archetypes[1][1] > 15:  # Only mention if significant
            secondary = top_archetypes[1]
            secondary_name = self.riasec_definitions[secondary[0]]['name']
            insights.append(f"You also show strong {secondary_name} characteristics ({secondary[1]:.1f}%), suggesting a balanced learning approach.")
        
        # Performance insight
        total_courses = len(grades_data)
        if total_courses > 0:
            avg_grade = sum(course.get('grade', 0) for course in grades_data) / total_courses
            if avg_grade <= 2.0:
                insights.append("Your strong academic performance across diverse subjects demonstrates excellent learning adaptability.")
            elif avg_grade <= 3.0:
                insights.append("Your consistent academic performance shows good learning potential with room for growth in specific areas.")
            else:
                insights.append("Focus on improving performance in core subjects to better align with your learning archetype.")
        
        return insights

# Helper function for easy integration
def predict_archetype_kmeans_riasec(grades_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Predict RIASEC archetype using K-means clustering (as requested by client)
    
    Args:
        grades_data: List of course grades with course_code and grade fields
        
    Returns:
        Complete archetype analysis
    """
    classifier = KMeansRIASECClassifier()
    
    # Try to load existing model, otherwise train new one
    # For now, we'll train a new model each time
    # In production, you might want to save/load the trained model
    classifier.train_model()
    
    return classifier.predict_archetype(grades_data)
