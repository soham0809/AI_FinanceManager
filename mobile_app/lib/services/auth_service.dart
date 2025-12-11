import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../config/network_config.dart';

class AuthService {
  static String get baseUrl => NetworkConfig.baseUrl;
  static const String _accessTokenKey = 'access_token';
  static const String _refreshTokenKey = 'refresh_token';
  static const String _userDataKey = 'user_data';

  // User model
  static Map<String, dynamic>? _currentUser;
  static String? _accessToken;
  static String? _refreshToken;

  // Initialize auth service
  static Future<void> initialize() async {
    final prefs = await SharedPreferences.getInstance();
    _accessToken = prefs.getString(_accessTokenKey);
    _refreshToken = prefs.getString(_refreshTokenKey);
    
    final userDataString = prefs.getString(_userDataKey);
    if (userDataString != null) {
      _currentUser = jsonDecode(userDataString);
    }
  }

  // Check if user is logged in
  static bool get isLoggedIn => _accessToken != null && _refreshToken != null;

  // Get current user
  static Map<String, dynamic>? get currentUser => _currentUser;

  // Get access token
  static String? get accessToken => _accessToken;

  // Register new user
  static Future<Map<String, dynamic>> register({
    required String email,
    required String username,
    required String password,
    String? fullName,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/register'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email,
          'username': username,
          'password': password,
          'full_name': fullName,
        }),
      );

      final data = jsonDecode(response.body);

      if (response.statusCode == 201) {
        return {
          'success': true,
          'message': 'Registration successful',
          'user': data,
        };
      } else {
        return {
          'success': false,
          'message': data['detail'] ?? 'Registration failed',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Network error: $e',
      };
    }
  }

  // Login user
  static Future<Map<String, dynamic>> login({
    required String username,
    required String password,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/login'),
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: {
          'username': username,
          'password': password,
        },
      );

      final data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        // Store tokens and user data
        await _storeAuthData(data);
        
        return {
          'success': true,
          'message': 'Login successful',
          'user': data['user'],
        };
      } else {
        return {
          'success': false,
          'message': data['detail'] ?? 'Login failed',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Network error: $e',
      };
    }
  }

  // Refresh access token
  static Future<bool> refreshToken() async {
    if (_refreshToken == null) return false;

    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/refresh'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'refresh_token': _refreshToken,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _accessToken = data['access_token'];
        
        // Update stored access token
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString(_accessTokenKey, _accessToken!);
        
        return true;
      } else {
        // Refresh token is invalid, logout user
        await logout();
        return false;
      }
    } catch (e) {
      print('Token refresh error: $e');
      return false;
    }
  }

  // Logout user
  static Future<void> logout() async {
    try {
      // Call logout endpoint if we have a valid access token
      if (_accessToken != null) {
        await http.post(
          Uri.parse('$baseUrl/auth/logout'),
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer $_accessToken',
          },
        );
      }
    } catch (e) {
      print('Logout API error: $e');
    } finally {
      // Clear local storage regardless of API call success
      await _clearAuthData();
    }
  }

  // Get current user info from server
  static Future<Map<String, dynamic>?> getCurrentUserInfo() async {
    if (_accessToken == null) return null;

    try {
      final response = await http.get(
        Uri.parse('$baseUrl/auth/me'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $_accessToken',
        },
      );

      if (response.statusCode == 200) {
        final userData = jsonDecode(response.body);
        _currentUser = userData;
        
        // Update stored user data
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString(_userDataKey, jsonEncode(userData));
        
        return userData;
      } else if (response.statusCode == 401) {
        // Token expired, try to refresh
        if (await refreshToken()) {
          return await getCurrentUserInfo(); // Retry with new token
        } else {
          await logout(); // Refresh failed, logout
          return null;
        }
      }
    } catch (e) {
      print('Get user info error: $e');
    }
    
    return null;
  }

  // Make authenticated HTTP request
  static Future<http.Response?> authenticatedRequest({
    required String method,
    required String endpoint,
    Map<String, String>? headers,
    dynamic body,
  }) async {
    if (_accessToken == null) {
      throw Exception('No access token available');
    }

    final authHeaders = {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $_accessToken',
      ...?headers,
    };

    http.Response response;
    final uri = Uri.parse('$baseUrl$endpoint');

    try {
      switch (method.toUpperCase()) {
        case 'GET':
          response = await http.get(uri, headers: authHeaders);
          break;
        case 'POST':
          response = await http.post(uri, headers: authHeaders, body: body);
          break;
        case 'PUT':
          response = await http.put(uri, headers: authHeaders, body: body);
          break;
        case 'DELETE':
          response = await http.delete(uri, headers: authHeaders);
          break;
        default:
          throw Exception('Unsupported HTTP method: $method');
      }

      // Handle token expiration
      if (response.statusCode == 401) {
        if (await refreshToken()) {
          // Retry with new token
          authHeaders['Authorization'] = 'Bearer $_accessToken';
          switch (method.toUpperCase()) {
            case 'GET':
              response = await http.get(uri, headers: authHeaders);
              break;
            case 'POST':
              response = await http.post(uri, headers: authHeaders, body: body);
              break;
            case 'PUT':
              response = await http.put(uri, headers: authHeaders, body: body);
              break;
            case 'DELETE':
              response = await http.delete(uri, headers: authHeaders);
              break;
          }
        } else {
          await logout();
          throw Exception('Authentication failed');
        }
      }

      return response;
    } catch (e) {
      print('Authenticated request error: $e');
      return null;
    }
  }

  // Store authentication data
  static Future<void> _storeAuthData(Map<String, dynamic> authData) async {
    _accessToken = authData['access_token'];
    _refreshToken = authData['refresh_token'];
    _currentUser = authData['user'];

    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_accessTokenKey, _accessToken!);
    await prefs.setString(_refreshTokenKey, _refreshToken!);
    await prefs.setString(_userDataKey, jsonEncode(_currentUser!));
  }

  // Clear authentication data
  static Future<void> _clearAuthData() async {
    _accessToken = null;
    _refreshToken = null;
    _currentUser = null;

    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_accessTokenKey);
    await prefs.remove(_refreshTokenKey);
    await prefs.remove(_userDataKey);
  }

  // Check token expiration and refresh if needed
  static Future<bool> ensureValidToken() async {
    if (_accessToken == null) return false;
    
    // Try to get user info to validate token
    final userInfo = await getCurrentUserInfo();
    return userInfo != null;
  }
}
