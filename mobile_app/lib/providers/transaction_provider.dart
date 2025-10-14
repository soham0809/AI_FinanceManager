import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import '../models/transaction.dart';
import '../services/api_service.dart';
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

    final isDuplicate = _transactions.any((existing) =>
        existing.id == transactionWithId.id || // Check for duplicate ID
        (existing.amount == transactionWithId.amount &&
            existing.vendor == transactionWithId.vendor &&
            existing.date.substring(0, 10) == transactionWithId.date.substring(0, 10)));

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
    }
  }

  // Add multiple transactions efficiently and save to backend
  Future<void> addTransactionsBatch(List<Transaction> transactions) async {
    bool hasNewTransactions = false;
    for (final transaction in transactions) {
      // Generate a unique ID for the transaction if it doesn't have one
      final transactionWithId = (transaction.id == null || transaction.id!.isEmpty) ? transaction.copyWith(id: _uuid.v4()) : transaction;

      final isDuplicate = _transactions.any((existing) =>
          existing.id == transactionWithId.id || // Check for duplicate ID
          (existing.amount == transactionWithId.amount &&
              existing.vendor == transactionWithId.vendor &&
              existing.date.substring(0, 10) == transactionWithId.date.substring(0, 10)));

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
      }
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

  // Parse SMS and add transaction
  Future<Map<String, dynamic>> parseSms(String smsText) async {
    _isLoading = true;
    _error = null;
    // Don't notify listeners immediately to avoid build phase conflicts
    
    try {

      final response = await apiService.parseSms(smsText);
      
      if (response['success'] == true) {
        final transaction = Transaction(
          id: _uuid.v4(), // Generate a new ID here
          success: true,
          vendor: response['vendor'],
          amount: response['amount'].toDouble(),
          date: response['date'],
          transactionType: response['transaction_type'],
          category: response['category'],
          rawText: smsText,
          confidence: response['confidence']?.toDouble() ?? 0.0,
        );
        
        // Save to backend
        try {
          await apiService.saveTransaction(transaction);
        } catch (e) {
          debugPrint('Error saving parsed transaction to backend: $e');
          // Continue even if backend save fails
        }
        
        _transactions.insert(0, transaction);
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
  Future<void> parseSMSAndAddTransaction(String smsText) async {
    await parseSms(smsText);
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
}
