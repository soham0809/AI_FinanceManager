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
  
  // Sample SMS messages for testing
  final List<Map<String, String>> sampleSMS = [
    {
      'text': 'Rs 450.00 debited from A/c **1234 on 10-Sep-24 at SWIGGY BANGALORE for UPI/123456789. Avl Bal Rs 15,234.56',
      'type': '✅ Valid Transaction'
    },
    {
      'text': 'Amount Rs 1250.50 paid to AMAZON PAY INDIA via UPI on 10-Sep-24. UPI Ref No 123456789012. Available Balance: Rs 8,765.43',
      'type': '✅ Valid Transaction'
    },
    {
      'text': 'xyz has requested money through Google Pay. On approval Rs 1629.46 will be debited from your bank account.',
      'type': '❌ Request (Should Filter)'
    },
    {
      'text': 'John Doe is requesting Rs 500.00 via UPI. Tap to approve payment.',
      'type': '❌ Request (Should Filter)'
    },
    {
      'text': 'Your OTP for UPI transaction is 123456. Do not share with anyone. Valid for 10 minutes.',
      'type': '❌ OTP (Should Filter)'
    },
    {
      'text': 'Special offer! Get 50% cashback on your next order. Use code SAVE50. Limited time offer!',
      'type': '❌ Promotional (Should Filter)'
    },
  ];

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
              'Test SMS Parser',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'Test the AI SMS parsing functionality with sample transaction messages:',
              style: TextStyle(fontSize: 14, color: Colors.grey),
            ),
            const SizedBox(height: 12),
            
            // Sample SMS buttons
            Column(
              children: sampleSMS.asMap().entries.map((entry) {
                int index = entry.key;
                final sample = entry.value;
                final isValid = sample['type']!.startsWith('✅');
                
                return Container(
                  margin: const EdgeInsets.only(bottom: 8),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Expanded(
                            child: ElevatedButton(
                              onPressed: () {
                                _smsController.text = sample['text']!;
                              },
                              style: ElevatedButton.styleFrom(
                                backgroundColor: isValid ? Colors.green.shade50 : Colors.red.shade50,
                                foregroundColor: isValid ? Colors.green.shade700 : Colors.red.shade700,
                              ),
                              child: Text('Sample ${index + 1}'),
                            ),
                          ),
                          const SizedBox(width: 8),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                            decoration: BoxDecoration(
                              color: isValid ? Colors.green.shade100 : Colors.red.shade100,
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Text(
                              sample['type']!,
                              style: TextStyle(
                                fontSize: 10,
                                fontWeight: FontWeight.bold,
                                color: isValid ? Colors.green.shade700 : Colors.red.shade700,
                              ),
                            ),
                          ),
                        ],
                      ),
                      Padding(
                        padding: const EdgeInsets.only(left: 8, top: 4),
                        child: Text(
                          sample['text']!,
                          style: TextStyle(
                            fontSize: 11,
                            color: Colors.grey[600],
                            fontStyle: FontStyle.italic,
                          ),
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ),
                );
              }).toList(),
            ),
            
            const SizedBox(height: 12),
            
            // SMS input field
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
            
            // Parse button
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
