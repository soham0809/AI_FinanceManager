import 'package:json_annotation/json_annotation.dart';

part 'transaction.g.dart';

@JsonSerializable()
class Transaction {
  @JsonKey(fromJson: _idFromJson, toJson: _idToJson)
  final String? id; // Make id nullable to handle backend responses
  final String vendor;
  final double amount;
  final String date;
  @JsonKey(name: 'transaction_type')
  final String transactionType;
  final String? category;
  final bool success;
  @JsonKey(name: 'raw_text')
  final String rawText;
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
    required this.transactionType,
    this.category,
    required this.success,
    required this.rawText,
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

  bool get isDebit => transactionType.toLowerCase() == 'debit';
  bool get isCredit => transactionType.toLowerCase() == 'credit';

  String get formattedAmount {
    return '₹${amount.toStringAsFixed(2)}';
  }

  DateTime get parsedDate {
    return DateTime.parse(date);
  }

  Transaction copyWith({
    String? id,
    String? vendor,
    double? amount,
    String? date,
    String? transactionType,
    String? category,
    bool? success,
    String? rawText,
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
      transactionType: transactionType ?? this.transactionType,
      category: category ?? this.category,
      success: success ?? this.success,
      rawText: rawText ?? this.rawText,
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
