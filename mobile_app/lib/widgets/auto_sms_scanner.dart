import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import 'package:provider/provider.dart';
import '../services/sms_service.dart';
import '../providers/transaction_provider.dart';
import '../models/transaction.dart';
import 'package:uuid/uuid.dart';

class AutoSMSScanner extends StatefulWidget {
  const AutoSMSScanner({super.key});

  @override
  State<AutoSMSScanner> createState() => _AutoSMSScannerState();
}

class _AutoSMSScannerState extends State<AutoSMSScanner> {
  final SMSService _smsService = SMSService();
  final Uuid _uuid = Uuid(); // Initialize Uuid here
  bool _isScanning = false;
  bool _hasPermissions = false;
  int _foundTransactions = 0;
  String? _scanStatus;
  bool _useLocalBatch = true;

  @override
  void initState() {
    super.initState();
    _checkPermissions();
  }

  Future<void> _checkPermissions() async {
    final hasPermissions = await _smsService.hasPermissions();
    setState(() => _hasPermissions = hasPermissions);
  }

  Future<void> _scanTransactionSMS() async {
    debugPrint('🔍 SMS Scan started - checking permissions...');
    
    if (!_hasPermissions) {
      debugPrint('❌ No SMS permissions, requesting...');
      final granted = await _smsService.requestPermissions();
      if (!granted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('SMS permissions required for auto-scanning'),
            backgroundColor: Colors.orange,
          ),
        );
        return;
      }
      setState(() => _hasPermissions = true);
    }

    setState(() {
      _isScanning = true;
      _foundTransactions = 0;
      _scanStatus = 'Reading SMS messages with metadata...';
    });

    try {
      debugPrint('📱 Getting transaction SMS with metadata from device...');
      
      // NEW: Get SMS with full metadata (sender, timestamp, body)
      final smsWithMetadata = await _smsService.getTransactionSMSWithMetadata(limit: 100);
      
      debugPrint('📨 Found ${smsWithMetadata.length} SMS messages with metadata');
      
      setState(() {
        _foundTransactions = smsWithMetadata.length;
        _scanStatus = 'Found ${smsWithMetadata.length} transaction SMS!';
      });

      // Use server-side batch parsing with progress polling
      final provider = context.read<TransactionProvider>();
      setState(() => _scanStatus = _useLocalBatch ? 'Starting LOCAL batch parsing on server...' : 'Starting LLM batch parsing on server...');

      // NEW: Kick off background batch job WITH METADATA for fingerprint dedup
      final startResp = await provider.apiService.startParseSmsBatchWithMetadata(
        smsWithMetadata,
        batchSize: 10,  // Process 10 messages at a time
        delaySeconds: 3,  // 3 second delay between batches
        useLocal: _useLocalBatch,
      );
      final String jobId = startResp['job_id'];

      // Poll job status until completed/failed
      int lastProcessed = 0;
      while (mounted) {
        try {
          final status = await provider.apiService.getQuickJobStatus(jobId);
          final s = (status['status'] ?? '').toString();
          final total = status['result']?['total'] ?? status['total'] ?? smsMessages.length;
          final processed = status['result']?['processed'] ?? status['processed'] ?? 0;
          final success = status['result']?['success'] ?? status['success'] ?? 0;
          final failed = status['result']?['failed'] ?? status['failed'] ?? 0;
          final items = status['result']?['items'] ?? status['items'];
          String lastInfo = '';
          if (items is List && items.isNotEmpty) {
            final last = items.last;
            if (last is Map && (last['success'] == true)) {
              final vendor = (last['vendor'] ?? '').toString();
              final amount = last['amount'];
              lastInfo = vendor.isNotEmpty ? ' • Last: ' + vendor + (amount != null ? ' - ₹' + amount.toString() : '') : '';
            } else {
              lastInfo = ' • Last: failed';
            }
          }

          if (processed != lastProcessed) {
            setState(() => _scanStatus = (_useLocalBatch ? 'LOCAL parsing' : 'LLM parsing') + '... ' + '$processed/$total (✓$success ✗$failed)' + lastInfo);
            lastProcessed = processed;
          }

          if (s == 'completed') {
            setState(() {
              _foundTransactions = success is int ? success : 0;
              _scanStatus = (_useLocalBatch ? 'Local' : 'LLM') + ' batch completed: $success saved, $failed failed';
            });
            break;
          }
          if (s == 'failed') {
            setState(() => _scanStatus = (_useLocalBatch ? 'Local' : 'LLM') + ' batch failed after $processed/$total');
            break;
          }
        } catch (e) {
          // Transient failure (server reload, tunnel hiccup). Keep polling.
          setState(() => _scanStatus = 'Waiting for server... retrying');
        }

        await Future.delayed(const Duration(seconds: 2));
      }

      // Refresh user-specific transactions from server
      await provider.fetchTransactions();

      // Show success message
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('✅ ' + (_useLocalBatch ? 'LOCAL' : 'LLM') + ' batch parsed ${smsMessages.length} SMS. Saved $_foundTransactions transactions.'),
            backgroundColor: Colors.green,
            duration: Duration(seconds: 5),
          ),
        );
      }
      
    } catch (e) {
      debugPrint('❌ SMS scan error: $e');
      setState(() => _scanStatus = 'Scan failed: $e');
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('SMS scan failed: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      setState(() => _isScanning = false);
      
      // Clear status after 5 seconds
      Future.delayed(const Duration(seconds: 5), () {
        if (mounted) {
          setState(() => _scanStatus = null);
        }
      });
    }
  }

  // Enhanced SMS parsing to extract transaction details
  Transaction? _createTransactionFromSMS(String smsText, int index) {
    try {
      // Enhanced regex patterns for Indian banking SMS
      final amountPatterns = [
        RegExp(r'Rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)', caseSensitive: false),
        RegExp(r'INR\s*(\d+(?:,\d+)*(?:\.\d{2})?)', caseSensitive: false),
        RegExp(r'₹\s*(\d+(?:,\d+)*(?:\.\d{2})?)', caseSensitive: false),
        RegExp(r'amount.*?(\d+(?:,\d+)*(?:\.\d{2})?)', caseSensitive: false),
      ];

      final vendorPatterns = [
        RegExp(r'paid to ([\w\s]+)', caseSensitive: false),
        RegExp(r'from ([\w\s]+)', caseSensitive: false),
        RegExp(r'at ([\w\s]+)', caseSensitive: false),
        RegExp(r'UPI.*?to ([\w\s]+)', caseSensitive: false),
      ];

      // Extract amount
      double? amount;
      for (final pattern in amountPatterns) {
        final match = pattern.firstMatch(smsText);
        if (match != null) {
          final amountStr = match.group(1)?.replaceAll(',', '') ?? '';
          amount = double.tryParse(amountStr);
          if (amount != null) break;
        }
      }

      // Extract vendor/merchant with enhanced patterns
      String vendor = 'Unknown';
      
      // Enhanced vendor extraction patterns for Indian banking SMS
      final specificVendorPatterns = [
        RegExp(r'paid to ([\w\s@.-]+?)(?:\s|$|\()', caseSensitive: false),
        RegExp(r'from a/c no\.\s*(\w+)', caseSensitive: false),
        RegExp(r'UPI.*?to ([\w\s@.-]+?)(?:\s|$|\()', caseSensitive: false),
        RegExp(r'merchant ([\w\s@.-]+?)(?:\s|$|\()', caseSensitive: false),
        RegExp(r'at ([\w\s@.-]+?)(?:\s|$|\()', caseSensitive: false),
        RegExp(r'credited.*?from ([\w\s@.-]+?)(?:\s|$|\()', caseSensitive: false),
        RegExp(r'debited.*?to ([\w\s@.-]+?)(?:\s|$|\()', caseSensitive: false),
      ];
      
      for (final pattern in specificVendorPatterns) {
        final match = pattern.firstMatch(smsText);
        if (match != null) {
          String extractedVendor = match.group(1)?.trim() ?? '';
          if (extractedVendor.isNotEmpty && extractedVendor.length > 2) {
            vendor = extractedVendor;
            // Clean up vendor name
            vendor = vendor.replaceAll(RegExp(r'[^\w\s@.-]'), '').trim();
            vendor = vendor.replaceAll(RegExp(r'\s+'), ' ').trim();
            if (vendor.length > 25) vendor = vendor.substring(0, 25);
            break;
          }
        }
      }
      
      // If no specific vendor found, extract from bank name, sender, or transaction type
      if (vendor == 'Unknown' || vendor.length < 3) {
        if (smsText.contains('CANBNK') || smsText.contains('Canara')) vendor = 'Canara Bank Transfer';
        else if (smsText.contains('TDCBNK') || smsText.contains('TD Bank')) vendor = 'TD Bank';
        else if (smsText.contains('ICICI')) vendor = 'ICICI Bank';
        else if (smsText.contains('HDFC')) vendor = 'HDFC Bank';
        else if (smsText.contains('IDFCFB')) vendor = 'IDFC First Bank';
        else if (smsText.contains('SBI')) vendor = 'State Bank';
        else if (smsText.contains('AXIS')) vendor = 'Axis Bank';
        else if (smsText.contains('KOTAK')) vendor = 'Kotak Bank';
        else if (smsText.contains('AVANSE')) vendor = 'Avanse Education Loan';
        else if (smsText.contains('PAYTM')) vendor = 'Paytm';
        else if (smsText.contains('GPAY')) vendor = 'Google Pay';
        else if (smsText.contains('PHONEPE')) vendor = 'PhonePe';
        else if (smsText.contains('JIOPAY') || smsText.contains('Jio')) vendor = 'Jio Recharge';
        else if (smsText.contains('AMAZON') || smsText.contains('Amazon')) vendor = 'Amazon';
        else if (smsText.contains('UPI')) vendor = 'UPI Transfer';
        else if (smsText.contains('ATM')) vendor = 'ATM Withdrawal';
        else if (smsText.contains('Cheque')) vendor = 'Cheque Payment';
        else if (smsText.contains('mandate')) vendor = 'Auto Debit';
        else vendor = 'Bank Transaction';
      }

      // Determine transaction type
      String transactionType = 'debit';
      if (smsText.toLowerCase().contains('credited') || 
          smsText.toLowerCase().contains('received') ||
          smsText.toLowerCase().contains('refund')) {
        transactionType = 'credit';
      }

      // Smart category detection based on SMS content
      String category = _detectCategory(smsText, vendor);

      // Extract date (use current date if not found)
      String date = DateTime.now().toIso8601String();
      final datePattern = RegExp(r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})');
      final dateMatch = datePattern.firstMatch(smsText);
      if (dateMatch != null) {
        try {
          final dateStr = dateMatch.group(1) ?? '';
          // Parse Indian date format (dd-mm-yy or dd/mm/yy)
          final parts = dateStr.split(RegExp(r'[-/]'));
          if (parts.length == 3) {
            int day = int.parse(parts[0]);
            int month = int.parse(parts[1]);
            int year = int.parse(parts[2]);
            if (year < 100) year += 2000; // Convert 2-digit year
            date = DateTime(year, month, day).toIso8601String();
          }
        } catch (e) {
          // Keep current date if parsing fails
        }
      }

      if (amount == null || amount <= 0) return null;

      return Transaction(
        id: _uuid.v4(), // Add unique ID
        vendor: vendor,
        amount: amount,
        date: date,
        category: category,
        smsText: smsText,  // Updated field name
        confidence: 0.85, // High confidence for real SMS data
      );
    } catch (e) {
      debugPrint('Error creating transaction from SMS: $e');
      return null;
    }
  }

  // Enhanced category detection based on SMS content and vendor
  String _detectCategory(String smsText, String vendor) {
    final text = smsText.toLowerCase();
    final vendorLower = vendor.toLowerCase();

    // Food & Dining
    if (text.contains('swiggy') || text.contains('zomato') || 
        text.contains('restaurant') || text.contains('food') ||
        text.contains('cafe') || text.contains('hotel')) {
      return 'Food & Dining';
    }

    // Transportation
    if (text.contains('uber') || text.contains('ola') || 
        text.contains('metro') || text.contains('bus') ||
        text.contains('taxi') || text.contains('petrol') ||
        text.contains('fuel')) {
      return 'Transportation';
    }

    // Shopping
    if (text.contains('amazon') || text.contains('flipkart') || 
        text.contains('myntra') || text.contains('shopping') ||
        text.contains('purchase') || vendorLower.contains('store')) {
      return 'Shopping';
    }

    // Utilities
    if (text.contains('electricity') || text.contains('water') || 
        text.contains('gas') || text.contains('internet') ||
        text.contains('mobile') || text.contains('recharge') ||
        text.contains('jio') || text.contains('airtel')) {
      return 'Utilities';
    }

    // Healthcare
    if (text.contains('hospital') || text.contains('medical') || 
        text.contains('pharmacy') || text.contains('doctor') ||
        text.contains('clinic')) {
      return 'Healthcare';
    }

    // Financial
    if (text.contains('bank') || text.contains('loan') || 
        text.contains('emi') || text.contains('interest') ||
        text.contains('fee') || text.contains('charge')) {
      return 'Financial';
    }

    // Education
    if (text.contains('school') || text.contains('college') || 
        text.contains('university') || text.contains('course') ||
        text.contains('tuition') || text.contains('education')) {
      return 'Education';
    }

    // Entertainment
    if (text.contains('movie') || text.contains('netflix') || 
        text.contains('spotify') || text.contains('game') ||
        text.contains('entertainment')) {
      return 'Entertainment';
    }

    return 'Others';
  }

  // Process SMS in background thread to avoid blocking main UI thread
  Future<List<Transaction>> _processSMSInBackground(List<String> smsMessages) async {
    try {
      return await compute(_processSMSList, smsMessages);
    } catch (e) {
      debugPrint('Background processing error: $e');
      // Fallback to main thread processing if compute fails
      return _processSMSListSync(smsMessages);
    }
  }

  // Synchronous fallback processing
  List<Transaction> _processSMSListSync(List<String> smsMessages) {
    final transactions = <Transaction>[];
    
    for (int i = 0; i < smsMessages.length; i++) {
      try {
        final transaction = _createTransactionFromSMS(smsMessages[i], i);
        if (transaction != null) {
          transactions.add(transaction);
        }
      } catch (e) {
        debugPrint('Error processing SMS ${i + 1}: $e');
      }
    }
    
    return transactions;
  }

  Future<void> _setupRealTimeListener() async {
    if (!_hasPermissions) return;

    try {
      await _smsService.setupSMSListener((Transaction transaction) {
        // Add new transaction to provider
        context.read<TransactionProvider>().parseSMSAndAddTransaction(transaction.smsText);
        
        // Show notification
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('New transaction: ${transaction.vendor} - ${transaction.formattedAmount}'),
              backgroundColor: Colors.blue,
              duration: const Duration(seconds: 2),
            ),
          );
        }
      });
    } catch (e) {
      print('Failed to setup SMS listener: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.auto_awesome,
                  color: _hasPermissions ? Colors.blue : Colors.grey,
                  size: 24,
                ),
                const SizedBox(width: 8),
                const Text(
                  'Auto SMS Scanner',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            
            if (!_hasPermissions) ...[
              const Text(
                'Grant SMS permissions to automatically scan and import your transaction history.',
                style: TextStyle(color: Colors.grey),
              ),
            ] else ...[
              const Text(
                'Automatically scan your SMS for bank and UPI transaction alerts.',
                style: TextStyle(color: Colors.grey),
              ),
              const SizedBox(height: 12),
              
              if (_scanStatus != null) ...[
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.blue.shade50,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    children: [
                      if (_isScanning) ...[
                        const SizedBox(
                          width: 16,
                          height: 16,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        ),
                        const SizedBox(width: 8),
                      ],
                      Expanded(child: Text(_scanStatus!)),
                    ],
                  ),
                ),
                const SizedBox(height: 12),
              ],
              
              // Mode toggle: NLP vs LLM
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Batch Parsing Mode:', style: TextStyle(fontWeight: FontWeight.w500)),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Expanded(
                        child: ChoiceChip(
                          label: const Text('🚀 NLP Quick Parse'),
                          selected: _useLocalBatch,
                          onSelected: (v) => setState(() => _useLocalBatch = true),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: ChoiceChip(
                          label: const Text('🤖 LLM Detailed Parse'),
                          selected: !_useLocalBatch,
                          onSelected: (v) => setState(() => _useLocalBatch = false),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    _useLocalBatch ? 'Fast regex-based parsing' : 'AI-powered detailed analysis',
                    style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                  ),
                ],
              ),
              const SizedBox(height: 12),

              Row(
                children: [
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: _isScanning ? null : _scanTransactionSMS,
                      icon: Icon(_isScanning ? Icons.hourglass_empty : Icons.scanner),
                      label: Text(_isScanning ? 'Scanning...' : 'Scan SMS History'),
                    ),
                  ),
                  const SizedBox(width: 8),
                  ElevatedButton.icon(
                    onPressed: _isScanning ? null : _setupRealTimeListener,
                    icon: const Icon(Icons.notifications_active),
                    label: const Text('Live'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green.shade600,
                      foregroundColor: Colors.white,
                    ),
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }
}

