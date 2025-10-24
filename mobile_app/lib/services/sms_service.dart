import 'package:flutter/material.dart';
import 'package:permission_handler/permission_handler.dart';
import '../models/transaction.dart';
import 'api_service.dart';
import 'mock_sms_service.dart';
import 'package:flutter/services.dart';
import 'package:uuid/uuid.dart'; // Import the uuid package

class SMSService {
  static final SMSService _instance = SMSService._internal();
  factory SMSService() => _instance;
  SMSService._internal();
  
  final ApiService _apiService = ApiService();
  static const MethodChannel _channel = MethodChannel('sms_reader');
  final Uuid _uuid = Uuid(); // Initialize Uuid
  
  // Check if SMS permissions are granted
  Future<bool> hasPermissions() async {
    final status = await Permission.sms.status;
    return status.isGranted;
  }
  
  // Request SMS permissions
  Future<bool> requestPermissions() async {
    final status = await Permission.sms.request();
    return status.isGranted;
  }
  
  // Get all SMS messages from device
  Future<List<String>> getAllSMS() async {
    try {
      // Check permissions first
      if (!await hasPermissions()) {
        final granted = await requestPermissions();
        if (!granted) {
          debugPrint('SMS permissions not granted');
          return MockSmsService.getMockSmsMessages(count: 10);
        }
      }
      
      // Try to read real SMS messages using platform channel
      final List<dynamic> messages = await _channel.invokeMethod('getAllSMS');
      final List<String> smsMessages = messages.cast<String>();
      
      // Extract just the message body from formatted SMS
      return smsMessages.map((formattedSms) {
        final bodyIndex = formattedSms.indexOf('BODY: ');
        if (bodyIndex != -1) {
          return formattedSms.substring(bodyIndex + 6);
        }
        return formattedSms;
      }).toList();
    } catch (e) {
      debugPrint('Error reading SMS messages: $e');
      // Fallback to mock data if SMS reading fails
      return MockSmsService.getMockSmsMessages(count: 10);
    }
  }
  
  // Get transaction-related SMS messages from device
  Future<List<String>> getTransactionSMS({int limit = 100}) async {
    try {
      debugPrint('Starting SMS scan - checking permissions...');
      
      // Check permissions first
      if (!await hasPermissions()) {
        debugPrint('SMS permissions not granted, requesting...');
        final granted = await requestPermissions();
        if (!granted) {
          debugPrint('SMS permissions denied by user');
          return MockSmsService.getMockSmsMessages(count: limit);
        }
        debugPrint('SMS permissions granted');
      } else {
        debugPrint('SMS permissions already granted');
      }
      
      debugPrint('Calling platform channel to get SMS messages...');
      // Use platform channel to get filtered transaction SMS directly
      final Map<String, dynamic> arguments = {'limit': limit};
      final List<dynamic> messages = await _channel.invokeMethod('getTransactionSMS', arguments);
      final List<String> smsMessages = messages.cast<String>();
      
      debugPrint('Raw SMS messages received: ${smsMessages.length}');
      
      // Extract just the message body from formatted SMS
      final transactionSMS = smsMessages.map((formattedSms) {
        final bodyIndex = formattedSms.indexOf('BODY: ');
        if (bodyIndex != -1) {
          return formattedSms.substring(bodyIndex + 6);
        }
        return formattedSms;
      }).toList();
      
      debugPrint('✅ SUCCESS: Found ${transactionSMS.length} transaction SMS from device');
      
      // Log first few messages for debugging
      for (int i = 0; i < transactionSMS.length && i < 3; i++) {
        debugPrint('SMS $i: ${transactionSMS[i].substring(0, transactionSMS[i].length > 100 ? 100 : transactionSMS[i].length)}...');
      }
      
      return transactionSMS;
    } catch (e) {
      debugPrint('❌ ERROR reading transaction SMS: $e');
      debugPrint('Stack trace: ${StackTrace.current}');
      // Fallback to mock data if SMS reading fails
      return MockSmsService.getMockSmsMessages(count: limit);
    }
  }
  
  // Parse SMS and send to backend
  Future<Transaction?> parseSMSToTransaction(String smsText) async {
    try {
      final response = await _apiService.parseSms(smsText);
      
      if (response['success'] == true) {
        return Transaction(
          id: _uuid.v4(), // Add unique ID
          vendor: response['vendor'],
          amount: response['amount'].toDouble(),
          date: response['date'],
          category: response['category'],
          smsText: smsText,  // Updated field name
          confidence: response['confidence']?.toDouble() ?? 0.0,
        );
      }
      
      return null;
    } catch (e) {
      debugPrint('Error parsing SMS: $e');
      return null;
    }
  }
  
  // Mock SMS listening for testing
  void startListening() {
    // For testing, simulate periodic SMS arrival
    MockSmsService.simulateSmsStream().listen((smsText) async {
      final transaction = await parseSMSToTransaction(smsText);
      if (transaction != null) {
        debugPrint('New mock transaction: ${transaction.vendor} - ${transaction.amount}');
      }
    });
  }

  // Legacy method for compatibility
  Future<void> setupSMSListener(Function(Transaction) callback) async {
    startListening();
  }

  // Parse transaction SMS method for compatibility
  Future<List<Transaction>> parseTransactionSMS({int limit = 100}) async {
    final smsMessages = await getTransactionSMS(limit: limit);
    final List<Transaction> transactions = [];
    
    for (final sms in smsMessages) {
      final transaction = await parseSMSToTransaction(sms);
      if (transaction != null) {
        transactions.add(transaction);
      }
    }
    
    return transactions;
  }
  Future<Map<String, dynamic>> getSMSStats() async {
    try {
      final transactionSMS = await getTransactionSMS(limit: 1000);
      
      // Count by sender (mock implementation)
      final Map<String, int> senderCounts = {
        'Bank SMS': transactionSMS.length ~/ 2,
        'UPI Alerts': transactionSMS.length ~/ 3,
        'Other': transactionSMS.length - (transactionSMS.length ~/ 2) - (transactionSMS.length ~/ 3),
      };
      final Map<String, int> monthlyCounts = {};
      
      // Mock monthly counts
      final now = DateTime.now();
      for (int i = 0; i < 6; i++) {
        final month = DateTime(now.year, now.month - i);
        final monthKey = '${month.year}-${month.month.toString().padLeft(2, '0')}';
        monthlyCounts[monthKey] = (transactionSMS.length / (i + 1)).round();
      }
      
      return {
        'totalTransactionSMS': transactionSMS.length,
        'topSenders': senderCounts.entries
            .toList()
            ..sort((a, b) => b.value.compareTo(a.value)),
        'monthlyBreakdown': monthlyCounts,
      };
    } catch (e) {
      debugPrint('Error getting SMS stats: $e');
      return {
        'totalTransactionSMS': 0,
        'topSenders': <MapEntry<String, int>>[],
        'monthlyBreakdown': <String, int>{},
      };
    }
  }
}
