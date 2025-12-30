import 'package:flutter/material.dart';
import 'package:permission_handler/permission_handler.dart';
import '../models/transaction.dart';
import 'api_service.dart';
import 'mock_sms_service.dart';
import 'package:flutter/services.dart';
import 'package:uuid/uuid.dart'; // Import the uuid package

/// Structured SMS message with metadata for temporal-context aware parsing
class SMSMessage {
  final String body;
  final String sender;
  final int deviceTimestamp; // Milliseconds since epoch

  SMSMessage({
    required this.body,
    required this.sender,
    required this.deviceTimestamp,
  });

  /// Convert to JSON for API request
  Map<String, dynamic> toJson() => {
    'sms_text': body,
    'sender': sender,
    'device_timestamp': deviceTimestamp,
  };
  
  /// Parse from formatted string: "FROM: address | DATE: timestamp | BODY: message"
  factory SMSMessage.fromFormattedString(String formattedSms) {
    final fromMatch = RegExp(r'FROM: (.+?) \|').firstMatch(formattedSms);
    final dateMatch = RegExp(r'DATE: (\d+) \|').firstMatch(formattedSms);
    final bodyMatch = RegExp(r'BODY: (.+)$', dotAll: true).firstMatch(formattedSms);
    
    return SMSMessage(
      sender: fromMatch?.group(1) ?? 'Unknown',
      deviceTimestamp: int.tryParse(dateMatch?.group(1) ?? '0') ?? DateTime.now().millisecondsSinceEpoch,
      body: bodyMatch?.group(1) ?? formattedSms,
    );
  }
}

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
      
      // Parse to structured SMSMessage objects (preserving metadata)
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
  
  /// NEW: Get transaction SMS with full metadata (sender, timestamp, body)
  /// This is the preferred method for temporal-context aware parsing
  Future<List<SMSMessage>> getTransactionSMSWithMetadata({int limit = 100}) async {
    try {
      debugPrint('Starting SMS scan with metadata - checking permissions...');
      
      if (!await hasPermissions()) {
        final granted = await requestPermissions();
        if (!granted) {
          debugPrint('SMS permissions denied');
          // Return mock data as SMSMessage objects
          return MockSmsService.getMockSmsMessages(count: limit)
              .map((body) => SMSMessage(
                    body: body,
                    sender: 'MOCK-SENDER',
                    deviceTimestamp: DateTime.now().millisecondsSinceEpoch,
                  ))
              .toList();
        }
      }
      
      debugPrint('Calling platform channel for SMS with metadata...');
      final Map<String, dynamic> arguments = {'limit': limit};
      final List<dynamic> messages = await _channel.invokeMethod('getTransactionSMS', arguments);
      
      // Parse formatted strings to structured SMSMessage objects
      final List<SMSMessage> smsWithMetadata = messages
          .cast<String>()
          .map((formatted) => SMSMessage.fromFormattedString(formatted))
          .toList();
      
      debugPrint('✅ SUCCESS: Got ${smsWithMetadata.length} SMS with metadata');
      
      // Log first few for debugging
      for (int i = 0; i < smsWithMetadata.length && i < 2; i++) {
        final sms = smsWithMetadata[i];
        debugPrint('SMS $i: sender=${sms.sender}, timestamp=${sms.deviceTimestamp}, body=${sms.body.substring(0, sms.body.length > 50 ? 50 : sms.body.length)}...');
      }
      
      return smsWithMetadata;
    } catch (e) {
      debugPrint('❌ ERROR getting SMS with metadata: $e');
      // Fallback to mock data
      return MockSmsService.getMockSmsMessages(count: limit)
          .map((body) => SMSMessage(
                body: body,
                sender: 'MOCK-SENDER',
                deviceTimestamp: DateTime.now().millisecondsSinceEpoch,
              ))
          .toList();
    }
  }
  
  // Parse SMS and send to backend (legacy - body only)
  Future<Transaction?> parseSMSToTransaction(String smsText) async {
    return parseSMSMessageToTransaction(SMSMessage(
      body: smsText,
      sender: 'unknown',
      deviceTimestamp: DateTime.now().millisecondsSinceEpoch,
    ));
  }
  
  /// NEW: Parse SMS with full metadata for temporal-context aware parsing
  Future<Transaction?> parseSMSMessageToTransaction(SMSMessage sms) async {
    try {
      // Use the new API method that sends metadata
      final response = await _apiService.parseSmsWithMetadata(sms);
      
      if (response['success'] == true) {
        return Transaction(
          id: _uuid.v4(),
          vendor: response['vendor'],
          amount: response['amount'].toDouble(),
          date: response['date'],
          category: response['category'],
          smsText: sms.body,
          confidence: response['confidence']?.toDouble() ?? 0.0,
        );
      }
      
      return null;
    } catch (e) {
      debugPrint('Error parsing SMS with metadata: $e');
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
