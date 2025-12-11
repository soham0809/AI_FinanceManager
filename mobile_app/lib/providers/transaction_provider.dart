import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import '../models/transaction.dart';
import '../services/api_service.dart';
import '../services/sms_filter_service.dart';
import 'package:uuid/uuid.dart';

class TransactionProvider with ChangeNotifier {
  final ApiService apiService;
  
  TransactionProvider(this.apiService) {
    _transactions.clear(); // Clear the list instead of reassigning
  }
  
  final List<Transaction> _transactions = [];
  final Uuid _uuid = Uuid(); // Initialize Uuid
  bool _isLoading = false;
  String? _error;
  bool _isConnected = false;

  List<Transaction> get transactions => _transactions;
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get isConnected => _isConnected;

  // Add transaction directly to the list and save to backend
  Future<void> addTransaction(Transaction transaction) async {
    // Generate a unique ID for the transaction if it doesn't have one
    final transactionWithId = (transaction.id == null || transaction.id!.isEmpty) ? transaction.copyWith(id: _uuid.v4()) : transaction;

    final isDuplicate = _isTransactionDuplicate(transactionWithId);

    if (!isDuplicate) {
      try {
        // Save to backend first
        await apiService.saveTransaction(transactionWithId);
        
        // Then add to local list
        _transactions.insert(0, transactionWithId); // Insert at beginning for newest first
        notifyListeners();
        debugPrint('Added transaction: ${transactionWithId.vendor} - Rs.${transactionWithId.amount}');
      } catch (e) {
        debugPrint('Error saving transaction to backend: $e');
        // Still add to local list even if backend save fails
        _transactions.insert(0, transactionWithId);
        notifyListeners();
      }
    } else {
      debugPrint('Duplicate transaction detected and skipped: ${transactionWithId.vendor} - Rs.${transactionWithId.amount}');
    }
  }

  // Add multiple transactions efficiently and save to backend
  Future<void> addTransactionsBatch(List<Transaction> transactions) async {
    bool hasNewTransactions = false;
    int duplicatesSkipped = 0;
    
    for (final transaction in transactions) {
      // Generate a unique ID for the transaction if it doesn't have one
      final transactionWithId = (transaction.id == null || transaction.id!.isEmpty) ? transaction.copyWith(id: _uuid.v4()) : transaction;

      final isDuplicate = _isTransactionDuplicate(transactionWithId);

      if (!isDuplicate) {
        try {
          // Save to backend
          await apiService.saveTransaction(transactionWithId);
        } catch (e) {
          debugPrint('Error saving transaction to backend: $e');
          // Continue with other transactions even if one fails
        }
        
        _transactions.insert(0, transactionWithId);
        hasNewTransactions = true;
      } else {
        duplicatesSkipped++;
      }
    }
    
    if (duplicatesSkipped > 0) {
      debugPrint('Skipped $duplicatesSkipped duplicate transactions in batch');
    }
    
    if (hasNewTransactions) {
      notifyListeners();
    }
  }

  // Clear all transactions
  void clearTransactions() {
    _transactions.clear();
    notifyListeners();
  }

  // Delete a single transaction locally and on backend (if possible)
  Future<void> deleteTransaction(Transaction t) async {
    try {
      if (t.id != null && t.id!.isNotEmpty) {
        await apiService.deleteTransaction(t.id!); // Persist delete on server
      }
    } catch (e) {
      debugPrint('deleteTransaction backend error: $e');
    }
    // Remove locally regardless to keep UI responsive
    _transactions.removeWhere((x) => x.id == t.id || (x.vendor == t.vendor && x.amount == t.amount && x.date == t.date));
    notifyListeners();
    // Resync from server to avoid stale data
    try {
      await fetchTransactions();
    } catch (_) {}
  }

  // Check server connection
  Future<void> checkConnection() async {
    _isLoading = true;
    _error = null;
    // Don't notify listeners immediately to avoid build phase conflicts
    
    try {
      final healthData = await apiService.healthCheck();
      _isConnected = healthData['status'] == 'healthy';
      
      if (_isConnected) {
        await fetchTransactions();
      }
    } catch (e) {
      _error = e.toString();
      _isConnected = false;
    } finally {
      _isLoading = false;
      // Only notify listeners once at the end
      notifyListeners();
    }
  }

  // Fetch all transactions from server
  Future<void> fetchTransactions() async {
    _isLoading = true;
    _error = null;
    // Don't notify listeners immediately to avoid build phase conflicts
    
    try {
      final fetchedTransactions = await apiService.getTransactions();
      _transactions.clear(); // Clear existing transactions
      _transactions.addAll(fetchedTransactions); // Add all fetched transactions
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      // Only notify listeners once at the end
      notifyListeners();
    }
  }

