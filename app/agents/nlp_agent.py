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
            'real_estate': ['house', 'apartment', 'property', 'building', 'land', 'condo', 'flat', 'villa', 'sqft', 'bedroom', 'bathroom'],
            'vehicle': ['car', 'truck', 'motorcycle', 'boat', 'plane', 'vehicle', 'mileage', 'sedan', 'suv', 'year', 'model'],
            'artwork': ['painting', 'sculpture', 'art', 'artwork', 'canvas', 'oil painting', 'artist', 'frame'],
            'equipment': ['machinery', 'equipment', 'tool', 'device', 'machine', 'serial number', 'operating hours'],
            'commodity': ['gold', 'silver', 'oil', 'wheat', 'commodity', 'metal', 'oz', 'purity']
        }

        # Value patterns
        self.value_patterns = [
            r'\$([0-9,]+(?:\.[0-9]{2})?)',
            r'([0-9,]+(?:\.[0-9]{2})?) dollars?',
            r'worth ([0-9,]+)',
            r'valued at ([0-9,]+)',
            r'inr[\s₹]*([\d,]+)',
            r'(\d+(?:\.\d+)?)\s*(crore|crores|cr)',
            r'(\d+(?:\.\d+)?)\s*(lakh|lac|lacs)'
        ]

        # Location patterns
        self.location_patterns = [
            r'in ([A-Z][a-z]+(?: [A-Z][a-z]+)*)',
            r'located in ([A-Z][a-z]+(?: [A-Z][a-z]+)*)',
            r'at ([A-Z][a-z]+(?: [A-Z][a-z]+)*)'
        ]

    def parse_user_input(self, text: str) -> Dict:
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

        result['confidence_score'] = self._calculate_confidence(result)

        return result

    def _extract_asset_type(self, text: str) -> Optional[str]:
        text_lower = text.lower()
        for asset_type, keywords in self.asset_patterns.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return asset_type
        return 'unknown'

    def _extract_value(self, text: str) -> Optional[float]:
        text = text.lower()

        for pattern in self.value_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value_str = match.group(1).replace(',', '')
                try:
                    value = float(value_str)
                    # Apply crore / lakh scaling
                    if len(match.groups()) >= 2:
                        unit = match.group(2)
                        if unit in ['crore', 'crores', 'cr']:
                            value *= 1e7
                        elif unit in ['lakh', 'lac', 'lacs']:
                            value *= 1e5
                    return value
                except ValueError:
                    continue

        return None

    def _extract_location(self, text: str) -> Optional[str]:
        for pattern in self.location_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return None

    def _clean_description(self, text: str) -> str:
        return ' '.join(text.split())[:500]

    def _analyze_sentiment(self, text: str) -> Dict:
        scores = self.sentiment_analyzer.polarity_scores(text)
        return {
            'compound': scores['compound'],
            'positive': scores['pos'],
            'negative': scores['neg'],
            'neutral': scores['neu']
        }

    def _extract_entities(self, doc) -> List[Dict]:
        return [
            {
                'text': ent.text,
                'label': ent.label_,
                'description': spacy.explain(ent.label_)
            }
            for ent in doc.ents
        ]

    def _calculate_confidence(self, result: Dict) -> float:
        score = 0.0

        if result['asset_type'] != 'unknown':
            score += 0.25

        if result['estimated_value'] is not None:
            score += 0.25

        if result['location'] is not None:
            score += 0.25

        if result['sentiment']['compound'] >= 0:
            score += 0.25

        return round(min(score, 1.0), 2)

    def generate_follow_up_questions(self, parsed_data: Dict) -> List[str]:
        questions = []

        if parsed_data['asset_type'] == 'unknown':
            questions.append("What type of asset are you looking to tokenize?")

        if parsed_data['estimated_value'] is None:
            questions.append("What is the estimated value of your asset?")

        if parsed_data['location'] is None:
            questions.append("Where is the asset located?")

        if parsed_data['confidence_score'] < 0.7:
            questions.append("Could you provide more details about your asset?")

        if parsed_data['asset_type'] == 'real_estate':
            questions.append("Please provide size (sqft), bedrooms, year built.")

        if parsed_data['asset_type'] == 'vehicle':
            questions.append("Please provide year, model, mileage of the vehicle.")

        if parsed_data['asset_type'] == 'artwork':
            questions.append("Please provide artist name, dimensions, and medium.")

        return questions[:3]
