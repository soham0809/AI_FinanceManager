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
    
    try {
      // Decide endpoint based on parsing mode
      final String authedPath = useLocal ? '/v1/parse-sms-local' : '/v1/parse-sms';
      final String publicPath = useLocal ? '/v1/parse-sms-local-public' : '/v1/parse-sms-public';

      // Try authenticated endpoint first if user is logged in
      if (AuthService.isLoggedIn && AuthService.accessToken != null) {
        print('🔐 Using ${useLocal ? 'LOCAL' : 'LLM'} authenticated SMS parsing endpoint');
        final response = await http.post(
          Uri.parse('$baseUrl$authedPath'),
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ${AuthService.accessToken}',
          },
          body: json.encode({'sms_text': smsText}),
        ).timeout(Duration(seconds: 60));
        
        if (response.statusCode == 200) {
          print('✅ Authenticated ${useLocal ? 'LOCAL' : 'LLM'} SMS parsing successful');
          return json.decode(response.body);
        } else if (response.statusCode == 401) {
          // Token expired, try to refresh
          await AuthService.refreshToken();
          // Retry with new token
          return await parseSms(smsText, useLocal: useLocal);
        }
        print('⚠️ Authenticated ${useLocal ? 'LOCAL' : 'LLM'} SMS parsing failed: ${response.statusCode}, falling back to public');
      }
      
      // Fallback to public endpoint
      print('⚠️ Using ${useLocal ? 'LOCAL' : 'LLM'} public SMS parsing endpoint');
      final response = await http.post(
        Uri.parse('$baseUrl$publicPath'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'sms_text': smsText}),
      ).timeout(Duration(seconds: 60));

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

  // Get all transactions (user-specific if authenticated)
  Future<List<Transaction>> getTransactions() async {
    try {
      // Try authenticated endpoint first
      if (AuthService.isLoggedIn && AuthService.accessToken != null) {
        final response = await http.get(
          Uri.parse('$baseUrl/v1/transactions'),
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ${AuthService.accessToken}',
          },
        );
        print('✅ getTransactions (authenticated) response status: ${response.statusCode}');
        
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
          print('❌ Authenticated endpoint failed: ${response.statusCode}');
          print('❌ Error body: ${response.body}');
        }
      }
      
      // Fallback to public endpoint (shows all transactions - not ideal)
      print('⚠️ Using public endpoint - transactions not user-isolated');
      final response = await http.get(Uri.parse('$baseUrl/v1/transactions-public'));
      print('✅ getTransactions (public) response status: ${response.statusCode}');
      
      if (response.statusCode == 200) {
        final List<dynamic> transactionsJson = json.decode(response.body);
        print('✅ Successfully parsed ${transactionsJson.length} transactions (all users)');
        
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
      // Prefer authenticated endpoint for proper user isolation
      if (AuthService.isLoggedIn && AuthService.accessToken != null) {
        final headers = {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ${AuthService.accessToken}',
        };

        final authResponse = await http.post(
          Uri.parse('$baseUrl/v1/transactions'),
          headers: headers,
          body: json.encode(transaction.toJson()),
        );

        if (authResponse.statusCode == 200 || authResponse.statusCode == 201) {
          return json.decode(authResponse.body);
        } else if (authResponse.statusCode == 401) {
          // Try refresh token once
          await AuthService.refreshToken();
          final retryHeaders = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ${AuthService.accessToken}',
          };
          final retryResponse = await http.post(
            Uri.parse('$baseUrl/v1/transactions'),
            headers: retryHeaders,
            body: json.encode(transaction.toJson()),
          );
          if (retryResponse.statusCode == 200 || retryResponse.statusCode == 201) {
            return json.decode(retryResponse.body);
          }
          print('❌ Authenticated save failed after refresh: ${retryResponse.statusCode}');
          print('❌ Error body: ${retryResponse.body}');
        } else {
          print('❌ Authenticated save failed: ${authResponse.statusCode}');
          print('❌ Error body: ${authResponse.body}');
        }
      }

      // Fallback to public endpoint (not user-isolated)
      final publicResponse = await http.post(
        Uri.parse('$baseUrl/v1/transactions-public'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(transaction.toJson()),
      );

      if (publicResponse.statusCode == 200 || publicResponse.statusCode == 201) {
        return json.decode(publicResponse.body);
      } else {
        print('Error response body: ${publicResponse.body}'); // Add this line
        throw Exception('Failed to save transaction: ${publicResponse.statusCode}');
      }
    } catch (e) {
      print('Network error in saveTransaction: $e'); // Add this line
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

    final resp = await http
        .post(Uri.parse('$baseUrl$path'), headers: headers, body: body)
        .timeout(Duration(seconds: 30));

    if (resp.statusCode == 200) {
      return json.decode(resp.body) as Map<String, dynamic>;
    }

    print('❌ startParseSmsBatch failed: ${resp.statusCode}');
    print('❌ Body: ${resp.body}');
    throw Exception('Failed to start batch parsing: ${resp.statusCode}');
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
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/v1/analytics/monthly-trends-public'),
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
        Uri.parse('$baseUrl/v1/analytics/insights-public'),
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
        Uri.parse('$baseUrl/v1/analytics/top-vendors-public?limit=$limit'),
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

  // Chatbot endpoints
  Future<Map<String, dynamic>> queryChatbot(String query, {int limit = 100}) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/v1/chatbot/query-public'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'query': query,
          'limit': limit,
        }),
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
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
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/v1/chatbot/quick-insights-public'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
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
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/v1/chatbot/summary-public?days=$days'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
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
