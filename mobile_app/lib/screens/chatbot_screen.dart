import 'package:flutter/material.dart';
import '../services/api_service.dart';

class ChatMessage {
  final String text;
  final bool isUser;
  final DateTime timestamp;
  final int? transactionCount;

  ChatMessage({
    required this.text,
    required this.isUser,
    required this.timestamp,
    this.transactionCount,
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
      final response = await _apiService.getQuickInsights();
      _addMessage(ChatMessage(
        text: "Welcome! Here are your quick financial insights:\n\n${response['insights']}",
        isUser: false,
        timestamp: DateTime.now(),
        transactionCount: response['transaction_count'],
      ));
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
      print('🤖 Sending chatbot query: $message');
      final response = await _apiService.queryChatbot(message);
      print('🤖 Received response: ${response.toString()}');
      
      _addMessage(ChatMessage(
        text: response['response'],
        isUser: false,
        timestamp: DateTime.now(),
        transactionCount: response['transaction_count'],
      ));
    } catch (e) {
      print('❌ Chatbot error: $e');
      String errorMessage = "Sorry, I'm having trouble processing your request right now.";
      
      if (e.toString().contains('timeout')) {
        errorMessage = "The AI is taking too long to respond. Please try a simpler question.";
      } else if (e.toString().contains('connection')) {
        errorMessage = "Can't connect to the AI service. Please check your internet connection.";
      } else if (e.toString().contains('500')) {
        errorMessage = "The AI service is having issues. Please try again in a moment.";
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
        title: const Text('Financial Assistant'),
        backgroundColor: Colors.deepPurple,
        foregroundColor: Colors.white,
        elevation: 0,
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
}
