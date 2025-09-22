import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/transaction.dart';
import 'dart:io';

class ApiService {
  // Configuration for different environments
  // Android Emulator: 10.0.2.2:8000
  // iOS Simulator: localhost:8000 or 127.0.0.1:8000
  // Physical Device: Your computer's IP address (e.g., 192.168.1.100:8000)
  // Web/Desktop: localhost:8000
  
  static String get baseUrl {
    // Configuration based on your setup:
    // - Android Emulator: 10.0.2.2:8000
    // - Physical Device: 192.168.0.105:8000 (your computer's IP)
    // - iOS Simulator: localhost:8000
    
    if (Platform.isAndroid) {
      // For physical Android device, use your computer's actual IP
      // For Android emulator, use 'http://10.0.2.2:8000'
      return 'http://192.168.0.105:8000';  // Your computer's correct IP for physical device
    } else if (Platform.isIOS) {
      // For iOS simulator
      return 'http://localhost:8000';
    } else {
      // For web/desktop
      return 'http://localhost:8000';
    }
  }

  static const bool offlineMode = false; // Set to true for offline testing
  // Health check endpoint
  Future<Map<String, dynamic>> healthCheck() async {
    print('🔍 Attempting to connect to: $baseUrl/health');
    print('🔍 Platform: ${Platform.operatingSystem}');
    
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/health'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(Duration(seconds: 10));

      print('🔍 Response status: ${response.statusCode}');
      
      if (response.statusCode == 200) {
        print('✅ Health check successful');
        return json.decode(response.body);
      } else {
        print('❌ Error response body: ${response.body}');
        throw Exception('Health check failed: ${response.statusCode}');
      }
    } catch (e) {
      print('❌ Network error in healthCheck: $e');
      print('🔍 Trying alternative URLs...');
      
      // Try alternative URLs for physical device
      final alternativeUrls = [
        'http://192.168.0.105:8000', // Your computer's actual IP
        'http://192.168.0.102:8000', // Previous IP that was being used
        'http://10.0.2.2:8000',      // For emulator
        'http://localhost:8000',     // Local testing
        'http://127.0.0.1:8000',     // Alternative localhost
      ];
      
      for (String altUrl in alternativeUrls) {
        if (altUrl != baseUrl) {
          try {
            print('🔍 Trying: $altUrl/health');
            final altResponse = await http.get(
              Uri.parse('$altUrl/health'),
              headers: {'Content-Type': 'application/json'},
            ).timeout(Duration(seconds: 5));
            
            if (altResponse.statusCode == 200) {
              print('✅ Alternative URL works: $altUrl');
              return json.decode(altResponse.body);
            }
          } catch (altError) {
            print('❌ Alternative URL failed: $altUrl - $altError');
          }
        }
      }
      
      throw Exception('Failed to connect to server: $e');
    }
  }

  // Parse SMS and extract transaction data
  Future<Map<String, dynamic>> parseSms(String smsText) async {
    if (offlineMode) {
      // Return mock data for offline testing
      await Future.delayed(Duration(milliseconds: 500)); // Simulate network delay
      return {
        'success': true,
        'vendor': 'Test Vendor',
        'amount': 150.0,
        'date': DateTime.now().toIso8601String(),
        'transaction_type': 'debit',
        'category': 'Food & Dining',
        'confidence': 0.95,
      };
    }
    
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/v1/parse-sms'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'sms_text': smsText}),
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        print('Error response body: ${response.body}'); // Add this line
        throw Exception('Failed to parse SMS: ${response.statusCode}');
      }
    } catch (e) {
      print('Network error in parseSms: $e'); // Add this line
      throw Exception('Network error: $e');
    }
  }

  // Get all transactions
  Future<List<Transaction>> getTransactions() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/v1/transactions'));
      print('✅ getTransactions response status: ${response.statusCode}');
      
      if (response.statusCode == 200) {
        final List<dynamic> transactionsJson = json.decode(response.body);
        print('✅ Successfully parsed ${transactionsJson.length} transactions');
        
        return transactionsJson
            .map((json) => Transaction.fromJson(json))
            .toList();
      } else {
        print('❌ Error response body: ${response.body}');
        throw Exception('Failed to load transactions: ${response.statusCode}');
      }
    } catch (e) {
      print('❌ Network error in getTransactions: $e');
      throw Exception('Network error: $e');
    }
  }
  
  // Save a transaction to the backend
  Future<Map<String, dynamic>> saveTransaction(Transaction transaction) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/v1/transactions'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(transaction.toJson()),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        return json.decode(response.body);
      } else {
        print('Error response body: ${response.body}'); // Add this line
        throw Exception('Failed to save transaction: ${response.statusCode}');
      }
    } catch (e) {
      print('Network error in saveTransaction: $e'); // Add this line
      throw Exception('Network error: $e');
    }
  }

  Future<Map<String, dynamic>> categorizeVendor(String vendor) async {
    try {
      final response = await http.post(
        Uri.parse(
            '$baseUrl/v1/categorize?vendor=${Uri.encodeComponent(vendor)}'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        print('Error response body: ${response.body}'); // Add this line
        throw Exception('Failed to categorize vendor: ${response.statusCode}');
      }
    } catch (e) {
      print('Network error in categorizeVendor: $e'); // Add this line
      throw Exception('Network error: $e');
    }
  }

  Future<Map<String, dynamic>> getMLModelInfo() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/v1/ml-info'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        print('Error response body: ${response.body}'); // Add this line
        throw Exception('Failed to get ML model info: ${response.statusCode}');
      }
    } catch (e) {
      print('Network error in getMLModelInfo: $e'); // Add this line
      throw Exception('Network error: $e');
    }
  }

  // Analytics endpoints
  Future<Map<String, dynamic>> getSpendingByCategory() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/v1/analytics/spending-by-category'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        print('Error response body: ${response.body}'); // Add this line
        throw Exception(
            'Failed to get category spending: ${response.statusCode}');
      }
    } catch (e) {
      print('Network error: $e'); // Add this line
      throw Exception('Network error: $e');
    }
  }

  Future<Map<String, dynamic>> getMonthlyTrends() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/v1/analytics/monthly-trends'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        print('Error response body: ${response.body}'); // Add this line
        throw Exception('Failed to get monthly trends: ${response.statusCode}');
      }
    } catch (e) {
      print('Network error: $e'); // Add this line
      throw Exception('Network error: $e');
    }
  }

  Future<Map<String, dynamic>> getSpendingInsights() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/v1/analytics/insights'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        print('Error response body: ${response.body}'); // Add this line
        throw Exception(
            'Failed to get spending insights: ${response.statusCode}');
      }
    } catch (e) {
      print('Network error: $e'); // Add this line
      throw Exception('Network error: $e');
    }
  }

  Future<Map<String, dynamic>> getTopVendors({int limit = 10}) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/v1/analytics/top-vendors?limit=$limit'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        print('Error response body: ${response.body}'); // Add this line
        throw Exception('Failed to get top vendors: ${response.statusCode}');
      }
    } catch (e) {
      print('Network error: $e'); // Add this line
      throw Exception('Network error: $e');
    }
  }

  // Predictive Analytics endpoints
  Future<Map<String, dynamic>> trainPredictionModels() async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/v1/predictions/train-models'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        print('Error response body: ${response.body}'); // Add this line
        throw Exception('Failed to train models: ${response.statusCode}');
      }
    } catch (e) {
      print('Network error: $e'); // Add this line
      throw Exception('Network error: $e');
    }
  }

  Future<Map<String, dynamic>> getSpendingForecast({String? category}) async {
    try {
      String url = '$baseUrl/v1/predictions/spending-forecast';
      if (category != null) {
        url += '?category=${Uri.encodeComponent(category)}';
      }

      final response = await http.get(
        Uri.parse(url),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        print('Error response body: ${response.body}'); // Add this line
        throw Exception(
            'Failed to get spending forecast: ${response.statusCode}');
      }
    } catch (e) {
      print('Network error: $e'); // Add this line
      throw Exception('Network error: $e');
    }
  }

  Future<Map<String, dynamic>> createSavingsGoal({
    required double targetAmount,
    required int targetMonths,
    required double currentIncome,
    required double currentExpenses,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/v1/predictions/savings-goal'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'target_amount': targetAmount,
          'target_months': targetMonths,
          'current_income': currentIncome,
          'current_expenses': currentExpenses,
        }),
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        print('Error response body: ${response.body}'); // Add this line
        throw Exception(
            'Failed to create savings goal: ${response.statusCode}');
      }
    } catch (e) {
      print('Network error: $e'); // Add this line
      throw Exception('Network error: $e');
    }
  }

  Future<Map<String, dynamic>> getBudgetAlerts(
      Map<String, double> budgetLimits) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/v1/predictions/budget-alerts'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'limits': budgetLimits}),
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        print('Error response body: ${response.body}'); // Add this line
        throw Exception('Failed to get budget alerts: ${response.statusCode}');
      }
    } catch (e) {
      print('Network error: $e'); // Add this line
      throw Exception('Network error: $e');
    }
  }

  Future<Map<String, dynamic>> getFinancialInsights() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/v1/predictions/financial-insights'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        print('Error response body: ${response.body}'); // Add this line
        throw Exception(
            'Failed to get financial insights: ${response.statusCode}');
      }
    } catch (e) {
      print('Network error: $e'); // Add this line
      throw Exception('Network error: $e');
    }
  }

  // Generic analytics method for flexible API calls
  Future<Map<String, dynamic>> getAnalytics(String endpoint) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl$endpoint'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        print('Error response body: ${response.body}'); // Add this line
        throw Exception('Failed to get analytics: ${response.statusCode}');
      }
    } catch (e) {
      print('Network error: $e'); // Add this line
      throw Exception('Network error: $e');
    }
  }

  // Monthly tracking endpoints
  Future<Map<String, dynamic>> getMonthlySummary({int? year, int? month}) async {
    try {
      String url = '$baseUrl/v1/monthly/summary';
      List<String> params = [];
      if (year != null) params.add('year=$year');
      if (month != null) params.add('month=$month');
      if (params.isNotEmpty) url += '?${params.join('&')}';

      final response = await http.get(
        Uri.parse(url),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        print('Error response body: ${response.body}'); // Add this line
        throw Exception('Failed to get monthly summary: ${response.statusCode}');
      }
    } catch (e) {
      print('Network error: $e'); // Add this line
      throw Exception('Network error: $e');
    }
  }

  Future<Map<String, dynamic>> getYearlyOverview({int? year}) async {
    try {
      String url = '$baseUrl/v1/monthly/yearly-overview';
      if (year != null) url += '?year=$year';

      final response = await http.get(
        Uri.parse(url),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        print('Error response body: ${response.body}'); // Add this line
        throw Exception('Failed to get yearly overview: ${response.statusCode}');
      }
    } catch (e) {
      print('Network error: $e'); // Add this line
      throw Exception('Network error: $e');
    }
  }
}
