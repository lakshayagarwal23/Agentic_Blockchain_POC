import spacy
import re
from nltk.sentiment import SentimentIntensityAnalyzer
from typing import Dict, List, Optional

class NLPAgent:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        
        # Asset type patterns
        self.asset_patterns = {
            'real_estate': ['house', 'apartment', 'property', 'building', 'land', 'condo'],
            'vehicle': ['car', 'truck', 'motorcycle', 'boat', 'plane', 'vehicle', 'auto'],
            'artwork': ['painting', 'sculpture', 'art', 'artwork', 'masterpiece'],
            'equipment': ['machinery', 'equipment', 'tool', 'device', 'machine'],
            'commodity': ['gold', 'silver', 'oil', 'wheat', 'commodity', 'metal']
        }
        
        # Value patterns
        self.value_patterns = [
            r'\$([0-9,]+(?:\.[0-9]{2})?)',
            r'([0-9,]+(?:\.[0-9]{2})?) dollars?',
            r'worth ([0-9,]+)',
            r'valued at ([0-9,]+)'
        ]
        
        # Location patterns
        self.location_patterns = [
            r'in ([A-Z][a-z]+(?: [A-Z][a-z]+)*)',
            r'located in ([A-Z][a-z]+(?: [A-Z][a-z]+)*)',
            r'at ([A-Z][a-z]+(?: [A-Z][a-z]+)*)'
        ]

    def parse_user_input(self, text: str) -> Dict:
        """Parse user input and extract asset information"""
        doc = self.nlp(text.lower())
        
        result = {
            'asset_type': self._extract_asset_type(text),
            'description': self._clean_description(text),
            'estimated_value': self._extract_value(text),
            'location': self._extract_location(text),
            'sentiment': self._analyze_sentiment(text),
            'entities': self._extract_entities(doc),
            'confidence_score': 0.0
        }
        
        # Calculate confidence score
        result['confidence_score'] = self._calculate_confidence(result)
        
        return result

    def _extract_asset_type(self, text: str) -> Optional[str]:
        """Extract asset type from text"""
        text_lower = text.lower()
        for asset_type, keywords in self.asset_patterns.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return asset_type
        return 'unknown'

    def _extract_value(self, text: str) -> Optional[float]:
        """Extract monetary value from text"""
        for pattern in self.value_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value_str = match.group(1).replace(',', '')
                try:
                    return float(value_str)
                except ValueError:
                    continue
        return None

    def _extract_location(self, text: str) -> Optional[str]:
        """Extract location from text"""
        for pattern in self.location_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return None

    def _clean_description(self, text: str) -> str:
        """Clean and format description"""
        # Remove extra whitespace and normalize
        description = ' '.join(text.split())
        return description[:500]  # Limit length

    def _analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of the text"""
        scores = self.sentiment_analyzer.polarity_scores(text)
        return {
            'compound': scores['compound'],
            'positive': scores['pos'],
            'negative': scores['neg'],
            'neutral': scores['neu']
        }

    def _extract_entities(self, doc) -> List[Dict]:
        """Extract named entities"""
        entities = []
        for ent in doc.ents:
            entities.append({
                'text': ent.text,
                'label': ent.label_,
                'description': spacy.explain(ent.label_)
            })
        return entities

    def _calculate_confidence(self, result: Dict) -> float:
        """Calculate confidence score for parsing results"""
        score = 0.0
        
        # Asset type confidence
        if result['asset_type'] != 'unknown':
            score += 0.3
            
        # Value confidence
        if result['estimated_value'] is not None:
            score += 0.3
            
        # Location confidence
        if result['location'] is not None:
            score += 0.2
            
        # Sentiment confidence (neutral to positive is good)
        if result['sentiment']['compound'] >= 0:
            score += 0.1
            
        # Entity confidence
        if len(result['entities']) > 0:
            score += 0.1
            
        return min(score, 1.0)

    def generate_follow_up_questions(self, parsed_data: Dict) -> List[str]:
        """Generate follow-up questions based on missing information"""
        questions = []
        
        if parsed_data['asset_type'] == 'unknown':
            questions.append("What type of asset are you looking to tokenize? (real estate, vehicle, artwork, etc.)")
            
        if parsed_data['estimated_value'] is None:
            questions.append("What is the estimated value of your asset?")
            
        if parsed_data['location'] is None:
            questions.append("Where is the asset located?")
            
        if parsed_data['confidence_score'] < 0.7:
            questions.append("Could you provide more details about your asset to help us better understand it?")
            
        # Asset-specific questions
        if parsed_data['asset_type'] == 'real_estate':
            questions.append("Do you have property deeds and ownership documents?")
        elif parsed_data['asset_type'] == 'vehicle':
            questions.append("Do you have the vehicle title and registration?")
        elif parsed_data['asset_type'] == 'artwork':
            questions.append("Do you have authenticity certificates or appraisals?")
            
        return questions[:3]  # Limit to 3 questions