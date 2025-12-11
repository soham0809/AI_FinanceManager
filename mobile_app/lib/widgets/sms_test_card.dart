import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/transaction_provider.dart';

class SMSTestCard extends StatefulWidget {
  const SMSTestCard({super.key});

  @override
  State<SMSTestCard> createState() => _SMSTestCardState();
}

class _SMSTestCardState extends State<SMSTestCard> {
  final TextEditingController _smsController = TextEditingController();
  bool _useLocal = true;
  
  // Removed test samples for production UI
  final List<Map<String, String>> sampleSMS = const [];

  @override
  void dispose() {
    _smsController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'SMS Parser',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'Paste an SMS below and parse it with AI or quick regex mode.',
              style: TextStyle(fontSize: 14, color: Colors.grey),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _smsController,
              maxLines: 3,
              decoration: const InputDecoration(
                labelText: 'Enter SMS Text',
                hintText: 'Paste a transaction SMS here...',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                const Text('Parsing Mode:'),
                const SizedBox(width: 8),
                Expanded(
                  child: Column(
                    children: [
                      ChoiceChip(
                        label: const Text('🚀 NLP Quick Parse (Fast)'),
                        selected: _useLocal,
                        onSelected: (v) => setState(() => _useLocal = true),
                      ),
                      const SizedBox(height: 4),
                      ChoiceChip(
                        label: const Text('🤖 LLM Detailed Parse (Accurate)'),
                        selected: !_useLocal,
                        onSelected: (v) => setState(() => _useLocal = false),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              child: Consumer<TransactionProvider>(
                builder: (context, provider, child) {
                  return ElevatedButton.icon(
                    onPressed: provider.isLoading || _smsController.text.isEmpty
                        ? null
                        : () => _parseSMS(context, provider),
                    icon: provider.isLoading
                        ? const SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Icon(Icons.psychology),
                    label: Text(provider.isLoading ? 'Parsing...' : 'Parse SMS'),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _parseSMS(BuildContext context, TransactionProvider provider) async {
    if (_smsController.text.trim().isEmpty) return;
    
    try {
      final result = await provider.parseSms(_smsController.text.trim(), useLocal: _useLocal);
      
      if (context.mounted) {
        if (result['filtered'] == true) {
          // SMS was filtered out
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('🛡️ SMS Filtered: ${result['filter_reason']}'),
                  Text('Confidence: ${(result['confidence'] * 100).toStringAsFixed(1)}%'),
                  if (result['detected_keywords'] != null && result['detected_keywords'].isNotEmpty)
                    Text('Keywords: ${result['detected_keywords'].join(', ')}'),
                ],
              ),
              backgroundColor: Colors.orange,
              duration: const Duration(seconds: 4),
            ),
          );
        } else if (result['success'] == true) {
          // Successfully parsed
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('✅ SMS parsed successfully!'),
                  if (result['sms_analysis'] != null)
                    Text('Filter confidence: ${(result['sms_analysis']['filter_confidence'] * 100).toStringAsFixed(1)}%'),
                ],
              ),
              backgroundColor: Colors.green,
              duration: const Duration(seconds: 3),
            ),
          );
          _smsController.clear();
        } else {
          // Parsing failed
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('❌ Failed to parse SMS: ${result['error'] ?? 'Unknown error'}'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('❌ Error: ${e.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }
}
