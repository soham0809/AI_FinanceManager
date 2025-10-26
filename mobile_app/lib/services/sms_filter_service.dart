import 'package:flutter/foundation.dart';

class SMSFilterService {
  // Keywords that indicate a transaction request rather than actual transaction
  static const List<String> _requestKeywords = [
    'has requested',
    'requesting',
    'request money',
    'money request',
    'on approval',
    'will be debited',
    'will be credited',
    'pending approval',
    'approve payment',
    'payment request',
    'collect request',
    'money collection',
    'tap to pay',
    'click to pay',
    'authorize payment',
    'confirm payment',
    'payment pending',
    'awaiting approval',
    'requires approval',
    'needs approval',
  ];

  // Keywords that indicate promotional/marketing messages
  static const List<String> _promotionalKeywords = [
    'offer',
    'discount',
    'cashback offer',
    'limited time',
    'hurry up',
    'don\'t miss',
    'exclusive deal',
    'special offer',
    'promo code',
    'coupon',
    'sale',
    'free delivery',
    'buy now',
    'shop now',
    'visit our',
    'download app',
    'install app',
    'refer and earn',
    'invite friends',
  ];

  // Keywords that indicate OTP/verification messages
  static const List<String> _otpKeywords = [
    'otp',
    'one time password',
    'verification code',
    'verify',
    'authentication code',
    'security code',
    'login code',
    'access code',
    'pin',
    'do not share',
    'confidential',
    'expires in',
    'valid for',
  ];

  // Keywords that indicate actual completed transactions
  static const List<String> _transactionKeywords = [
    'debited',
    'credited',
    'paid',
    'received',
    'transferred',
    'transaction successful',
    'payment successful',
    'amount deducted',
    'balance',
    'available balance',
    'account balance',
    'transaction id',
    'ref no',
    'reference number',
    'upi ref',
    'transaction completed',
  ];

  /// Analyzes SMS text to determine if it's a valid transaction or should be filtered out
  static SMSAnalysisResult analyzeSMS(String smsText) {
    final lowerText = smsText.toLowerCase();
    
    // Check for transaction requests first (highest priority to filter out)
    for (final keyword in _requestKeywords) {
      if (lowerText.contains(keyword.toLowerCase())) {
        return SMSAnalysisResult(
          isValidTransaction: false,
          filterReason: SMSFilterReason.transactionRequest,
          confidence: 0.9,
          detectedKeywords: [keyword],
        );
      }
    }

    // Check for OTP/verification messages
    for (final keyword in _otpKeywords) {
      if (lowerText.contains(keyword.toLowerCase())) {
        return SMSAnalysisResult(
          isValidTransaction: false,
          filterReason: SMSFilterReason.otpVerification,
          confidence: 0.95,
          detectedKeywords: [keyword],
        );
      }
    }

    // Check for promotional messages
    int promoMatches = 0;
    List<String> promoKeywordsFound = [];
    for (final keyword in _promotionalKeywords) {
      if (lowerText.contains(keyword.toLowerCase())) {
        promoMatches++;
        promoKeywordsFound.add(keyword);
      }
    }
    
    if (promoMatches >= 2) { // Multiple promotional keywords indicate marketing message
      return SMSAnalysisResult(
        isValidTransaction: false,
        filterReason: SMSFilterReason.promotional,
        confidence: 0.8,
        detectedKeywords: promoKeywordsFound,
      );
    }

    // Check for actual transaction indicators
    int transactionMatches = 0;
    List<String> transactionKeywordsFound = [];
    for (final keyword in _transactionKeywords) {
      if (lowerText.contains(keyword.toLowerCase())) {
        transactionMatches++;
        transactionKeywordsFound.add(keyword);
      }
    }

    // If we have transaction keywords and no request keywords, likely valid
    if (transactionMatches > 0) {
      return SMSAnalysisResult(
        isValidTransaction: true,
        filterReason: SMSFilterReason.validTransaction,
        confidence: 0.8 + (transactionMatches * 0.1), // Higher confidence with more keywords
        detectedKeywords: transactionKeywordsFound,
      );
    }

    // Additional heuristics for edge cases
    if (_containsAmountPattern(lowerText) && _containsBankingTerms(lowerText)) {
      // Has amount and banking terms but no clear transaction keywords
      // Could be a transaction, but lower confidence
      return SMSAnalysisResult(
        isValidTransaction: true,
        filterReason: SMSFilterReason.possibleTransaction,
        confidence: 0.6,
        detectedKeywords: ['amount_pattern', 'banking_terms'],
      );
    }

    // Default: uncertain, let LLM decide but flag as low confidence
    return SMSAnalysisResult(
      isValidTransaction: true,
      filterReason: SMSFilterReason.uncertain,
      confidence: 0.3,
      detectedKeywords: [],
    );
  }