// Static function for background SMS processing (required for compute)
List<Transaction> _processSMSList(List<String> smsMessages) {
  final transactions = <Transaction>[];
  final Uuid _uuidStatic = Uuid(); // Initialize Uuid for static method
  
  for (int i = 0; i < smsMessages.length; i++) {
    try {
      final transaction = _createTransactionFromSMSStatic(smsMessages[i], i, _uuidStatic);
      if (transaction != null) {
        transactions.add(transaction);
      }
    } catch (e) {
      debugPrint('Error processing SMS ${i + 1}: $e');
    }
  }
  
  return transactions;
}

// Static version of SMS parsing for background processing
Transaction? _createTransactionFromSMSStatic(String smsText, int index, Uuid uuidStatic) {
  try {
    // Enhanced regex patterns for Indian banking SMS
    final amountPatterns = [
      RegExp(r'Rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)', caseSensitive: false),
      RegExp(r'INR\s*(\d+(?:,\d+)*(?:\.\d{2})?)', caseSensitive: false),
      RegExp(r'₹\s*(\d+(?:,\d+)*(?:\.\d{2})?)', caseSensitive: false),
      RegExp(r'amount.*?(\d+(?:,\d+)*(?:\.\d{2})?)', caseSensitive: false),
    ];

    // Extract amount
    double? amount;
    for (final pattern in amountPatterns) {
      final match = pattern.firstMatch(smsText);
      if (match != null) {
        final amountStr = match.group(1)?.replaceAll(',', '') ?? '';
        amount = double.tryParse(amountStr);
        if (amount != null) break;
      }
    }

    // Extract vendor/merchant with enhanced patterns
    String vendor = 'Unknown';
    
    final specificVendorPatterns = [
      RegExp(r'paid to ([\w\s@.-]+?)(?:\s|$|\()', caseSensitive: false),
      RegExp(r'to\s+([\w\s@.-]+?)\s+via\s+upi', caseSensitive: false),
      RegExp(r'UPI.*?to ([\w\s@.-]+?)(?:\s|$|\()', caseSensitive: false),
      RegExp(r'merchant ([\w\s@.-]+?)(?:\s|$|\()', caseSensitive: false),
      RegExp(r'at ([\w\s@.-]+?)(?:\s|$|\()', caseSensitive: false),
      RegExp(r'credited.*?from ([\w\s@.-]+?)(?:\s|$|\()', caseSensitive: false),
      RegExp(r'debited.*?to ([\w\s@.-]+?)(?:\s|$|\()', caseSensitive: false),
      RegExp(r'paid.*?at ([\w\s@.-]+?)(?:\s|$|\()', caseSensitive: false),
      RegExp(r'payment.*?to ([\w\s@.-]+?)(?:\s|$|\()', caseSensitive: false),
    ];
    
    for (final pattern in specificVendorPatterns) {
      final match = pattern.firstMatch(smsText);
      if (match != null) {
        String extractedVendor = match.group(1)?.trim() ?? '';
        if (extractedVendor.isNotEmpty && extractedVendor.length > 2) {
          // Clean up vendor name - remove account numbers and common prefixes
          extractedVendor = extractedVendor.replaceAll(RegExp(r'\*+\d+'), '');
          extractedVendor = extractedVendor.replaceAll(RegExp(r'A/C\s*\d+', caseSensitive: false), '');
          
          // Format vendor name properly (capitalize first letter of each word)
          List<String> words = extractedVendor.split(' ');
          words = words.map((word) {
            if (word.isNotEmpty) {
              return word[0].toUpperCase() + (word.length > 1 ? word.substring(1).toLowerCase() : '');
            }
            return word;
          }).toList();
          
          vendor = words.join(' ');
          vendor = vendor.replaceAll(RegExp(r'[^\w\s@.-]'), '').trim();
          vendor = vendor.replaceAll(RegExp(r'\s+'), ' ').trim();
          
          // Limit vendor name length but ensure it's meaningful
          if (vendor.length > 25) vendor = vendor.substring(0, 25);
          break;
        }
      }
    }
    
    // If no specific vendor found, extract from bank name, sender, or transaction type
    if (vendor == 'Unknown' || vendor.length < 3) {
      if (smsText.contains('CANBNK') || smsText.contains('Canara')) vendor = 'Canara Bank Transfer';
      else if (smsText.contains('TDCBNK') || smsText.contains('TD Bank')) vendor = 'TD Bank';
      else if (smsText.contains('ICICI')) vendor = 'ICICI Bank';
      else if (smsText.contains('HDFC')) vendor = 'HDFC Bank';
      else if (smsText.contains('IDFCFB')) vendor = 'IDFC First Bank';
      else if (smsText.contains('SBI')) vendor = 'State Bank';
      else if (smsText.contains('AXIS')) vendor = 'Axis Bank';
      else if (smsText.contains('KOTAK')) vendor = 'Kotak Bank';
      else if (smsText.contains('AVANSE')) vendor = 'Avanse Education Loan';
      else if (smsText.contains('PAYTM')) vendor = 'Paytm';
      else if (smsText.contains('GPAY')) vendor = 'Google Pay';
      else if (smsText.contains('PHONEPE')) vendor = 'PhonePe';
      else if (smsText.contains('JIOPAY') || smsText.contains('Jio')) vendor = 'Jio Recharge';
      else if (smsText.contains('AMAZON') || smsText.contains('Amazon')) vendor = 'Amazon';
      else if (smsText.contains('UPI')) vendor = 'UPI Transfer';
      else if (smsText.contains('ATM')) vendor = 'ATM Withdrawal';
      else if (smsText.contains('Cheque')) vendor = 'Cheque Payment';
      else if (smsText.contains('mandate')) vendor = 'Auto Debit';
      else vendor = 'Bank Transaction';
    }

    // Determine transaction type
    String transactionType = 'debit';
    if (smsText.toLowerCase().contains('credited') || 
        smsText.toLowerCase().contains('received') ||
        smsText.toLowerCase().contains('refund')) {
      transactionType = 'credit';
    }

    // Smart category detection
    String category = _detectCategoryStatic(smsText, vendor);

    // Extract date (use current date if not found)
    String date = DateTime.now().toIso8601String();
    final datePattern = RegExp(r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})');
    final dateMatch = datePattern.firstMatch(smsText);
    if (dateMatch != null) {
      try {
        final dateStr = dateMatch.group(1) ?? '';
        final parts = dateStr.split(RegExp(r'[-/]'));
        if (parts.length == 3) {
          int day = int.parse(parts[0]);
          int month = int.parse(parts[1]);
          int year = int.parse(parts[2]);
          if (year < 100) year += 2000;
          date = DateTime(year, month, day).toIso8601String();
        }
      } catch (e) {
        // Keep current date if parsing fails
      }
    }

    if (amount == null || amount <= 0) return null;

    return Transaction(
      id: uuidStatic.v4(), // Add unique ID
      vendor: vendor,
      amount: amount,
      date: date,
      category: category,
      smsText: smsText,  // Updated field name
      confidence: 0.85,
    );
  } catch (e) {
    debugPrint('Error creating transaction from SMS: $e');
    return null;
  }
}

