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
  
  // Sample SMS messages for testing
  final List<String> sampleSMS = [
    'Rs 450.00 debited from A/c **1234 on 10-Sep-24 at SWIGGY BANGALORE for UPI/123456789. Avl Bal Rs 15,234.56',
    'Amount Rs 1250.50 paid to AMAZON PAY INDIA via UPI on 10-Sep-24. UPI Ref No 123456789012. Available Balance: Rs 8,765.43',
    'Rs 75.00 debited for UBER TRIP on 10-Sep-24. Transaction ID: 987654321. Current Balance: Rs 12,890.25',
    'You have received Rs 2000.00 from JOHN DOE via UPI on 10-Sep-24. Ref: 456789123. Balance: Rs 14,890.25',
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
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: sampleSMS.asMap().entries.map((entry) {
                int index = entry.key;
                return ElevatedButton(
                  onPressed: () {
                    _smsController.text = entry.value;
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.blue.shade50,
                    foregroundColor: Colors.blue.shade700,
                  ),
                  child: Text('Sample ${index + 1}'),
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
      await provider.parseSMSAndAddTransaction(_smsController.text.trim());
      
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('SMS parsed successfully!'),
            backgroundColor: Colors.green,
          ),
        );
        _smsController.clear();
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to parse SMS: ${provider.error}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }
}
