import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/transaction_provider.dart';
import '../models/transaction.dart';
import '../services/api_service.dart';

class SimpleAnalyticsDashboard extends StatefulWidget {
  const SimpleAnalyticsDashboard({Key? key}) : super(key: key);

  @override
  State<SimpleAnalyticsDashboard> createState() => _SimpleAnalyticsDashboardState();
}

class _SimpleAnalyticsDashboardState extends State<SimpleAnalyticsDashboard> {
  bool _isLoading = true;
  Map<String, double> _categorySpending = {};
  Map<String, double> _vendorSpending = {};
  Map<String, int> _paymentMethodCount = {};
  double _totalSpent = 0;
  double _totalEarned = 0;
  int _transactionCount = 0;
  
  // Monthly and Weekly data
  List<Map<String, dynamic>> _monthlyData = [];
  List<Map<String, dynamic>> _weeklyData = [];
  bool _hasMonthlyData = false;
  bool _hasWeeklyData = false; // Weekly trends disabled

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadAnalyticsData();
    });
  }

  Future<void> _loadAnalyticsData() async {
    if (!mounted) return;
    
    setState(() {
      _isLoading = true;
    });

    try {
      final provider = Provider.of<TransactionProvider>(context, listen: false);
      await provider.fetchTransactions();

      if (provider.transactions.isNotEmpty) {
        _calculateAnalytics(provider.transactions);
      }

      // Load monthly data (weekly disabled)
      await _loadMonthlyWeeklyData();

      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  void _calculateAnalytics(List<Transaction> transactions) {
    final now = DateTime.now();
    final thisMonth = transactions.where((t) {
      final date = t.parsedDate;
      return date.year == now.year && date.month == now.month;
    }).toList();

    _categorySpending.clear();
    _vendorSpending.clear();
    _paymentMethodCount.clear();
    _totalSpent = 0;
    _totalEarned = 0;
    _transactionCount = thisMonth.length;

    for (final transaction in thisMonth) {
      if (transaction.isDebit) {
        _totalSpent += transaction.amount;
        final category = transaction.category ?? 'Others';
        _categorySpending[category] = (_categorySpending[category] ?? 0) + transaction.amount;
        _vendorSpending[transaction.vendor] = (_vendorSpending[transaction.vendor] ?? 0) + transaction.amount;
      } else {
        _totalEarned += transaction.amount;
      }

      // Count payment methods
      final paymentMethod = transaction.paymentMethod ?? 'Unknown';
      _paymentMethodCount[paymentMethod] = (_paymentMethodCount[paymentMethod] ?? 0) + 1;
    }

    // Sort and limit top items
    final sortedCategories = _categorySpending.entries.toList()
      ..sort((a, b) => b.value.compareTo(a.value));
    _categorySpending = Map.fromEntries(sortedCategories.take(5));

    final sortedVendors = _vendorSpending.entries.toList()
      ..sort((a, b) => b.value.compareTo(a.value));
    _vendorSpending = Map.fromEntries(sortedVendors.take(5));
  }

  Future<void> _loadMonthlyWeeklyData() async {
    try {
      final apiService = ApiService();
      
      // Load monthly data
      try {
        final monthlyResponse = await apiService.getMonthlySpending(months: 6);
        if (monthlyResponse['success'] == true && monthlyResponse['data'] != null) {
          _monthlyData = List<Map<String, dynamic>>.from(
            monthlyResponse['data']['monthly_spending'] ?? []
          );
          _hasMonthlyData = true;
        }
      } catch (e) {
        print('Monthly data load failed: $e');
        _hasMonthlyData = false;
      }

      // Weekly trends disabled in UI
      _hasWeeklyData = false;
      _weeklyData = [];
    } catch (e) {
      print('Error loading monthly/weekly data: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(
        child: Padding(
          padding: EdgeInsets.all(32.0),
          child: CircularProgressIndicator(),
        ),
      );
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Quick Stats Cards
          _buildQuickStatsSection(),
          const SizedBox(height: 24),
          
          // Category Breakdown
          _buildCategorySection(),
          const SizedBox(height: 24),
          
          // Top Vendors
          _buildVendorSection(),
          const SizedBox(height: 24),
          
          // Payment Methods
          _buildPaymentMethodSection(),
          const SizedBox(height: 24),
          
          // Monthly Trends Section
          if (_hasMonthlyData) ...[
            _buildMonthlySection(),
            const SizedBox(height: 24),
          ],
          
          // Weekly Trends Section disabled
          
          // AI Insights
          _buildInsightsSection(),
        ],
      ),
    );
  }

  Widget _buildQuickStatsSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'This Month Overview',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(
              child: _buildStatCard(
                'Total Spent',
                '₹${_totalSpent.toStringAsFixed(2)}',
                Icons.arrow_downward,
                Colors.red,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildStatCard(
                'Total Earned',
                '₹${_totalEarned.toStringAsFixed(2)}',
                Icons.arrow_upward,
                Colors.green,
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: _buildStatCard(
                'Transactions',
                _transactionCount.toString(),
                Icons.receipt,
                Colors.blue,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildStatCard(
                'Average',
                _transactionCount > 0 ? '₹${(_totalSpent / _transactionCount).toStringAsFixed(0)}' : '₹0',
                Icons.analytics,
                Colors.purple,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildStatCard(String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: color, size: 20),
              const SizedBox(width: 8),
              Text(
                title,
                style: TextStyle(
                  color: color.withOpacity(0.8),
                  fontSize: 12,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              color: color,
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCategorySection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Top Spending Categories',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 16),
        if (_categorySpending.isEmpty)
          const Text('No spending data available')
        else
          ..._categorySpending.entries.map((entry) => _buildProgressBar(
            entry.key,
            entry.value,
            _totalSpent > 0 ? entry.value / _totalSpent : 0,
            _getCategoryColor(entry.key),
          )),
      ],
    );
  }

  Widget _buildVendorSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Top Vendors',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 16),
        if (_vendorSpending.isEmpty)
          const Text('No vendor data available')
        else
          ..._vendorSpending.entries.map((entry) => _buildProgressBar(
            entry.key,
            entry.value,
            _totalSpent > 0 ? entry.value / _totalSpent : 0,
            Colors.indigo,
          )),
      ],
    );
  }

  Widget _buildPaymentMethodSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Payment Methods',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 16),
        if (_paymentMethodCount.isEmpty)
          const Text('No payment method data available')
        else
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: _paymentMethodCount.entries.map((entry) => _buildPaymentMethodChip(
              entry.key,
              entry.value,
            )).toList(),
          ),
      ],
    );
  }

  Widget _buildPaymentMethodChip(String method, int count) {
    final color = _getPaymentMethodColor(method);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(_getPaymentMethodIcon(method), color: color, size: 16),
          const SizedBox(width: 6),
          Text(
            '$method ($count)',
            style: TextStyle(
              color: color,
              fontWeight: FontWeight.w500,
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildProgressBar(String label, double value, double percentage, Color color) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Text(
                  label,
                  style: const TextStyle(fontWeight: FontWeight.w500),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              Text(
                '₹${value.toStringAsFixed(0)}',
                style: TextStyle(
                  color: color,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          LinearProgressIndicator(
            value: percentage,
            backgroundColor: color.withOpacity(0.2),
            valueColor: AlwaysStoppedAnimation<Color>(color),
          ),
        ],
      ),
    );
  }

  Widget _buildInsightsSection() {
    final insights = _generateInsights();
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'AI Insights',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 16),
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [Colors.purple.withOpacity(0.1), Colors.blue.withOpacity(0.1)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.purple.withOpacity(0.3)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(Icons.psychology, color: Colors.purple, size: 20),
                  const SizedBox(width: 8),
                  const Text(
                    'Smart Recommendations',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              ...insights.map((insight) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('• ', style: TextStyle(color: Colors.purple)),
                    Expanded(child: Text(insight)),
                  ],
                ),
              )),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildMonthlySection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            const Icon(Icons.calendar_month, color: Colors.blue, size: 20),
            const SizedBox(width: 8),
            const Text(
              'Monthly Trends',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
          ],
        ),
        const SizedBox(height: 16),
        Container(
          height: 200,
          child: ListView.builder(
            scrollDirection: Axis.horizontal,
            itemCount: _monthlyData.length,
            itemBuilder: (context, index) {
              final monthData = _monthlyData[index];
              return Container(
                width: 140,
                margin: const EdgeInsets.only(right: 12),
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.blue.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.blue.withOpacity(0.3)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      monthData['month_name'] ?? 'Unknown',
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Spent: ₹${(monthData['total_spent'] ?? 0).toStringAsFixed(0)}',
                      style: TextStyle(
                        color: Colors.red[700],
                        fontSize: 12,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    Text(
                      'Transactions: ${monthData['transaction_count'] ?? 0}',
                      style: TextStyle(
                        color: Colors.grey[600],
                        fontSize: 11,
                      ),
                    ),
                    const Spacer(),
                    Text(
                      'Avg: ₹${monthData['transaction_count'] != null && monthData['transaction_count'] > 0 ? ((monthData['total_spent'] ?? 0) / monthData['transaction_count']).toStringAsFixed(0) : '0'}',
                      style: TextStyle(
                        color: Colors.blue[700],
                        fontSize: 11,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildWeeklySection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            const Icon(Icons.date_range, color: Colors.green, size: 20),
            const SizedBox(width: 8),
            const Text(
              'Weekly Trends',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
          ],
        ),
        const SizedBox(height: 16),
        Container(
          height: 200,
          child: ListView.builder(
            scrollDirection: Axis.horizontal,
            itemCount: _weeklyData.length,
            itemBuilder: (context, index) {
              final weekData = _weeklyData[index];
              return Container(
                width: 140,
                margin: const EdgeInsets.only(right: 12),
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.green.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.green.withOpacity(0.3)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Week ${weekData['week_number'] ?? 'Unknown'}',
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                      ),
                    ),
                    Text(
                      weekData['week_period'] ?? '',
                      style: TextStyle(
                        color: Colors.grey[600],
                        fontSize: 10,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Spent: ₹${(weekData['total_spent'] ?? 0).toStringAsFixed(0)}',
                      style: TextStyle(
                        color: Colors.red[700],
                        fontSize: 12,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    Text(
                      'Transactions: ${weekData['transaction_count'] ?? 0}',
                      style: TextStyle(
                        color: Colors.grey[600],
                        fontSize: 11,
                      ),
                    ),
                    const Spacer(),
                    Text(
                      'Avg: ₹${weekData['transaction_count'] != null && weekData['transaction_count'] > 0 ? ((weekData['total_spent'] ?? 0) / weekData['transaction_count']).toStringAsFixed(0) : '0'}',
                      style: TextStyle(
                        color: Colors.green[700],
                        fontSize: 11,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              );
            },
          ),
        ),
      ],
    );
  }

  List<String> _generateInsights() {
    final insights = <String>[];
    
    if (_categorySpending.isNotEmpty) {
      final topCategory = _categorySpending.entries.first;
      insights.add('Your highest spending category is ${topCategory.key} (₹${topCategory.value.toStringAsFixed(0)})');
    }
    
    if (_vendorSpending.isNotEmpty) {
      final topVendor = _vendorSpending.entries.first;
      insights.add('You spend the most at ${topVendor.key} (₹${topVendor.value.toStringAsFixed(0)})');
    }
    
    if (_transactionCount > 0) {
      final avgTransaction = _totalSpent / _transactionCount;
      if (avgTransaction > 500) {
        insights.add('Your average transaction is ₹${avgTransaction.toStringAsFixed(0)} - consider budgeting for smaller purchases');
      } else {
        insights.add('Good job keeping your average transaction low at ₹${avgTransaction.toStringAsFixed(0)}');
      }
    }
    
    final subscriptionCount = _paymentMethodCount['Subscription'] ?? 0;
    if (subscriptionCount > 0) {
      insights.add('You have $subscriptionCount subscription transactions - review them regularly');
    }
    
    if (insights.isEmpty) {
      insights.add('Start making transactions to see personalized insights');
    }
    
    return insights;
  }

  Color _getCategoryColor(String category) {
    switch (category.toLowerCase()) {
      case 'food & dining':
      case 'food':
        return Colors.orange;
      case 'shopping':
      case 'retail':
        return Colors.pink;
      case 'transportation':
      case 'travel':
        return Colors.blue;
      case 'entertainment':
        return Colors.purple;
      case 'bills & utilities':
      case 'utilities':
        return Colors.green;
      default:
        return Colors.grey;
    }
  }

  Color _getPaymentMethodColor(String method) {
    switch (method.toLowerCase()) {
      case 'upi':
        return Colors.orange;
      case 'credit card':
        return Colors.red;
      case 'debit card':
        return Colors.green;
      case 'net banking':
        return Colors.indigo;
      case 'subscription':
        return Colors.purple;
      default:
        return Colors.grey;
    }
  }

  IconData _getPaymentMethodIcon(String method) {
    switch (method.toLowerCase()) {
      case 'upi':
        return Icons.account_balance_wallet;
      case 'credit card':
      case 'debit card':
        return Icons.credit_card;
      case 'net banking':
        return Icons.account_balance;
      case 'subscription':
        return Icons.subscriptions;
      default:
        return Icons.payment;
    }
  }
}