// Static category detection for background processing
String _detectCategoryStatic(String smsText, String vendor) {
  final text = smsText.toLowerCase();
  final vendorLower = vendor.toLowerCase();

  // Food & Dining
  if (text.contains('swiggy') || text.contains('zomato') || 
      text.contains('restaurant') || text.contains('food') ||
      text.contains('cafe') || text.contains('hotel')) {
    return 'Food & Dining';
  }

  // Transportation
  if (text.contains('uber') || text.contains('ola') || 
      text.contains('metro') || text.contains('bus') ||
      text.contains('taxi') || text.contains('petrol') ||
      text.contains('fuel')) {
    return 'Transportation';
  }

  // Shopping
  if (text.contains('amazon') || text.contains('flipkart') || 
      text.contains('myntra') || text.contains('shopping') ||
      text.contains('purchase') || vendorLower.contains('store')) {
    return 'Shopping';
  }

  // Utilities
  if (text.contains('electricity') || text.contains('water') || 
      text.contains('gas') || text.contains('internet') ||
      text.contains('mobile') || text.contains('recharge') ||
      text.contains('jio') || text.contains('airtel')) {
    return 'Utilities';
  }

  // Healthcare
  if (text.contains('hospital') || text.contains('medical') || 
      text.contains('pharmacy') || text.contains('doctor') ||
      text.contains('clinic')) {
    return 'Healthcare';
  }

  // Financial
  if (text.contains('bank') || text.contains('loan') || 
      text.contains('emi') || text.contains('interest') ||
      text.contains('fee') || text.contains('charge')) {
    return 'Financial';
  }

  // Education
  if (text.contains('school') || text.contains('college') || 
      text.contains('university') || text.contains('course') ||
      text.contains('tuition') || text.contains('education')) {
    return 'Education';
  }

  // Entertainment
  if (text.contains('movie') || text.contains('netflix') || 
      text.contains('spotify') || text.contains('game') ||
      text.contains('entertainment')) {
    return 'Entertainment';
  }

  return 'Others';
}
