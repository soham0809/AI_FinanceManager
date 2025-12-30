import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/transaction.dart';
import 'dart:io';
import '../config/network_config.dart';
import 'auth_service.dart';

class ApiService {
  // 🌐 Using central network configuration
  static String get baseUrl => NetworkConfig.baseUrl;

  static const bool offlineMode = false; // Set to false to use the backend server
  // Health check endpoint
  Future<Map<String, dynamic>> healthCheck() async {
    print('🔍 Attempting to connect to: $baseUrl/health');
    print('🔍 Platform: ${Platform.operatingSystem}');
    
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/health'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(Duration(seconds: 15));

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
      
      // Only use Cloudflare URL - no fallback to localhost
      final alternativeUrls = [
        'https://ai-finance.sohamm.xyz', // Primary Cloudflare URL
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
  Future<Map<String, dynamic>> parseSms(String smsText, {bool useLocal = false}) async {
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
    
    // Require authentication
    if (!AuthService.isLoggedIn || AuthService.accessToken == null) {
      throw Exception('Authentication required. Please log in to parse SMS messages.');
    }
    
    try {
      // Decide endpoint based on parsing mode
      final String endpoint = useLocal ? '/v1/parse-sms-local' : '/v1/parse-sms';

      print('🔐 Using ${useLocal ? 'LOCAL' : 'LLM'} authenticated SMS parsing endpoint');
      final response = await http.post(
        Uri.parse('$baseUrl$endpoint'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ${AuthService.accessToken}',
        },
        body: json.encode({'sms_text': smsText}),
      ).timeout(Duration(seconds: 180));  // 3 minutes for LLM parsing
      
      if (response.statusCode == 200) {
        print('✅ Authenticated ${useLocal ? 'LOCAL' : 'LLM'} SMS parsing successful');
        return json.decode(response.body);
      } else if (response.statusCode == 401) {
        // Token expired, try to refresh
        await AuthService.refreshToken();
        // Retry with new token
        return await parseSms(smsText, useLocal: useLocal);
      } else {
        print('Error response body: ${response.body}');
        throw Exception('Failed to parse SMS: ${response.statusCode}');
      }
    } catch (e) {
      print('Network error in parseSms: $e');
      throw Exception('Network error: $e');
    }
  }

  /// NEW: Parse SMS with full metadata for temporal-context aware parsing
  /// Sends sender address and device timestamp for fingerprint-based deduplication
  Future<Map<String, dynamic>> parseSmsWithMetadata(dynamic sms, {bool useLocal = true}) async {
    if (!AuthService.isLoggedIn || AuthService.accessToken == null) {
      throw Exception('Authentication required. Please log in to parse SMS messages.');
    }
    
    try {
      final String endpoint = useLocal ? '/v1/parse-sms-local' : '/v1/parse-sms';
      
      // Build request body with metadata
      final Map<String, dynamic> requestBody = sms is Map 
          ? sms as Map<String, dynamic> 
          : sms.toJson();
      
      print('🔐 Parsing SMS with metadata: sender=${requestBody['sender']}, timestamp=${requestBody['device_timestamp']}');
      
      final response = await http.post(
        Uri.parse('$baseUrl$endpoint'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ${AuthService.accessToken}',
        },
        body: json.encode(requestBody),
      ).timeout(Duration(seconds: 180));  // 3 minutes for LLM parsing
      
      if (response.statusCode == 200) {
        print('✅ SMS parsing with metadata successful');
        return json.decode(response.body);
      } else if (response.statusCode == 401) {
        await AuthService.refreshToken();
        return await parseSmsWithMetadata(sms, useLocal: useLocal);
      } else if (response.statusCode == 409) {
        // Duplicate detected by fingerprint
        print('⚠️ Duplicate SMS detected (fingerprint match)');
        throw Exception('Duplicate SMS - already processed');
      } else {
        print('Error response body: ${response.body}');
        throw Exception('Failed to parse SMS: ${response.statusCode}');
      }
    } catch (e) {
      print('Network error in parseSmsWithMetadata: $e');
      rethrow;
    }
  }

  // Get all transactions (user-specific if authenticated)
  Future<List<Transaction>> getTransactions() async {
    // Require authentication
    if (!AuthService.isLoggedIn || AuthService.accessToken == null) {
      throw Exception('Authentication required. Please log in to view transactions.');
    }
    
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/v1/transactions'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ${AuthService.accessToken}',
        },
      );
      print('✅ getTransactions response status: ${response.statusCode}');
      
      if (response.statusCode == 200) {
        final List<dynamic> transactionsJson = json.decode(response.body);
        print('✅ Successfully parsed ${transactionsJson.length} user-specific transactions');
        
        return transactionsJson
            .map((json) => Transaction.fromJson(json))
            .toList();
      } else if (response.statusCode == 401) {
        // Token expired, try to refresh
        print('🔄 Token expired, refreshing...');
        await AuthService.refreshToken();
        // Retry with new token
        return await getTransactions();
      } else {
        print('❌ Error response: ${response.statusCode}');
        print('❌ Error body: ${response.body}');
        throw Exception('Failed to load transactions: ${response.statusCode}');
      }
    } catch (e) {
      print('❌ Network error in getTransactions: $e');
      throw Exception('Network error: $e');
    }
  }
  
  // Delete a transaction (authenticated only)
  Future<void> deleteTransaction(String id) async {
    try {
      if (AuthService.isLoggedIn && AuthService.accessToken != null) {
        final resp = await http.delete(
          Uri.parse('$baseUrl/v1/transactions/$id'),
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ${AuthService.accessToken}',
          },
        ).timeout(Duration(seconds: 15));
        if (resp.statusCode == 200) {
          return;
        }
        if (resp.statusCode == 401) {
          await AuthService.refreshToken();
          return await deleteTransaction(id);
        }
        // Non-200: log and still remove locally
        print('❌ deleteTransaction failed: ${resp.statusCode} ${resp.body}');
      } else {
        print('⚠️ Not authenticated; skipping backend delete for id=$id');
      }
    } catch (e) {
      print('❌ Network error in deleteTransaction: $e');
    }
  }

  // Save a transaction to the backend
  Future<Map<String, dynamic>> saveTransaction(Transaction transaction) async {
    // Require authentication
    if (!AuthService.isLoggedIn || AuthService.accessToken == null) {
      throw Exception('Authentication required. Please log in to save transactions.');
    }
    
    try {
      final headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ${AuthService.accessToken}',
      };

      final response = await http.post(
        Uri.parse('$baseUrl/v1/transactions'),
        headers: headers,
        body: json.encode(transaction.toJson()),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        return json.decode(response.body);
      } else if (response.statusCode == 401) {
        // Try refresh token once
        await AuthService.refreshToken();
        final retryResponse = await http.post(
          Uri.parse('$baseUrl/v1/transactions'),
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ${AuthService.accessToken}',
          },
          body: json.encode(transaction.toJson()),
        );
        if (retryResponse.statusCode == 200 || retryResponse.statusCode == 201) {
          return json.decode(retryResponse.body);
        }
        print('❌ Authenticated save failed after refresh: ${retryResponse.statusCode}');
        throw Exception('Failed to save transaction after refresh: ${retryResponse.statusCode}');
      } else {
        print('Error response body: ${response.body}');
        throw Exception('Failed to save transaction: ${response.statusCode}');
      }
    } catch (e) {
      print('Network error in saveTransaction: $e');
      throw Exception('Network error: $e');
    }
  }

  // Quick batch SMS parsing (authenticated, background job)
  Future<Map<String, dynamic>> startParseSmsBatch(
    List<String> smsTexts, {
    int batchSize = 3,
    int delaySeconds = 3,
    bool useLocal = false,
  }) async {
    if (!(AuthService.isLoggedIn && AuthService.accessToken != null)) {
      throw Exception('Authentication required for batch parsing');
    }

    final headers = {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ${AuthService.accessToken}',
    };

    final body = json.encode({
      'sms_texts': smsTexts,
      'batch_size': batchSize,
      'delay_seconds': delaySeconds,
    });

    final String path = useLocal ? '/v1/quick/parse-sms-batch-local' : '/v1/quick/parse-sms-batch';
    
    print('🔐 Starting batch SMS parsing...');
    print('📍 URL: $baseUrl$path');
    print('📊 Total SMS: ${smsTexts.length}, Batch size: $batchSize, Delay: ${delaySeconds}s');
    print('🔧 Mode: ${useLocal ? "LOCAL" : "LLM"}');

    final resp = await http
        .post(Uri.parse('$baseUrl$path'), headers: headers, body: body)
        .timeout(Duration(seconds: 90));

    if (resp.statusCode == 200) {
      return json.decode(resp.body) as Map<String, dynamic>;
    }

    print('❌ startParseSmsBatch failed: ${resp.statusCode}');
    print('❌ Body: ${resp.body}');
    throw Exception('Failed to start batch parsing: ${resp.statusCode}');
  }

  /// NEW: Batch SMS parsing WITH METADATA for fingerprint-based deduplication
  /// Sends sender, deviceTimestamp, and body for each SMS
  Future<Map<String, dynamic>> startParseSmsBatchWithMetadata(
    List<dynamic> smsMessages, {  // List<SMSMessage> but dynamic for flexibility
    int batchSize = 10,
    int delaySeconds = 3,
    bool useLocal = false,
  }) async {
    if (!(AuthService.isLoggedIn && AuthService.accessToken != null)) {
      throw Exception('Authentication required for batch parsing');
    }

    final headers = {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ${AuthService.accessToken}',
    };

    // Convert SMSMessage objects to maps with metadata
    final List<Map<String, dynamic>> smsWithMetadata = smsMessages.map((sms) {
      if (sms is Map) {
        return sms as Map<String, dynamic>;
      }
      // Assume it has toJson() method (SMSMessage class)
      return {
        'sms_text': sms.body,
        'sender': sms.sender,
        'device_timestamp': sms.deviceTimestamp,
      };
    }).toList();

    final body = json.encode({
      'sms_messages': smsWithMetadata,  // NEW: Full metadata
      'batch_size': batchSize,
      'delay_seconds': delaySeconds,
    });

    final String path = useLocal ? '/v1/quick/parse-sms-batch-local' : '/v1/quick/parse-sms-batch';
    
    print('🔐 Starting batch SMS parsing WITH METADATA...');
    print('📍 URL: $baseUrl$path');
    print('📊 Total SMS: ${smsMessages.length}, Batch size: $batchSize, Delay: ${delaySeconds}s');
    print('🔧 Mode: ${useLocal ? "LOCAL" : "LLM"}');
    print('📱 Sample metadata: sender=${smsWithMetadata.isNotEmpty ? smsWithMetadata[0]['sender'] : 'N/A'}');

    final resp = await http
        .post(Uri.parse('$baseUrl$path'), headers: headers, body: body)
        .timeout(Duration(seconds: 90));

    if (resp.statusCode == 200) {
      return json.decode(resp.body) as Map<String, dynamic>;
    }

    print('❌ startParseSmsBatchWithMetadata failed: ${resp.statusCode}');
    print('❌ Body: ${resp.body}');
    throw Exception('Failed to start batch parsing with metadata: ${resp.statusCode}');
  }

  Future<Map<String, dynamic>> getQuickJobStatus(String jobId) async {
    final resp = await http
        .get(Uri.parse('$baseUrl/v1/quick/job-status/$jobId'), headers: {'Content-Type': 'application/json'})
        .timeout(Duration(seconds: 30));

    if (resp.statusCode == 200) {
      return json.decode(resp.body) as Map<String, dynamic>;
    }

    print('❌ getQuickJobStatus failed: ${resp.statusCode}');
    print('❌ Body: ${resp.body}');
    throw Exception('Failed to get job status: ${resp.statusCode}');
  }

  Future<Map<String, dynamic>> categorizeVendor(String vendor) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/v1/categorize?vendor=${Uri.encodeComponent(vendor)}'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final raw = json.decode(response.body) as Map<String, dynamic>;
        final cat = (raw['category'] ?? 'Others').toString();
        final conf = (raw['confidence'] is num) ? (raw['confidence'] as num).toDouble() : 0.5;
        // Normalize to the structure expected by MLCategorizationCard
        return {
          'predicted_category': cat,
          'confidence': conf,
          'all_probabilities': {cat: conf},
          'raw': raw,
        };
      } else {
        print('Error response body: ${response.body}');
        // Return a safe default instead of throwing to keep UI stable
        return {
          'predicted_category': 'Others',
          'confidence': 0.0,
          'all_probabilities': {'Others': 0.0},
          'error': 'HTTP ${response.statusCode}',
        };
      }
    } catch (e) {
      print('Network error in categorizeVendor: $e');
      return {
        'predicted_category': 'Others',
        'confidence': 0.0,
        'all_probabilities': {'Others': 0.0},
        'error': e.toString(),
      };
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
      // Use authenticated endpoint if logged in
      String endpoint = '/v1/analytics/spending-by-category';
      Map<String, String> headers = {'Content-Type': 'application/json'};
      
      if (AuthService.isLoggedIn && AuthService.accessToken != null) {
        headers['Authorization'] = 'Bearer ${AuthService.accessToken}';
        print('🔐 Using authenticated analytics endpoint');
      } else {
        endpoint = '/v1/analytics/spending-by-category-public';
        print('⚠️ Using public analytics endpoint - not user-isolated');
      }
      
      final response = await http.get(
        Uri.parse('$baseUrl$endpoint'),
        headers: headers,
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
    // Require authentication
    if (!AuthService.isLoggedIn || AuthService.accessToken == null) {
      throw Exception('Authentication required. Please log in to view analytics.');
    }
    
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/v1/analytics/monthly-trends'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ${AuthService.accessToken}',
        },
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else if (response.statusCode == 401) {
        await AuthService.refreshToken();
        return await getMonthlyTrends();
      } else {
        print('Error response body: ${response.body}');
        throw Exception('Failed to get monthly trends: ${response.statusCode}');
      }
    } catch (e) {
      print('Network error: $e');
      throw Exception('Network error: $e');
    }
  }

  Future<Map<String, dynamic>> getSpendingInsights() async {
    // Require authentication
    if (!AuthService.isLoggedIn || AuthService.accessToken == null) {
      throw Exception('Authentication required. Please log in to view analytics.');
    }
    
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/v1/analytics/insights'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ${AuthService.accessToken}',
        },
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else if (response.statusCode == 401) {
        await AuthService.refreshToken();
        return await getSpendingInsights();
      } else {
        print('Error response body: ${response.body}');
        throw Exception('Failed to get spending insights: ${response.statusCode}');
      }
    } catch (e) {
      print('Network error: $e');
      throw Exception('Network error: $e');
    }
  }

  Future<Map<String, dynamic>> getTopVendors({int limit = 10}) async {
    // Require authentication
    if (!AuthService.isLoggedIn || AuthService.accessToken == null) {
      throw Exception('Authentication required. Please log in to view analytics.');
    }
    
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/v1/analytics/top-vendors?limit=$limit'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ${AuthService.accessToken}',
        },
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else if (response.statusCode == 401) {
        await AuthService.refreshToken();
        return await getTopVendors(limit: limit);
      } else {
        print('Error response body: ${response.body}');
        throw Exception('Failed to get top vendors: ${response.statusCode}');
      }
    } catch (e) {
      print('Network error: $e');
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

  // Chatbot endpoints
  Future<Map<String, dynamic>> queryChatbot(String query, {int limit = 100}) async {
    // Require authentication
    if (!AuthService.isLoggedIn || AuthService.accessToken == null) {
      throw Exception('Authentication required. Please log in to use chatbot.');
    }
    
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/v1/chatbot/query'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ${AuthService.accessToken}',
        },
        body: json.encode({
          'query': query,
          'limit': limit,
        }),
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else if (response.statusCode == 401) {
        await AuthService.refreshToken();
        return await queryChatbot(query, limit: limit);
      } else {
        print('Error response body: ${response.body}');
        throw Exception('Failed to get chatbot response: ${response.statusCode}');
      }
    } catch (e) {
      print('Network error in queryChatbot: $e');
      throw Exception('Network error: $e');
    }
  }

  Future<Map<String, dynamic>> getQuickInsights() async {
    // Require authentication
    if (!AuthService.isLoggedIn || AuthService.accessToken == null) {
      throw Exception('Authentication required. Please log in to use chatbot.');
    }
    
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/v1/chatbot/quick-insights'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ${AuthService.accessToken}',
        },
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else if (response.statusCode == 401) {
        await AuthService.refreshToken();
        return await getQuickInsights();
      } else {
        print('Error response body: ${response.body}');
        throw Exception('Failed to get quick insights: ${response.statusCode}');
      }
    } catch (e) {
      print('Network error in getQuickInsights: $e');
      throw Exception('Network error: $e');
    }
  }

  Future<Map<String, dynamic>> getFinancialSummary({int days = 30}) async {
    // Require authentication
    if (!AuthService.isLoggedIn || AuthService.accessToken == null) {
      throw Exception('Authentication required. Please log in to use chatbot.');
    }
    
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/v1/chatbot/summary?days=$days'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ${AuthService.accessToken}',
        },
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else if (response.statusCode == 401) {
        await AuthService.refreshToken();
        return await getFinancialSummary(days: days);
      } else {
        print('Error response body: ${response.body}');
        throw Exception('Failed to get financial summary: ${response.statusCode}');
      }
    } catch (e) {
      print('Network error in getFinancialSummary: $e');
      throw Exception('Network error: $e');
    }
  }

  // Enhanced Chatbot with transaction context
  Future<Map<String, dynamic>> queryEnhancedChatbot(String query, {bool useCache = true, bool includeContext = true}) async {
    try {
      // Check if user is authenticated
      if (!AuthService.isLoggedIn || AuthService.accessToken == null) {
        throw Exception('Authentication required for enhanced chatbot');
      }

      print('🤖 Using enhanced chatbot with transaction context');
      final response = await http.post(
        Uri.parse('$baseUrl/v1/enhanced-chatbot/ask'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ${AuthService.accessToken}',
        },
        body: json.encode({
          'query': query,
          'use_cache': useCache,
          'include_context': includeContext,
        }),
      );

      if (response.statusCode == 200) {
        final result = json.decode(response.body);
        print('🤖 Enhanced chatbot response: cached=${result['cached']}, quality=${result['data_quality']['quality_score']}%');
        return result;
      } else {
        print('Error response body: ${response.body}');
        throw Exception('Failed to get enhanced chatbot response: ${response.statusCode}');
      }
    } catch (e) {
      print('Network error in queryEnhancedChatbot: $e');
      throw Exception('Network error: $e');
    }
  }

  // Get monthly spending data
  Future<Map<String, dynamic>> getMonthlySpending({int months = 6}) async {
    try {
      if (!AuthService.isLoggedIn || AuthService.accessToken == null) {
        throw Exception('Authentication required for monthly spending data');
      }

      final response = await http.get(
        Uri.parse('$baseUrl/v1/spending/monthly?months=$months'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ${AuthService.accessToken}',
        },
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        print('Error response body: ${response.body}');
        throw Exception('Failed to get monthly spending: ${response.statusCode}');
      }
    } catch (e) {
      print('Network error in getMonthlySpending: $e');
      throw Exception('Network error: $e');
    }
  }

  // Get weekly spending data
  Future<Map<String, dynamic>> getWeeklySpending({int weeks = 8}) async {
    try {
      if (!AuthService.isLoggedIn || AuthService.accessToken == null) {
        throw Exception('Authentication required for weekly spending data');
      }

      final response = await http.get(
        Uri.parse('$baseUrl/v1/spending/weekly?weeks=$weeks'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ${AuthService.accessToken}',
        },
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        print('Error response body: ${response.body}');
        throw Exception('Failed to get weekly spending: ${response.statusCode}');
      }
    } catch (e) {
      print('Network error in getWeeklySpending: $e');
      throw Exception('Network error: $e');
    }
  }

  // Get data quality report
  Future<Map<String, dynamic>> getDataQualityReport() async {
    try {
      if (!AuthService.isLoggedIn || AuthService.accessToken == null) {
        throw Exception('Authentication required for data quality report');
      }

      final response = await http.get(
        Uri.parse('$baseUrl/v1/enhanced-chatbot/data-quality'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ${AuthService.accessToken}',
        },
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        print('Error response body: ${response.body}');
        throw Exception('Failed to get data quality report: ${response.statusCode}');
      }
    } catch (e) {
      print('Network error in getDataQualityReport: $e');
      throw Exception('Network error: $e');
    }
  }
}
