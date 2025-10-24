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
      category: json['category'] as String?,
      smsText: json['sms_text'] as String,
      confidence: (json['confidence'] as num).toDouble(),
      paymentMethod: json['payment_method'] as String?,
      isSubscription: json['is_subscription'] as bool? ?? false,
      subscriptionService: json['subscription_service'] as String?,
      cardLastFour: json['card_last_four'] as String?,
      upiTransactionId: json['upi_transaction_id'] as String?,
      merchantCategory: json['merchant_category'] as String?,
      isRecurring: json['is_recurring'] as bool? ?? false,
    );

Map<String, dynamic> _$TransactionToJson(Transaction instance) =>
    <String, dynamic>{
      'id': _idToJson(instance.id),
      'vendor': instance.vendor,
      'amount': instance.amount,
      'date': instance.date,
      'category': instance.category,
      'sms_text': instance.smsText,
      'confidence': instance.confidence,
      'payment_method': instance.paymentMethod,
      'is_subscription': instance.isSubscription,
      'subscription_service': instance.subscriptionService,
      'card_last_four': instance.cardLastFour,
      'upi_transaction_id': instance.upiTransactionId,
      'merchant_category': instance.merchantCategory,
      'is_recurring': instance.isRecurring,
    };
