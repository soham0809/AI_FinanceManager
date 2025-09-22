import 'package:json_annotation/json_annotation.dart';

part 'transaction.g.dart';

@JsonSerializable()
class Transaction {
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
    );
  }
}
