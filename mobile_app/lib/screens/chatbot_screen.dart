import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';

class ChatMessage {
  final String text;
  final bool isUser;
  final DateTime timestamp;
  final int? transactionCount;
  final String? source;
  final String? sourceDescription;
  final bool? cached;
  final double? processingTime;
  final double? qualityScore;

  ChatMessage({
    required this.text,
    required this.isUser,
    required this.timestamp,
    this.transactionCount,
    this.source,
    this.sourceDescription,
    this.cached,
    this.processingTime,
    this.qualityScore,
  });
}

class ChatbotScreen extends StatefulWidget {
  const ChatbotScreen({Key? key}) : super(key: key);

  @override
  State<ChatbotScreen> createState() => _ChatbotScreenState();
}

class _ChatbotScreenState extends State<ChatbotScreen> {
  final TextEditingController _messageController = TextEditingController();
  final List<ChatMessage> _messages = [];
  final ScrollController _scrollController = ScrollController();
  final ApiService _apiService = ApiService();
  bool _isLoading = false;
  bool _useEnhancedChatbot = true; // Toggle for enhanced vs old chatbot
  Map<String, dynamic>? _dataQuality;

  @override
  void initState() {
    super.initState();
    _loadQuickInsights();
  }

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _loadQuickInsights() async {
    setState(() => _isLoading = true);
    
    try {
      // Load data quality if user is authenticated and using enhanced chatbot
      if (AuthService.isLoggedIn && _useEnhancedChatbot) {
        try {
          _dataQuality = await _apiService.getDataQualityReport();
          final quality = _dataQuality!['data_quality'];
          
          _addMessage(ChatMessage(
            text: "🎉 Welcome to Enhanced Financial Assistant!\n\n"
                  "📊 Data Quality: ${quality['quality_score']}%\n"
                  "📈 Transactions: ${quality['total_transactions']}\n"
                  "📅 Range: ${quality['data_range']['from']} to ${quality['data_range']['to']}\n\n"
                  "I can analyze your parsed transaction data intelligently. Try asking:\n"
                  "• 'How much did I spend this month?'\n"
                  "• 'What are my top spending categories?'\n"
                  "• 'Show me my spending trends'",
            isUser: false,
            timestamp: DateTime.now(),
            transactionCount: quality['total_transactions'],
            qualityScore: quality['quality_score'].toDouble(),
            source: 'enhanced',
            sourceDescription: 'Enhanced AI with Transaction Context',
          ));
        } catch (e) {
          print('Failed to load data quality: $e');
          _addMessage(ChatMessage(
            text: "Welcome to Enhanced Financial Assistant! Please ensure you're logged in to access your transaction data.",
            isUser: false,
            timestamp: DateTime.now(),
          ));
        }
      } else {
        // Fallback to old quick insights
        final response = await _apiService.getQuickInsights();
        _addMessage(ChatMessage(
          text: "Welcome! Here are your quick financial insights:\n\n${response['insights']}",
          isUser: false,
          timestamp: DateTime.now(),
          transactionCount: response['transaction_count'],
          source: 'basic',
          sourceDescription: 'Basic Chatbot',
        ));
      }
    } catch (e) {
      _addMessage(ChatMessage(
        text: "Welcome to your Financial Assistant! Ask me about your spending patterns, transactions, or financial insights.",
        isUser: false,
        timestamp: DateTime.now(),
      ));
    }
    
    setState(() => _isLoading = false);
  }