  /// Checks if text contains amount patterns (₹, Rs, numbers with decimals)
  static bool _containsAmountPattern(String text) {
    final amountRegex = RegExp(r'(₹|rs\.?|inr)\s*\d+(\.\d{2})?|\d+(\.\d{2})?\s*(₹|rs\.?|inr)', caseSensitive: false);
    return amountRegex.hasMatch(text);
  }

  /// Checks if text contains banking/payment related terms
  static bool _containsBankingTerms(String text) {
    final bankingTerms = ['bank', 'account', 'upi', 'paytm', 'gpay', 'phonepe', 'payment', 'wallet'];
    return bankingTerms.any((term) => text.toLowerCase().contains(term));
  }

  /// Enhanced analysis with context awareness
  static SMSAnalysisResult analyzeWithContext(String smsText, {
    String? senderName,
    DateTime? timestamp,
    List<String>? recentTransactions,
  }) {
    final basicAnalysis = analyzeSMS(smsText);
    
    // Enhance confidence based on sender
    if (senderName != null) {
      final trustedSenders = ['paytm', 'gpay', 'phonepe', 'upi', 'sbi', 'hdfc', 'icici', 'axis'];
      final isTrustedSender = trustedSenders.any((sender) => 
        senderName.toLowerCase().contains(sender));
      
      if (isTrustedSender && basicAnalysis.isValidTransaction) {
        return basicAnalysis.copyWith(
          confidence: (basicAnalysis.confidence + 0.2).clamp(0.0, 1.0),
        );
      }
    }

    // Check for duplicate recent transactions (could indicate spam/repeated requests)
    if (recentTransactions != null && recentTransactions.isNotEmpty) {
      final similarCount = recentTransactions.where((recent) => 
        _calculateSimilarity(smsText, recent) > 0.8).length;
      
      if (similarCount > 2) { // Too many similar messages
        return basicAnalysis.copyWith(
          isValidTransaction: false,
          filterReason: SMSFilterReason.duplicateSpam,
          confidence: 0.9,
        );
      }
    }

    return basicAnalysis;
  }

  /// Calculate text similarity (simple implementation)
  static double _calculateSimilarity(String text1, String text2) {
    final words1 = text1.toLowerCase().split(' ').toSet();
    final words2 = text2.toLowerCase().split(' ').toSet();
    final intersection = words1.intersection(words2);
    final union = words1.union(words2);
    return union.isEmpty ? 0.0 : intersection.length / union.length;
  }
}

/// Result of SMS analysis
class SMSAnalysisResult {
  final bool isValidTransaction;
  final SMSFilterReason filterReason;
  final double confidence; // 0.0 to 1.0
  final List<String> detectedKeywords;

  const SMSAnalysisResult({
    required this.isValidTransaction,
    required this.filterReason,
    required this.confidence,
    required this.detectedKeywords,
  });

  SMSAnalysisResult copyWith({
    bool? isValidTransaction,
    SMSFilterReason? filterReason,
    double? confidence,
    List<String>? detectedKeywords,
  }) {
    return SMSAnalysisResult(
      isValidTransaction: isValidTransaction ?? this.isValidTransaction,
      filterReason: filterReason ?? this.filterReason,
      confidence: confidence ?? this.confidence,
      detectedKeywords: detectedKeywords ?? this.detectedKeywords,
    );
  }

  @override
  String toString() {
    return 'SMSAnalysisResult(valid: $isValidTransaction, reason: $filterReason, confidence: ${(confidence * 100).toStringAsFixed(1)}%, keywords: $detectedKeywords)';
  }
}

/// Reasons why an SMS might be filtered or accepted
enum SMSFilterReason {
  validTransaction,
  possibleTransaction,
  transactionRequest,
  otpVerification,
  promotional,
  duplicateSpam,
  uncertain,
}

/// Extension to get human-readable descriptions
extension SMSFilterReasonExtension on SMSFilterReason {
  String get description {
    switch (this) {
      case SMSFilterReason.validTransaction:
        return 'Valid completed transaction';
      case SMSFilterReason.possibleTransaction:
        return 'Possible transaction (uncertain)';
      case SMSFilterReason.transactionRequest:
        return 'Transaction request/approval needed';
      case SMSFilterReason.otpVerification:
        return 'OTP/verification message';
      case SMSFilterReason.promotional:
        return 'Promotional/marketing message';
      case SMSFilterReason.duplicateSpam:
        return 'Duplicate/spam message';
      case SMSFilterReason.uncertain:
        return 'Uncertain - needs LLM analysis';
    }
  }
}