  // Parse SMS and add transaction with smart filtering
  Future<Map<String, dynamic>> parseSms(String smsText, {bool useLocal = false, String? senderName}) async {
    _isLoading = true;
    _error = null;
    // Don't notify listeners immediately to avoid build phase conflicts
    
    try {
      // First, analyze the SMS to check if it's a valid transaction
      final recentSmsTexts = _transactions.take(10).map((t) => t.smsText).toList();
      final analysis = SMSFilterService.analyzeWithContext(
        smsText,
        senderName: senderName,
        timestamp: DateTime.now(),
        recentTransactions: recentSmsTexts,
      );

      debugPrint('SMS Analysis: $analysis');

      // If it's not a valid transaction, return early with explanation
      if (!analysis.isValidTransaction) {
        final response = {
          'success': false,
          'filtered': true,
          'filter_reason': analysis.filterReason.description,
          'confidence': analysis.confidence,
          'message': 'SMS filtered out: ${analysis.filterReason.description}',
          'detected_keywords': analysis.detectedKeywords,
        };
        
        debugPrint('SMS filtered out: ${analysis.filterReason.description}');
        return response;
      }

      // If confidence is very low, add a warning but still process
      if (analysis.confidence < 0.4) {
        debugPrint('Low confidence SMS (${(analysis.confidence * 100).toStringAsFixed(1)}%) - processing with caution');
      }

      final response = await apiService.parseSms(smsText, useLocal: useLocal);
      
      if (response['success'] == true) {
        final transaction = Transaction(
          // Use backend id so deletes can be persisted
          id: (response['id']?.toString()),
          vendor: response['vendor'],
          amount: response['amount'].toDouble(),
          date: response['date'],
          category: response['category'],
          smsText: smsText,  // Updated field name
          confidence: response['confidence']?.toDouble() ?? 0.0,
        );
        // Insert locally (already persisted by backend parse endpoint)
        _transactions.insert(0, transaction);
        
        // Add analysis metadata to response
        response['sms_analysis'] = {
          'filter_confidence': analysis.confidence,
          'filter_reason': analysis.filterReason.description,
          'detected_keywords': analysis.detectedKeywords,
        };
      }
      
      return response;
    } catch (e) {
      _error = e.toString();
      return {'success': false, 'error': e.toString()};
    } finally {
      _isLoading = false;
      // Only notify listeners once at the end
      notifyListeners();
    }
  }

  // Legacy method for compatibility
  Future<void> parseSMSAndAddTransaction(String smsText, {bool useLocal = false}) async {
    await parseSms(smsText, useLocal: useLocal);
  }

  // Get total spending
  double get totalSpending {
    return _transactions
        .where((t) => t.isDebit)
        .fold(0.0, (sum, t) => sum + t.amount);
  }

  // Get total income
  double get totalIncome {
    return _transactions
        .where((t) => t.isCredit)
        .fold(0.0, (sum, t) => sum + t.amount);
  }

  // Get spending by category (offline analytics)
  Map<String, double> get spendingByCategory {
    final Map<String, double> categorySpending = {};
    for (final transaction in _transactions.where((t) => t.isDebit)) {
      final category = transaction.category ?? 'Others';
      categorySpending[category] = 
          (categorySpending[category] ?? 0.0) + transaction.amount;
    }
    return categorySpending;
  }

  // Get recent transactions (last 30 days)
  List<Transaction> get recentTransactions {
    final thirtyDaysAgo = DateTime.now().subtract(Duration(days: 30));
    return _transactions.where((t) {
      try {
        final transactionDate = DateTime.parse(t.date);
        return transactionDate.isAfter(thirtyDaysAgo);
      } catch (e) {
        return true; // Include if date parsing fails
      }
    }).toList();
  }

  // Get top spending categories
  List<MapEntry<String, double>> get topSpendingCategories {
    final categorySpending = spendingByCategory;
    final sortedCategories = categorySpending.entries.toList()
      ..sort((a, b) => b.value.compareTo(a.value));
    return sortedCategories.take(5).toList();
  }

  // Get spending trend (daily average)
  double get dailyAverageSpending {
    final recentDebits = recentTransactions.where((t) => t.isDebit);
    if (recentDebits.isEmpty) return 0.0;
    
    final totalSpent = recentDebits.fold(0.0, (sum, t) => sum + t.amount);
    return totalSpent / 30; // 30-day average
  }