  Future<void> _sendMessage(String message) async {
    if (message.trim().isEmpty) return;

    // Add user message
    _addMessage(ChatMessage(
      text: message,
      isUser: true,
      timestamp: DateTime.now(),
    ));

    _messageController.clear();
    setState(() => _isLoading = true);

    try {
      Map<String, dynamic> response;
      
      if (_useEnhancedChatbot && AuthService.isLoggedIn) {
        print('🤖 Using enhanced chatbot with transaction context');
        response = await _apiService.queryEnhancedChatbot(message);
        
        _addMessage(ChatMessage(
          text: response['response'],
          isUser: false,
          timestamp: DateTime.now(),
          transactionCount: response['transaction_count'],
          cached: response['cached'],
          processingTime: response['processing_time']?.toDouble(),
          qualityScore: response['data_quality']['quality_score']?.toDouble(),
          source: 'enhanced',
          sourceDescription: 'Enhanced AI with Transaction Context',
        ));
      } else {
        print('🤖 Using basic chatbot');
        response = await _apiService.queryChatbot(message);
        
        _addMessage(ChatMessage(
          text: response['response'],
          isUser: false,
          timestamp: DateTime.now(),
          transactionCount: response['transaction_count'],
          source: response['source'] ?? 'basic',
          sourceDescription: response['source_description'] ?? 'Basic Chatbot',
        ));
      }
    } catch (e) {
      print('❌ Chatbot error: $e');
      String errorMessage = "Sorry, I'm having trouble processing your request right now.";
      
      if (e.toString().contains('timeout')) {
        errorMessage = "The AI is taking too long to respond. Please try a simpler question.";
      } else if (e.toString().contains('connection')) {
        errorMessage = "Can't connect to the AI service. Please check your internet connection.";
      } else if (e.toString().contains('500')) {
        errorMessage = "The AI service is having issues. Please try again in a moment.";
      } else if (e.toString().contains('Authentication required')) {
        errorMessage = "Please log in to use the enhanced chatbot with your transaction data.";
      }
      
      _addMessage(ChatMessage(
        text: "$errorMessage\n\nError details: ${e.toString()}",
        isUser: false,
        timestamp: DateTime.now(),
      ));
    }

    setState(() => _isLoading = false);
  }

