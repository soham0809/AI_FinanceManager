"""
Intelligent SMS filtering system to identify real financial transactions
vs promotional messages, notifications, and spam
"""
import re
from typing import Dict, List, Tuple, Optional
from enum import Enum

class SMSType(Enum):
    REAL_TRANSACTION = "real_transaction"
    PROMOTIONAL = "promotional"
    NOTIFICATION = "notification"
    SPAM = "spam"
    UNKNOWN = "unknown"

class IntelligentSMSFilter:
    def __init__(self):
        # Real transaction indicators (strong signals)
        self.transaction_keywords = [
            r'\b(debited|credited|paid|received|withdrawn|deposited|transferred)\b',
            r'\bRs\.?\s*\d+\.?\d*\s*(debited|credited|paid|received)',
            r'\bUPI\s+(Ref|ID|Transaction)',
            r'\bA/C\s+.*\s+(debited|credited)',
            r'\baccount.*\s+(debited|credited)',
            r'\bbalance.*Rs\.?\s*\d+',
            r'\btransaction\s+(successful|completed|failed)',
            r'\bpayment.*\s+(successful|completed|failed)',
        ]
        
        # Promotional message indicators (exclude these)
        self.promotional_keywords = [
            r'\b(offer|discount|cashback|reward|gift|free|congratulations|winner)\b',
            r'\b(claim|earn|grab|get|win|bonus|prize)\b',
            r'\b(upgrade|recharge.*plan|subscription.*offer)\b',
            r'\b(limited.*time|hurry|act.*now|don\'t.*miss)\b',
            r'\b(click|visit|download|install|register)\b',
            r'\b(thank.*you.*staying|welcome.*to|enjoy|experience)\b',
        ]
        
        # Notification indicators (exclude these)
        self.notification_keywords = [
            r'\b(alert|notification|reminder|update|expir|due|limit)\b',
            r'\b(plan.*expir|validity.*expir|service.*activ)\b',
            r'\b(data.*usage|balance.*low|recharge.*now)\b',
            r'\b(otp|verification|confirm|activate)\b',
            r'\b(statement|summary|report)\b',
        ]
        
        # Spam indicators (exclude these)
        self.spam_keywords = [
            r'\b(lottery|jackpot|million|crore|lakh.*won)\b',
            r'\b(urgent|immediate|action.*required)\b',
            r'\b(call.*now|sms.*stop|reply.*stop)\b',
        ]
        
        # Strong transaction patterns (amount + action)
        self.strong_transaction_patterns = [
            r'Rs\.?\s*\d+\.?\d*\s*(debited|credited|paid|received)',
            r'(debited|credited|paid|received).*Rs\.?\s*\d+\.?\d*',
            r'A/C.*XX\d+.*(debited|credited).*Rs\.?\s*\d+',
            r'UPI.*Rs\.?\s*\d+\.?\d*',
        ]
        
        # Bank/financial institution senders
        self.financial_senders = [
            r'.*BANK.*', r'.*-BANK-.*', r'.*HDFC.*', r'.*ICICI.*', 
            r'.*SBI.*', r'.*AXIS.*', r'.*KOTAK.*', r'.*CANARA.*',
            r'.*PAYTM.*', r'.*GPAY.*', r'.*PHONEPE.*', r'.*UPI.*'
        ]

    def classify_sms(self, sms_text: str, sender: str = "") -> Tuple[SMSType, float, str]:
        """
        Classify SMS into categories with confidence score and reason
        
        Returns:
            Tuple of (SMSType, confidence_score, reason)
        """
        sms_lower = sms_text.lower()
        sender_lower = sender.lower()
        
        # Check for strong transaction patterns first
        for pattern in self.strong_transaction_patterns:
            if re.search(pattern, sms_lower, re.IGNORECASE):
                return SMSType.REAL_TRANSACTION, 0.95, f"Strong transaction pattern: {pattern}"
        
        # Check if sender is financial institution
        is_financial_sender = any(re.match(pattern, sender_lower, re.IGNORECASE) 
                                for pattern in self.financial_senders)
        
        # Score different aspects
        transaction_score = self._calculate_transaction_score(sms_lower)
        promotional_score = self._calculate_promotional_score(sms_lower)
        notification_score = self._calculate_notification_score(sms_lower)
        spam_score = self._calculate_spam_score(sms_lower)
        
        # Boost transaction score if from financial sender
        if is_financial_sender:
            transaction_score += 0.2
        
        # Determine classification
        scores = {
            SMSType.REAL_TRANSACTION: transaction_score,
            SMSType.PROMOTIONAL: promotional_score,
            SMSType.NOTIFICATION: notification_score,
            SMSType.SPAM: spam_score
        }
        
        max_type = max(scores, key=scores.get)
        max_score = scores[max_type]
        
        # Apply thresholds
        if max_score < 0.3:
            return SMSType.UNKNOWN, max_score, "Low confidence in classification"
        
        # Special rules to prevent false positives
        if max_type == SMSType.REAL_TRANSACTION:
            # Must have amount AND action for real transaction
            has_amount = re.search(r'Rs\.?\s*\d+', sms_lower)
            has_action = any(re.search(keyword, sms_lower, re.IGNORECASE) 
                           for keyword in self.transaction_keywords)
            
            if not (has_amount and has_action):
                # Reclassify as promotional or notification
                if promotional_score > notification_score:
                    return SMSType.PROMOTIONAL, promotional_score, "No clear transaction action"
                else:
                    return SMSType.NOTIFICATION, notification_score, "No clear transaction action"
        
        return max_type, max_score, f"Highest score: {max_score:.2f}"

    def _calculate_transaction_score(self, text: str) -> float:
        """Calculate likelihood of being a real transaction"""
        score = 0.0
        
        for pattern in self.transaction_keywords:
            if re.search(pattern, text, re.IGNORECASE):
                score += 0.3
        
        # Bonus for specific transaction elements
        if re.search(r'Rs\.?\s*\d+\.?\d*', text):
            score += 0.2
        if re.search(r'UPI|NEFT|RTGS|IMPS', text, re.IGNORECASE):
            score += 0.2
        if re.search(r'A/C.*XX\d+', text):
            score += 0.2
        if re.search(r'(successful|completed|failed)', text, re.IGNORECASE):
            score += 0.1
            
        return min(score, 1.0)

    def _calculate_promotional_score(self, text: str) -> float:
        """Calculate likelihood of being promotional"""
        score = 0.0
        
        for pattern in self.promotional_keywords:
            if re.search(pattern, text, re.IGNORECASE):
                score += 0.25
        
        # Penalty for transaction keywords
        for pattern in self.transaction_keywords:
            if re.search(pattern, text, re.IGNORECASE):
                score -= 0.2
                
        return max(score, 0.0)

    def _calculate_notification_score(self, text: str) -> float:
        """Calculate likelihood of being notification"""
        score = 0.0
        
        for pattern in self.notification_keywords:
            if re.search(pattern, text, re.IGNORECASE):
                score += 0.25
                
        return min(score, 1.0)

    def _calculate_spam_score(self, text: str) -> float:
        """Calculate likelihood of being spam"""
        score = 0.0
        
        for pattern in self.spam_keywords:
            if re.search(pattern, text, re.IGNORECASE):
                score += 0.4
                
        return min(score, 1.0)

    def filter_real_transactions(self, sms_list: List[Dict]) -> List[Dict]:
        """
        Filter SMS list to return only real financial transactions
        
        Args:
            sms_list: List of SMS dictionaries with 'text' and optionally 'sender'
            
        Returns:
            List of SMS that are classified as real transactions
        """
        real_transactions = []
        
        for sms in sms_list:
            sms_text = sms.get('text', '')
            sender = sms.get('sender', '')
            
            sms_type, confidence, reason = self.classify_sms(sms_text, sender)
            
            if sms_type == SMSType.REAL_TRANSACTION and confidence > 0.6:
                sms['classification'] = {
                    'type': sms_type.value,
                    'confidence': confidence,
                    'reason': reason
                }
                real_transactions.append(sms)
        
        return real_transactions

    def analyze_sms_batch(self, sms_list: List[Dict]) -> Dict:
        """
        Analyze a batch of SMS and provide detailed breakdown
        """
        results = {
            'total': len(sms_list),
            'real_transactions': 0,
            'promotional': 0,
            'notifications': 0,
            'spam': 0,
            'unknown': 0,
            'details': []
        }
        
        for sms in sms_list:
            sms_text = sms.get('text', '')
            sender = sms.get('sender', '')
            
            sms_type, confidence, reason = self.classify_sms(sms_text, sender)
            
            results['details'].append({
                'text': sms_text[:100] + '...' if len(sms_text) > 100 else sms_text,
                'sender': sender,
                'type': sms_type.value,
                'confidence': confidence,
                'reason': reason
            })
            
            # Count by type
            if sms_type == SMSType.REAL_TRANSACTION:
                results['real_transactions'] += 1
            elif sms_type == SMSType.PROMOTIONAL:
                results['promotional'] += 1
            elif sms_type == SMSType.NOTIFICATION:
                results['notifications'] += 1
            elif sms_type == SMSType.SPAM:
                results['spam'] += 1
            else:
                results['unknown'] += 1
        
        return results