  // Generate offline insights
  List<String> get offlineInsights {
    final insights = <String>[];
    final categorySpending = spendingByCategory;
    final totalSpent = totalSpending;
    final dailyAvg = dailyAverageSpending;

    if (totalSpent > 0) {
      insights.add('💰 Total spending: ₹${totalSpent.toStringAsFixed(2)}');
      insights.add('📊 Daily average: ₹${dailyAvg.toStringAsFixed(2)}');
      
      if (categorySpending.isNotEmpty) {
        final topCategory = categorySpending.entries
            .reduce((a, b) => a.value > b.value ? a : b);
        insights.add('🏆 Top category: ${topCategory.key} (₹${topCategory.value.toStringAsFixed(2)})');
      }

      // Smart insights based on spending patterns
      if (categorySpending['Food & Dining'] != null && 
          categorySpending['Food & Dining']! > totalSpent * 0.3) {
        insights.add('🍽️ High food spending detected - consider meal planning');
      }

      if (categorySpending['Transportation'] != null && 
          categorySpending['Transportation']! > totalSpent * 0.25) {
        insights.add('🚗 Transportation costs are significant - explore alternatives');
      }

      if (categorySpending['Education'] != null) {
        insights.add('📚 Education investments: ₹${categorySpending['Education']!.toStringAsFixed(2)}');
      }

      if (totalIncome > totalSpent) {
        final savings = totalIncome - totalSpent;
        insights.add('💚 Positive balance: ₹${savings.toStringAsFixed(2)} saved');
      } else if (totalSpent > totalIncome) {
        insights.add('⚠️ Spending exceeds income - review budget');
      }
    }

    return insights.isEmpty ? ['📱 Scan SMS to generate insights'] : insights;
  }

  // Get transactions by category
  Map<String, List<Transaction>> get transactionsByCategory {
    final Map<String, List<Transaction>> categorized = {};
    
    for (final transaction in _transactions) {
      final category = transaction.category ?? 'Uncategorized';
      categorized.putIfAbsent(category, () => []);
      categorized[category]!.add(transaction);
    }
    
    return categorized;
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }

  // Enhanced duplicate detection method
  bool _isTransactionDuplicate(Transaction newTransaction) {
    return _transactions.any((existing) {
      // Check for exact ID match first
      if (existing.id == newTransaction.id && 
          existing.id != null && 
          existing.id!.isNotEmpty) {
        return true;
      }

      // Check for same amount and vendor
      if (existing.amount == newTransaction.amount &&
          existing.vendor.toLowerCase() == newTransaction.vendor.toLowerCase()) {
        
        try {
          // Parse dates for time comparison
          final existingDate = existing.parsedDate;
          final newDate = newTransaction.parsedDate;
          
          // Check if dates are within 1 minute of each other
          final timeDifference = existingDate.difference(newDate).abs();
          if (timeDifference.inMinutes <= 1) {
            return true;
          }
          
          // Also check if they're on the same day (fallback for date-only transactions)
          if (existingDate.year == newDate.year &&
              existingDate.month == newDate.month &&
              existingDate.day == newDate.day) {
            return true;
          }
        } catch (e) {
          // If date parsing fails, fall back to string comparison
          debugPrint('Date parsing failed in duplicate detection: $e');
          if (existing.date.substring(0, 10) == newTransaction.date.substring(0, 10)) {
            return true;
          }
        }
      }

      return false;
    });
  }

  // Method to remove duplicate transactions from existing list
  void removeDuplicateTransactions() {
    final uniqueTransactions = <Transaction>[];
    final seenTransactions = <String, Transaction>{};

    for (final transaction in _transactions) {
      final key = '${transaction.amount}_${transaction.vendor.toLowerCase()}_${transaction.date.substring(0, 10)}';
      
      if (!seenTransactions.containsKey(key)) {
        seenTransactions[key] = transaction;
        uniqueTransactions.add(transaction);
      } else {
        // Check if this transaction has a more complete date/time
        final existing = seenTransactions[key]!;
        try {
          final existingDate = existing.parsedDate;
          final currentDate = transaction.parsedDate;
          
          // Keep the one with more recent or complete information
          if (currentDate.isAfter(existingDate) || 
              (transaction.upiTransactionId != null && existing.upiTransactionId == null)) {
            seenTransactions[key] = transaction;
            final index = uniqueTransactions.indexOf(existing);
            if (index != -1) {
              uniqueTransactions[index] = transaction;
            }
          }
        } catch (e) {
          // Keep the first one if date parsing fails
          debugPrint('Date comparison failed in duplicate removal: $e');
        }
      }
    }

    final removedCount = _transactions.length - uniqueTransactions.length;
    if (removedCount > 0) {
      _transactions.clear();
      _transactions.addAll(uniqueTransactions);
      notifyListeners();
      debugPrint('Removed $removedCount duplicate transactions');
    }
  }
}