  void _addMessage(ChatMessage message) {
    setState(() {
      _messages.add(message);
    });
    
    // Auto-scroll to bottom
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_useEnhancedChatbot ? 'Enhanced Financial Assistant' : 'Basic Financial Assistant'),
        backgroundColor: _useEnhancedChatbot ? Colors.deepPurple : Colors.grey[700],
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          // Enhanced chatbot toggle
          Row(
            children: [
              Text(
                'Enhanced',
                style: TextStyle(
                  fontSize: 12,
                  color: _useEnhancedChatbot ? Colors.white : Colors.white70,
                ),
              ),
              Switch(
                value: _useEnhancedChatbot,
                onChanged: AuthService.isLoggedIn ? (value) {
                  setState(() {
                    _useEnhancedChatbot = value;
                    _messages.clear(); // Clear messages when switching
                  });
                  _loadQuickInsights(); // Reload with new mode
                } : null,
                activeColor: Colors.white,
                inactiveThumbColor: Colors.white70,
              ),
              const SizedBox(width: 8),
            ],
          ),
        ],
      ),
      body: Column(
        children: [
          // Quick action buttons
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.grey[50],
              boxShadow: [
                BoxShadow(
                  color: Colors.grey.withOpacity(0.1),
                  spreadRadius: 1,
                  blurRadius: 3,
                  offset: const Offset(0, 1),
                ),
              ],
            ),
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: [
                  _buildQuickActionButton("Monthly Spending", "How much did I spend this month?"),
                  const SizedBox(width: 8),
                  _buildQuickActionButton("Top Categories", "What are my top spending categories?"),
                  const SizedBox(width: 8),
                  _buildQuickActionButton("Subscriptions", "Show me my subscription payments"),
                  const SizedBox(width: 8),
                  _buildQuickActionButton("Food Delivery", "How much did I spend on food delivery?"),
                ],
              ),
            ),
          ),
          
          // Chat messages
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.all(16),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                return _buildMessageBubble(_messages[index]);
              },
            ),
          ),
          
          // Loading indicator
          if (_isLoading)
            Padding(
              padding: const EdgeInsets.all(8),
              child: Row(
                children: [
                  const SizedBox(width: 16),
                  const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    "Analyzing your transactions...",
                    style: TextStyle(color: Colors.grey[600]),
                  ),
                ],
              ),
            ),
          
          // Message input
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              boxShadow: [
                BoxShadow(
                  color: Colors.grey.withOpacity(0.1),
                  spreadRadius: 1,
                  blurRadius: 3,
                  offset: const Offset(0, -1),
                ),
              ],
            ),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _messageController,
                    decoration: InputDecoration(
                      hintText: "Ask about your finances...",
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(25),
                        borderSide: BorderSide.none,
                      ),
                      filled: true,
                      fillColor: Colors.grey[100],
                      contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
                    ),
                    onSubmitted: _sendMessage,
                    enabled: !_isLoading,
                  ),
                ),
                const SizedBox(width: 8),
                FloatingActionButton(
                  onPressed: _isLoading ? null : () => _sendMessage(_messageController.text),
                  backgroundColor: Colors.deepPurple,
                  mini: true,
                  child: const Icon(Icons.send, color: Colors.white),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickActionButton(String label, String query) {
    return ElevatedButton(
      onPressed: _isLoading ? null : () => _sendMessage(query),
      style: ElevatedButton.styleFrom(
        backgroundColor: Colors.deepPurple[50],
        foregroundColor: Colors.deepPurple[700],
        elevation: 0,
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
        ),
      ),
      child: Text(label, style: const TextStyle(fontSize: 12)),
    );
  }

  Widget _buildMessageBubble(ChatMessage message) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Row(
        mainAxisAlignment: message.isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!message.isUser) ...[
            CircleAvatar(
              radius: 16,
              backgroundColor: Colors.deepPurple,
              child: const Icon(Icons.smart_toy, color: Colors.white, size: 16),
            ),
            const SizedBox(width: 8),
          ],
          Flexible(
            child: Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: message.isUser ? Colors.deepPurple : Colors.grey[100],
                borderRadius: BorderRadius.circular(16),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    message.text,
                    style: TextStyle(
                      color: message.isUser ? Colors.white : Colors.black87,
                      fontSize: 14,
                    ),
                  ),
                  if (message.transactionCount != null) ...[
                    const SizedBox(height: 4),
                    Text(
                      "Based on ${message.transactionCount} transactions",
                      style: TextStyle(
                        color: Colors.grey[600],
                        fontSize: 11,
                        fontStyle: FontStyle.italic,
                      ),
                    ),
                  ],
                  if (!message.isUser && message.sourceDescription != null) ...[
                    const SizedBox(height: 4),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(
                        color: _getSourceColor(message.source),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        "📡 ${message.sourceDescription}",
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 9,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ),
                  ],
                  // Enhanced chatbot features
                  if (!message.isUser && message.source == 'enhanced') ...[
                    const SizedBox(height: 4),
                    Wrap(
                      spacing: 4,
                      children: [
                        if (message.cached != null)
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
                            decoration: BoxDecoration(
                              color: message.cached! ? Colors.green : Colors.orange,
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: Text(
                              message.cached! ? "⚡ CACHED" : "🔄 NEW",
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 8,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                        if (message.qualityScore != null)
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
                            decoration: BoxDecoration(
                              color: Colors.blue,
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: Text(
                              "📊 ${message.qualityScore!.toStringAsFixed(1)}%",
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 8,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                        if (message.processingTime != null)
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
                            decoration: BoxDecoration(
                              color: Colors.purple,
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: Text(
                              "⏱️ ${message.processingTime!.toStringAsFixed(1)}s",
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 8,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                      ],
                    ),
                  ],
                  const SizedBox(height: 4),
                  Text(
                    "${message.timestamp.hour}:${message.timestamp.minute.toString().padLeft(2, '0')}",
                    style: TextStyle(
                      color: message.isUser ? Colors.white70 : Colors.grey[500],
                      fontSize: 10,
                    ),
                  ),
                ],
              ),
            ),
          ),
          if (message.isUser) ...[
            const SizedBox(width: 8),
            CircleAvatar(
              radius: 16,
              backgroundColor: Colors.grey[300],
              child: Icon(Icons.person, color: Colors.grey[600], size: 16),
            ),
          ],
        ],
      ),
    );
  }

  Color _getSourceColor(String? source) {
    switch (source) {
      case 'enhanced':
        return Colors.deepPurple;
      case 'ai_model':
        return Colors.green;
      case 'analytics':
        return Colors.blue;
      case 'basic':
        return Colors.grey[600]!;
      case 'fallback':
        return Colors.orange;
      default:
        return Colors.grey;
    }
  }
}
