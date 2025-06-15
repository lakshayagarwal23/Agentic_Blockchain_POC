import re
from typing import Dict, List
from datetime import datetime
import json

class VerificationAgent:
    def __init__(self):
        self.verification_threshold = 0.7
        
        # Jurisdictional support
        self.supported_jurisdictions = {
            'US': {'compliance_level': 'high', 'required_docs': ['title', 'appraisal']},
            'EU': {'compliance_level': 'high', 'required_docs': ['ownership', 'certificate']},
            'UK': {'compliance_level': 'medium', 'required_docs': ['deed', 'valuation']},
            'CA': {'compliance_level': 'medium', 'required_docs': ['title', 'assessment']},
            'SG': {'compliance_level': 'high', 'required_docs': ['certificate', 'valuation']}
        }
        
        # Asset value ranges for validation
        self.value_ranges = {
            'real_estate': {'min': 10000, 'max': 50000000},
            'vehicle': {'min': 1000, 'max': 2000000},
            'artwork': {'min': 500, 'max': 100000000},
            'equipment': {'min': 100, 'max': 5000000},
            'commodity': {'min': 50, 'max': 10000000}
        }

    def verify_asset(self, asset_data: Dict) -> Dict:
        """Comprehensive asset verification"""
        verification_result = {
            'overall_score': 0.0,
            'status': 'pending',
            'breakdown': {},
            'issues': [],
            'recommendations': [],
            'next_steps': []
        }
        
        try:
            # Basic validation
            basic_score = self._verify_basic_information(asset_data)
            verification_result['breakdown']['basic_info'] = basic_score
            
            # Value assessment
            value_score = self._verify_value(asset_data)
            verification_result['breakdown']['value_assessment'] = value_score
            
            # Compliance check
            compliance_score = self._verify_compliance(asset_data)
            verification_result['breakdown']['compliance'] = compliance_score
            
            # Asset-specific verification
            specific_score = self._verify_asset_specific(asset_data)
            verification_result['breakdown']['asset_specific'] = specific_score
            
            # Calculate overall score
            scores = [basic_score, value_score, compliance_score, specific_score]
            verification_result['overall_score'] = sum(scores) / len(scores)
            
            # Determine status
            if verification_result['overall_score'] >= self.verification_threshold:
                verification_result['status'] = 'verified'
            elif verification_result['overall_score'] >= 0.5:
                verification_result['status'] = 'requires_review'
            else:
                verification_result['status'] = 'rejected'
                
            # Generate recommendations
            verification_result['recommendations'] = self._generate_recommendations(
                asset_data, verification_result
            )
            
            # Define next steps
            verification_result['next_steps'] = self._define_next_steps(
                verification_result['status'], asset_data
            )
            
        except Exception as e:
            verification_result['status'] = 'error'
            verification_result['issues'].append(f"Verification error: {str(e)}")
            
        return verification_result

    def _verify_basic_information(self, asset_data: Dict) -> float:
        """Verify basic asset information completeness"""
        score = 0.0
        required_fields = ['asset_type', 'description', 'estimated_value', 'location']
        
        for field in required_fields:
            if field in asset_data and asset_data[field]:
                if field == 'description' and len(str(asset_data[field])) >= 10:
                    score += 0.25
                elif field == 'estimated_value' and asset_data[field] > 0:
                    score += 0.25
                elif field in ['asset_type', 'location'] and len(str(asset_data[field])) >= 2:
                    score += 0.25
                    
        return min(score, 1.0)

    def _verify_value(self, asset_data: Dict) -> float:
        """Verify asset value reasonableness"""
        if 'estimated_value' not in asset_data or not asset_data['estimated_value']:
            return 0.0
            
        value = asset_data['estimated_value']
        asset_type = asset_data.get('asset_type', 'unknown')
        
        if asset_type in self.value_ranges:
            range_info = self.value_ranges[asset_type]
            if range_info['min'] <= value <= range_info['max']:
                return 1.0
            elif value < range_info['min']:
                return 0.3  # Too low
            else:
                return 0.6  # Too high, needs extra verification
        
        return 0.5  # Unknown asset type

    def _verify_compliance(self, asset_data: Dict) -> float:
        """Verify regulatory compliance requirements"""
        jurisdiction = self._extract_jurisdiction(asset_data.get('location', ''))
        
        if jurisdiction in self.supported_jurisdictions:
            return 0.9
        elif jurisdiction:
            return 0.5  # Partial support
        else:
            return 0.3  # Unknown jurisdiction

    def _verify_asset_specific(self, asset_data: Dict) -> float:
        """Asset-type specific verification"""
        asset_type = asset_data.get('asset_type', 'unknown')
        
        if asset_type == 'real_estate':
            return self._verify_real_estate(asset_data)
        elif asset_type == 'vehicle':
            return self._verify_vehicle(asset_data)
        elif asset_type == 'artwork':
            return self._verify_artwork(asset_data)
        elif asset_type == 'equipment':
            return self._verify_equipment(asset_data)
        elif asset_type == 'commodity':
            return self._verify_commodity(asset_data)
        else:
            return 0.4  # Unknown type gets lower score

    def _verify_real_estate(self, asset_data: Dict) -> float:
        """Real estate specific verification"""
        score = 0.5  # Base score
        description = asset_data.get('description', '').lower()
        
        # Look for property indicators
        property_indicators = ['sqft', 'bedroom', 'bathroom', 'acre', 'floor', 'apartment']
        for indicator in property_indicators:
            if indicator in description:
                score += 0.1
                
        return min(score, 1.0)

    def _verify_vehicle(self, asset_data: Dict) -> float:
        """Vehicle specific verification"""
        score = 0.5
        description = asset_data.get('description', '').lower()
        
        # Look for vehicle indicators
        vehicle_indicators = ['year', 'model', 'make', 'mileage', 'engine', 'transmission']
        for indicator in vehicle_indicators:
            if indicator in description:
                score += 0.1
                
        return min(score, 1.0)

    def _verify_artwork(self, asset_data: Dict) -> float:
        """Artwork specific verification"""
        score = 0.5
        description = asset_data.get('description', '').lower()
        
        # Look for art indicators
        art_indicators = ['artist', 'canvas', 'oil', 'watercolor', 'sculpture', 'signed']
        for indicator in art_indicators:
            if indicator in description:
                score += 0.1
                
        return min(score, 1.0)

    def _verify_equipment(self, asset_data: Dict) -> float:
        """Equipment specific verification"""
        score = 0.5
        description = asset_data.get('description', '').lower()
        
        # Look for equipment indicators
        equipment_indicators = ['serial', 'model', 'manufacturer', 'warranty', 'condition']
        for indicator in equipment_indicators:
            if indicator in description:
                score += 0.1
                
        return min(score, 1.0)

    def _verify_commodity(self, asset_data: Dict) -> float:
        """Commodity specific verification"""
        score = 0.5
        description = asset_data.get('description', '').lower()
        
        # Look for commodity indicators
        commodity_indicators = ['grade', 'purity', 'weight', 'certificate', 'assay', 'quality']
        for indicator in commodity_indicators:
            if indicator in description:
                score += 0.1
                
        return min(score, 1.0)

    def _extract_jurisdiction(self, location: str) -> str:
        """Extract jurisdiction from location string"""
        if not location:
            return ''
            
        location_upper = location.upper()
        
        # Simple jurisdiction mapping
        jurisdiction_mappings = {
            'US': ['USA', 'UNITED STATES', 'AMERICA', 'NEW YORK', 'CALIFORNIA', 'TEXAS'],
            'UK': ['UNITED KINGDOM', 'ENGLAND', 'SCOTLAND', 'WALES', 'LONDON'],
            'CA': ['CANADA', 'TORONTO', 'VANCOUVER', 'MONTREAL'],
            'EU': ['GERMANY', 'FRANCE', 'SPAIN', 'ITALY', 'NETHERLANDS'],
            'SG': ['SINGAPORE']
        }
        
        for jurisdiction, keywords in jurisdiction_mappings.items():
            for keyword in keywords:
                if keyword in location_upper:
                    return jurisdiction
                    
        return 'OTHER'

    def _generate_recommendations(self, asset_data: Dict, verification_result: Dict) -> List[str]:
        """Generate recommendations based on verification results"""
        recommendations = []
        
        if verification_result['breakdown']['basic_info'] < 0.8:
            recommendations.append("Provide more detailed asset description")
            
        if verification_result['breakdown']['value_assessment'] < 0.8:
            recommendations.append("Consider professional appraisal for accurate valuation")
            
        if verification_result['breakdown']['compliance'] < 0.8:
            recommendations.append("Verify jurisdiction-specific compliance requirements")
            
        if verification_result['breakdown']['asset_specific'] < 0.8:
            asset_type = asset_data.get('asset_type', 'unknown')
            if asset_type == 'real_estate':
                recommendations.append("Obtain property deeds and recent appraisal")
            elif asset_type == 'vehicle':
                recommendations.append("Provide vehicle title and registration documents")
            elif asset_type == 'artwork':
                recommendations.append("Obtain authenticity certificate and professional appraisal")
                
        return recommendations

    def _define_next_steps(self, status: str, asset_data: Dict) -> List[str]:
        """Define next steps based on verification status"""
        if status == 'verified':
            return [
                "Asset ready for tokenization",
                "Prepare smart contract deployment",
                "Set up marketplace listing"
            ]
        elif status == 'requires_review':
            return [
                "Submit additional documentation",
                "Schedule manual review",
                "Address verification concerns"
            ]
        else:  # rejected or error
            return [
                "Review asset information",
                "Provide missing documentation",
                "Contact support for assistance"
            ]