import 'package:json_annotation/json_annotation.dart';

part 'transaction.g.dart';

@JsonSerializable()
class Transaction {
  @JsonKey(fromJson: _idFromJson, toJson: _idToJson)
  final String? id; // Make id nullable to handle backend responses
  final String vendor;
  final double amount;
  final String date;
  // @JsonKey(name: 'transaction_type')  // Removed - not in current DB schema
  // final String transactionType;       // Removed - not in current DB schema
  final String? category;
  // final bool success;                 // Removed - not in current DB schema
  @JsonKey(name: 'sms_text')            // Updated to match backend schema
  final String smsText;                 // Updated field name
  final double confidence;
  
  // New enhanced fields for advanced classification
  @JsonKey(name: 'payment_method')
  final String? paymentMethod;
  @JsonKey(name: 'is_subscription')
  final bool isSubscription;
  @JsonKey(name: 'subscription_service')
  final String? subscriptionService;
  @JsonKey(name: 'card_last_four')
  final String? cardLastFour;
  @JsonKey(name: 'upi_transaction_id')
  final String? upiTransactionId;
  @JsonKey(name: 'merchant_category')
  final String? merchantCategory;
  @JsonKey(name: 'is_recurring')
  final bool isRecurring;

  Transaction({
    this.id, // Make id optional to handle backend responses
    required this.vendor,
    required this.amount,
    required this.date,
    // required this.transactionType,  // Removed - not in current DB schema
    this.category,
    // required this.success,          // Removed - not in current DB schema
    required this.smsText,             // Updated field name
    required this.confidence,
    // New enhanced fields
    this.paymentMethod,
    this.isSubscription = false,
    this.subscriptionService,
    this.cardLastFour,
    this.upiTransactionId,
    this.merchantCategory,
    this.isRecurring = false,
  });

  factory Transaction.fromJson(Map<String, dynamic> json) =>
      _$TransactionFromJson(json);

  Map<String, dynamic> toJson() => _$TransactionToJson(this);

  // Simple heuristic for transaction type since transactionType field is removed
  // Most SMS transactions are debits (spending), but we can infer from SMS text
  bool get isDebit {
    // Check SMS text for credit indicators
    final smsLower = smsText.toLowerCase();
    return !smsLower.contains('credited') && 
           !smsLower.contains('received') && 
           !smsLower.contains('refund');
  }
  
  bool get isCredit => !isDebit;

  String get formattedAmount {
    return '₹${amount.toStringAsFixed(2)}';
  }

  DateTime get parsedDate {
    try {
      // Handle various date formats
      if (date.contains('-')) {
        // Handle formats like '15-Oct-25', '2025-10-15', etc.
        final parts = date.split('-');
        if (parts.length == 3) {
          // Check if it's in DD-MMM-YY format
          if (parts[1].length == 3) {
            // Convert '15-Oct-25' to proper format
            final monthMap = {
              'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
              'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
              'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
            };
            final day = parts[0].padLeft(2, '0');
            final month = monthMap[parts[1]] ?? '01';
            final year = '20${parts[2]}'; // Assume 20XX for YY format
            final isoDate = '$year-$month-$day';
            return DateTime.parse(isoDate);
          }
        }
      }
      
      // Try parsing as-is (ISO format)
      return DateTime.parse(date);
    } catch (e) {
      // Fallback to current date if parsing fails
      print('Date parsing failed for: $date, using current date');
      return DateTime.now();
    }
  }

  Transaction copyWith({
    String? id,
    String? vendor,
    double? amount,
    String? date,
    // String? transactionType,  // Removed - not in current DB schema
    String? category,
    // bool? success,            // Removed - not in current DB schema
    String? smsText,             // Updated field name
    double? confidence,
    String? paymentMethod,
    bool? isSubscription,
    String? subscriptionService,
    String? cardLastFour,
    String? upiTransactionId,
    String? merchantCategory,
    bool? isRecurring,
  }) {
    return Transaction(
      id: id ?? this.id,
      vendor: vendor ?? this.vendor,
      amount: amount ?? this.amount,
      date: date ?? this.date,
      // transactionType: transactionType ?? this.transactionType,  // Removed
      category: category ?? this.category,
      // success: success ?? this.success,                          // Removed
      smsText: smsText ?? this.smsText,                             // Updated field name
      confidence: confidence ?? this.confidence,
      paymentMethod: paymentMethod ?? this.paymentMethod,
      isSubscription: isSubscription ?? this.isSubscription,
      subscriptionService: subscriptionService ?? this.subscriptionService,
      cardLastFour: cardLastFour ?? this.cardLastFour,
      upiTransactionId: upiTransactionId ?? this.upiTransactionId,
      merchantCategory: merchantCategory ?? this.merchantCategory,
      isRecurring: isRecurring ?? this.isRecurring,
    );
  }
}

// Helper functions for id conversion
String? _idFromJson(dynamic value) {
  if (value == null) return null;
  return value.toString();
}

dynamic _idToJson(String? id) {
  return id;
}
