// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'transaction.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Transaction _$TransactionFromJson(Map<String, dynamic> json) => Transaction(
      id: _idFromJson(json['id']),
      vendor: json['vendor'] as String,
      amount: (json['amount'] as num).toDouble(),
      date: json['date'] as String,
      transactionType: json['transaction_type'] as String,
      category: json['category'] as String?,
      success: json['success'] as bool,
      rawText: json['raw_text'] as String,
      confidence: (json['confidence'] as num).toDouble(),
    );

Map<String, dynamic> _$TransactionToJson(Transaction instance) =>
    <String, dynamic>{
      'id': _idToJson(instance.id),
      'vendor': instance.vendor,
      'amount': instance.amount,
      'date': instance.date,
      'transaction_type': instance.transactionType,
      'category': instance.category,
      'success': instance.success,
      'raw_text': instance.rawText,
      'confidence': instance.confidence,
    };
