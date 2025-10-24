import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/transaction_provider.dart';

class MLCategorizationCard extends StatefulWidget {
  const MLCategorizationCard({Key? key}) : super(key: key);

  @override
  State<MLCategorizationCard> createState() => _MLCategorizationCardState();
}

class _MLCategorizationCardState extends State<MLCategorizationCard> {
  final TextEditingController _vendorController = TextEditingController();
  Map<String, dynamic>? _categorizationResult;
  Map<String, dynamic>? _modelInfo;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadModelInfo();
  }

  Future<void> _loadModelInfo() async {
    try {
      final provider = Provider.of<TransactionProvider>(context, listen: false);
      final info = await provider.apiService.getMLModelInfo();
      setState(() {
        _modelInfo = info;
      });
    } catch (e) {
      print('Failed to load ML model info: $e');
    }
  }

  Future<void> _categorizeVendor() async {
    if (_vendorController.text.trim().isEmpty) return;

    setState(() {
      _isLoading = true;
      _categorizationResult = null;
    });

    try {
      final provider = Provider.of<TransactionProvider>(context, listen: false);
      final result = await provider.apiService.categorizeVendor(_vendorController.text.trim());
      
      setState(() {
        _categorizationResult = result;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to categorize: $e')),
      );
    }
  }

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
                const Icon(Icons.psychology, color: Colors.purple),
                const SizedBox(width: 8),
                const Text(
                  'AI Categorization',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            
            // Model Info
            if (_modelInfo != null) ...[
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.purple.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'ML Model Status: ${_modelInfo!['status']}',
                      style: const TextStyle(fontWeight: FontWeight.w500),
                    ),
                    Text('Model: ${_modelInfo!['model_type']}'),
                    Text('Categories: ${_modelInfo!['categories']?.length ?? 0}'),
                  ],
                ),
              ),
              const SizedBox(height: 16),
            ],

            // Vendor Input
            TextField(
              controller: _vendorController,
              decoration: const InputDecoration(
                labelText: 'Enter Vendor Name',
                hintText: 'e.g., SWIGGY BANGALORE, AMAZON PAY',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.store),
              ),
              onSubmitted: (_) => _categorizeVendor(),
            ),
            const SizedBox(height: 12),

            // Categorize Button
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: _isLoading ? null : _categorizeVendor,
                icon: _isLoading 
                  ? const SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.category),
                label: Text(_isLoading ? 'Categorizing...' : 'Categorize with AI'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.purple,
                  foregroundColor: Colors.white,
                ),
              ),
            ),

            // Results
            if (_categorizationResult != null) ...[
              const SizedBox(height: 16),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.green.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.green.withOpacity(0.3)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        const Icon(Icons.check_circle, color: Colors.green),
                        const SizedBox(width: 8),
                        const Text(
                          'AI Prediction',
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 16,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    
                    // Main prediction
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Category: ${_categorizationResult!['predicted_category']}',
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            'Confidence: ${(_categorizationResult!['confidence'] * 100).toStringAsFixed(1)}%',
                            style: TextStyle(
                              color: Colors.grey[600],
                              fontSize: 14,
                            ),
                          ),
                        ],
                      ),
                    ),
                    
                    const SizedBox(height: 12),
                    
                    // Top probabilities
                    const Text(
                      'All Predictions:',
                      style: TextStyle(fontWeight: FontWeight.w500),
                    ),
                    const SizedBox(height: 8),
                    
                    ...(_categorizationResult!['all_probabilities'] as Map<String, dynamic>)
                        .entries
                        .take(5)
                        .map((entry) {
                      final probability = entry.value as double;
                      return Padding(
                        padding: const EdgeInsets.symmetric(vertical: 2),
                        child: Row(
                          children: [
                            Expanded(
                              flex: 3,
                              child: Text(
                                entry.key,
                                style: const TextStyle(fontSize: 13),
                              ),
                            ),
                            Expanded(
                              flex: 2,
                              child: LinearProgressIndicator(
                                value: probability,
                                backgroundColor: Colors.grey[300],
                                valueColor: AlwaysStoppedAnimation<Color>(
                                  probability > 0.5 ? Colors.green : Colors.orange,
                                ),
                              ),
                            ),
                            const SizedBox(width: 8),
                            Text(
                              '${(probability * 100).toStringAsFixed(1)}%',
                              style: const TextStyle(fontSize: 12),
                            ),
                          ],
                        ),
                      );
                    }).toList(),
                  ],
                ),
              ),
            ],

            const SizedBox(height: 12),
            
            // Quick test buttons
            const Text(
              'Quick Tests:',
              style: TextStyle(fontWeight: FontWeight.w500),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 4,
              children: [
                'SWIGGY BANGALORE',
                'AMAZON PAY INDIA',
                'UBER TRIP',
                'NETFLIX INDIA',
                'APOLLO PHARMACY',
              ].map((vendor) => ActionChip(
                label: Text(
                  vendor,
                  style: const TextStyle(fontSize: 12),
                ),
                onPressed: () {
                  _vendorController.text = vendor;
                  _categorizeVendor();
                },
                backgroundColor: Colors.purple.withOpacity(0.1),
              )).toList(),
            ),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _vendorController.dispose();
    super.dispose();
  }
}
