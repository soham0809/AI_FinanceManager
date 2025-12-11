import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/mock_sms_service.dart';
import '../providers/transaction_provider.dart';

class SmsTestingWidget extends StatefulWidget {
  const SmsTestingWidget({Key? key}) : super(key: key);

  @override
  State<SmsTestingWidget> createState() => _SmsTestingWidgetState();
}

class _SmsTestingWidgetState extends State<SmsTestingWidget> {
  final TextEditingController _smsController = TextEditingController();
  bool _isProcessing = false;
  Map<String, dynamic>? _lastResult;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.all(16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.sms, color: Colors.blue),
                const SizedBox(width: 8),
                const Text(
                  'SMS Testing (No SIM Required)',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            
            // Mock SMS buttons
            Wrap(
              spacing: 8,
              children: [
                ElevatedButton.icon(
                  onPressed: () => _loadRandomSms(),
                  icon: const Icon(Icons.shuffle),
                  label: const Text('Random SMS'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green,
                    foregroundColor: Colors.white,
                  ),
                ),
                ElevatedButton.icon(
                  onPressed: () => _loadCustomSms(),
                  icon: const Icon(Icons.auto_awesome),
                  label: const Text('Generate SMS'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.orange,
                    foregroundColor: Colors.white,
                  ),
                ),
                ElevatedButton.icon(
                  onPressed: () => _loadMultipleSms(),
                  icon: const Icon(Icons.burst_mode),
                  label: const Text('Bulk Test'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.purple,
                    foregroundColor: Colors.white,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            
            // SMS input field
            TextField(
              controller: _smsController,
              maxLines: 3,
              decoration: const InputDecoration(
                labelText: 'SMS Text (or use buttons above)',
                hintText: 'Your account debited by Rs.250 at Zomato...',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.message),
              ),
            ),
            const SizedBox(height: 16),
            
            // Process button
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: _isProcessing ? null : _processSms,
                icon: _isProcessing 
                    ? const SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.analytics),
                label: Text(_isProcessing ? 'Processing...' : 'Analyze SMS'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blue,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 12),
                ),
              ),
            ),
            
            // Results display
            if (_lastResult != null) ...[
              const SizedBox(height: 20),
              const Divider(),
              const SizedBox(height: 12),
              _buildResultDisplay(),
            ],
          ],
        ),
      ),
    );
  }

  void _loadRandomSms() {
    setState(() {
      _smsController.text = MockSmsService.getRandomSms();
    });
  }

  void _loadCustomSms() {
    setState(() {
      _smsController.text = MockSmsService.generateCustomSms();
    });
  }

  void _loadMultipleSms() async {
    final messages = MockSmsService.getMockSmsMessages(count: 5);
    
    for (int i = 0; i < messages.length; i++) {
      setState(() {
        _smsController.text = messages[i];
        _isProcessing = true;
      });
      
      await _processSms(showSnackbar: false);
      
      if (i < messages.length - 1) {
        await Future.delayed(const Duration(milliseconds: 500));
      }
    }
    
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Processed ${messages.length} SMS messages!'),
        backgroundColor: Colors.green,
      ),
    );
  }

  Future<void> _processSms({bool showSnackbar = true}) async {
    if (_smsController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please enter SMS text or use mock data'),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }

    setState(() {
      _isProcessing = true;
    });

    try {
      final provider = Provider.of<TransactionProvider>(context, listen: false);
      final result = await provider.parseSms(_smsController.text);
      
      setState(() {
        _lastResult = result;
        _isProcessing = false;
      });

      if (showSnackbar) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              result['success'] == true 
                  ? 'SMS parsed successfully!' 
                  : 'SMS parsing failed'
            ),
            backgroundColor: result['success'] == true ? Colors.green : Colors.red,
          ),
        );
      }
    } catch (e) {
      setState(() {
        _isProcessing = false;
        _lastResult = {
          'success': false,
          'error': e.toString(),
        };
      });

      if (showSnackbar) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Widget _buildResultDisplay() {
    if (_lastResult == null) return const SizedBox();

    final isSuccess = _lastResult!['success'] == true;
    
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: isSuccess ? Colors.green.withOpacity(0.1) : Colors.red.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: isSuccess ? Colors.green : Colors.red,
          width: 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                isSuccess ? Icons.check_circle : Icons.error,
                color: isSuccess ? Colors.green : Colors.red,
              ),
              const SizedBox(width: 8),
              Text(
                isSuccess ? 'Parsing Successful' : 'Parsing Failed',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: isSuccess ? Colors.green : Colors.red,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          
          if (isSuccess) ...[
            _buildResultRow('Vendor', _lastResult!['vendor']),
            _buildResultRow('Amount', 'Rs.${_lastResult!['amount']}'),
            _buildResultRow('Type', _lastResult!['transaction_type']),
            _buildResultRow('Category', _lastResult!['category']),
            _buildResultRow('Date', _lastResult!['date']),
            if (_lastResult!['confidence'] != null)
              _buildResultRow('Confidence', '${(_lastResult!['confidence'] * 100).toStringAsFixed(1)}%'),
          ] else ...[
            _buildResultRow('Error', _lastResult!['error'] ?? 'Unknown error'),
            if (_lastResult!['error_type'] != null)
              _buildResultRow('Error Type', _lastResult!['error_type']),
            if (_lastResult!['suggestions'] != null) ...[
              const SizedBox(height: 8),
              const Text('Suggestions:', style: TextStyle(fontWeight: FontWeight.w600)),
              ...(_lastResult!['suggestions'] as List).map((suggestion) =>
                Padding(
                  padding: const EdgeInsets.only(left: 16, top: 4),
                  child: Text('• $suggestion', style: const TextStyle(fontSize: 12)),
                ),
              ),
            ],
          ],
        ],
      ),
    );
  }

  Widget _buildResultRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 80,
            child: Text(
              '$label:',
              style: const TextStyle(fontWeight: FontWeight.w600),
            ),
          ),
          Expanded(
            child: Text(value),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _smsController.dispose();
    super.dispose();
  }
}
