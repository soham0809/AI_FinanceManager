import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:fl_chart/fl_chart.dart';
import '../providers/transaction_provider.dart';
import '../models/transaction.dart';

class EnhancedAnalyticsDashboard extends StatefulWidget {
  const EnhancedAnalyticsDashboard({Key? key}) : super(key: key);

  @override
  State<EnhancedAnalyticsDashboard> createState() => _EnhancedAnalyticsDashboardState();
}

class _EnhancedAnalyticsDashboardState extends State<EnhancedAnalyticsDashboard> {
  Map<String, dynamic>? _categoryData;
  Map<String, dynamic>? _monthlyTrends;
  Map<String, dynamic>? _insights;
  Map<String, dynamic>? _topVendors;
  bool _isLoading = true;
  String _selectedPeriod = 'This Month';

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
        // Calculate analytics from local data
        _calculateLocalAnalytics(provider.transactions);
      }

      // Try to get server analytics
      try {
        final categoryData = await provider.apiService.getSpendingByCategory();
        final monthlyTrends = await provider.apiService.getMonthlyTrends();
        final insights = await provider.apiService.getSpendingInsights();
        final topVendors = await provider.apiService.getTopVendors();

        if (mounted) {
          setState(() {
            _categoryData = categoryData;
            _monthlyTrends = monthlyTrends;
            _insights = insights;
            _topVendors = topVendors;
            _isLoading = false;
          });
        }
      } catch (e) {
        // Use local analytics if server fails
        if (mounted) {
          setState(() {
            _isLoading = false;
          });
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  void _calculateLocalAnalytics(List<Transaction> transactions) {
    final now = DateTime.now();
    final thisMonth = transactions.where((t) {
      final date = t.parsedDate;
      return date.year == now.year && date.month == now.month;
    }).toList();

    // Calculate category spending
    final categorySpending = <String, double>{};
    final vendorSpending = <String, double>{};
    
    for (final transaction in thisMonth) {
      if (transaction.isDebit) {
        final category = transaction.category ?? 'Others';
        categorySpending[category] = (categorySpending[category] ?? 0) + transaction.amount;
        vendorSpending[transaction.vendor] = (vendorSpending[transaction.vendor] ?? 0) + transaction.amount;
      }
    }

    // Set local analytics
    _categoryData = {
      'success': true,
      'categories': categorySpending.map((k, v) => MapEntry(k, {
        'total_amount': v,
        'transaction_count': thisMonth.where((t) => t.category == k).length,
      }))
    };

    _topVendors = {
      'success': true,
      'vendors': vendorSpending.entries
          .toList()
          ..sort((a, b) => b.value.compareTo(a.value))
    };
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(),
            SizedBox(height: 16),
            Text('Loading analytics...'),
          ],
        ),
      );
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeader(),
          const SizedBox(height: 20),
          _buildQuickStats(),
          const SizedBox(height: 20),
          _buildSpendingOverview(),
          const SizedBox(height: 20),
          _buildCategoryBreakdown(),
          const SizedBox(height: 20),
          _buildTopVendors(),
          const SizedBox(height: 20),
          _buildMonthlyTrends(),
          const SizedBox(height: 20),
          _buildInsights(),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.blue.shade600, Colors.blue.shade800],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.blue.withOpacity(0.3),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        children: [
          const Icon(Icons.analytics, color: Colors.white, size: 32),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Financial Analytics',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  'AI-Powered Insights',
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.8),
                    fontSize: 14,
                  ),
                ),
              ],
            ),
          ),
          DropdownButton<String>(
            value: _selectedPeriod,
            dropdownColor: Colors.blue.shade700,
            style: const TextStyle(color: Colors.white),
            underline: Container(),
            items: ['This Week', 'This Month', 'Last 3 Months', 'This Year']
                .map((period) => DropdownMenuItem(
                      value: period,
                      child: Text(period),
                    ))
                .toList(),
            onChanged: (value) {
              setState(() {
                _selectedPeriod = value!;
              });
            },
          ),
        ],
      ),
    );
  }

  Widget _buildQuickStats() {
    final provider = Provider.of<TransactionProvider>(context);
    final transactions = provider.transactions;
    
    final totalSpent = transactions
        .where((t) => t.isDebit)
        .fold(0.0, (sum, t) => sum + t.amount);
    
    final totalEarned = transactions
        .where((t) => t.isCredit)
        .fold(0.0, (sum, t) => sum + t.amount);
    
    final thisMonthSpent = transactions
        .where((t) => t.isDebit && _isThisMonth(t.parsedDate))
        .fold(0.0, (sum, t) => sum + t.amount);
    
    final avgTransaction = transactions.isNotEmpty 
        ? totalSpent / transactions.where((t) => t.isDebit).length
        : 0.0;

    return Row(
      children: [
        Expanded(child: _buildStatCard('Total Spent', '₹${totalSpent.toStringAsFixed(0)}', Icons.trending_down, Colors.red)),
        const SizedBox(width: 12),
        Expanded(child: _buildStatCard('Total Earned', '₹${totalEarned.toStringAsFixed(0)}', Icons.trending_up, Colors.green)),
        const SizedBox(width: 12),
        Expanded(child: _buildStatCard('This Month', '₹${thisMonthSpent.toStringAsFixed(0)}', Icons.calendar_month, Colors.blue)),
        const SizedBox(width: 12),
        Expanded(child: _buildStatCard('Avg/Transaction', '₹${avgTransaction.toStringAsFixed(0)}', Icons.analytics, Colors.orange)),
      ],
    );
  }

  Widget _buildStatCard(String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          Text(
            title,
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey[600],
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildSpendingOverview() {
    final provider = Provider.of<TransactionProvider>(context);
    final transactions = provider.transactions;
    
    final last7Days = List.generate(7, (index) {
      final date = DateTime.now().subtract(Duration(days: 6 - index));
      final daySpending = transactions
          .where((t) => t.isDebit && _isSameDay(t.parsedDate, date))
          .fold(0.0, (sum, t) => sum + t.amount);
      return FlSpot(index.toDouble(), daySpending);
    });

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.show_chart, color: Colors.blue.shade600),
              const SizedBox(width: 8),
              const Text(
                'Spending Trend (Last 7 Days)',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
            ],
          ),
          const SizedBox(height: 20),
          SizedBox(
            height: 200,
            child: LineChart(
              LineChartData(
                gridData: FlGridData(show: true, drawVerticalLine: false),
                titlesData: FlTitlesData(
                  leftTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      reservedSize: 40,
                      getTitlesWidget: (value, meta) => Text(
                        '₹${value.toInt()}',
                        style: const TextStyle(fontSize: 10),
                      ),
                    ),
                  ),
                  bottomTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      getTitlesWidget: (value, meta) {
                        final days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
                        return Text(
                          days[value.toInt() % 7],
                          style: const TextStyle(fontSize: 10),
                        );
                      },
                    ),
                  ),
                  topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                  rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                ),
                borderData: FlBorderData(show: false),
                lineBarsData: [
                  LineChartBarData(
                    spots: last7Days,
                    isCurved: true,
                    color: Colors.blue.shade600,
                    barWidth: 3,
                    dotData: const FlDotData(show: true),
                    belowBarData: BarAreaData(
                      show: true,
                      color: Colors.blue.shade100,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCategoryBreakdown() {
    if (_categoryData == null || !(_categoryData!['success'] ?? false)) {
      return _buildEmptyCard('Category Breakdown', 'No category data available');
    }

    final categories = _categoryData!['categories'] as Map<String, dynamic>;
    final categoryList = categories.entries.toList()
      ..sort((a, b) => (b.value['total_amount'] as double).compareTo(a.value['total_amount'] as double));

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.pie_chart, color: Colors.green.shade600),
              const SizedBox(width: 8),
              const Text(
                'Spending by Category',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
            ],
          ),
          const SizedBox(height: 20),
          SizedBox(
            height: 250,
            child: Row(
              children: [
                Expanded(
                  flex: 3,
                  child: PieChart(
                    PieChartData(
                      sections: categoryList.asMap().entries.map((entry) {
                        final index = entry.key;
                        final category = entry.value;
                        final colors = [
                          Colors.blue, Colors.green, Colors.orange, Colors.red,
                          Colors.purple, Colors.teal, Colors.pink, Colors.indigo
                        ];
                        return PieChartSectionData(
                          value: category.value['total_amount'].toDouble(),
                          title: '${((category.value['total_amount'] / categoryList.fold(0.0, (sum, e) => sum + e.value['total_amount'])) * 100).toStringAsFixed(1)}%',
                          color: colors[index % colors.length],
                          radius: 60,
                          titleStyle: const TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        );
                      }).toList(),
                      centerSpaceRadius: 40,
                      sectionsSpace: 2,
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  flex: 2,
                  child: SingleChildScrollView(
                    child: Column(
                      children: categoryList.asMap().entries.map((entry) {
                        final index = entry.key;
                        final category = entry.value;
                        final colors = [
                          Colors.blue, Colors.green, Colors.orange, Colors.red,
                          Colors.purple, Colors.teal, Colors.pink, Colors.indigo
                        ];
                        return Padding(
                          padding: const EdgeInsets.symmetric(vertical: 4),
                          child: Row(
                            children: [
                              Container(
                                width: 16,
                                height: 16,
                                decoration: BoxDecoration(
                                  color: colors[index % colors.length],
                                  shape: BoxShape.circle,
                                ),
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      category.key,
                                      style: const TextStyle(
                                        fontSize: 12,
                                        fontWeight: FontWeight.w500,
                                      ),
                                    ),
                                    Text(
                                      '₹${category.value['total_amount'].toStringAsFixed(0)} (${category.value['transaction_count']} txns)',
                                      style: TextStyle(
                                        fontSize: 10,
                                        color: Colors.grey[600],
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ),
                        );
                      }).toList(),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTopVendors() {
    if (_topVendors == null || !(_topVendors!['success'] ?? false)) {
      return _buildEmptyCard('Top Vendors', 'No vendor data available');
    }

    final vendors = _topVendors!['vendors'] as List<MapEntry<String, double>>;
    final topVendors = vendors.take(5).toList();

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.store, color: Colors.purple.shade600),
              const SizedBox(width: 8),
              const Text(
                'Top Vendors',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
            ],
          ),
          const SizedBox(height: 16),
          ...topVendors.asMap().entries.map((entry) {
            final index = entry.key;
            final vendor = entry.value;
            final maxAmount = topVendors.first.value;
            final percentage = vendor.value / maxAmount;
            
            return Padding(
              padding: const EdgeInsets.symmetric(vertical: 8),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        vendor.key,
                        style: const TextStyle(fontWeight: FontWeight.w500),
                      ),
                      Text(
                        '₹${vendor.value.toStringAsFixed(0)}',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          color: Colors.grey[700],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  LinearProgressIndicator(
                    value: percentage,
                    backgroundColor: Colors.grey[200],
                    valueColor: AlwaysStoppedAnimation<Color>(
                      [Colors.blue, Colors.green, Colors.orange, Colors.red, Colors.purple][index],
                    ),
                  ),
                ],
              ),
            );
          }).toList(),
        ],
      ),
    );
  }

  Widget _buildMonthlyTrends() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.timeline, color: Colors.teal.shade600),
              const SizedBox(width: 8),
              const Text(
                'Monthly Trends',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
            ],
          ),
          const SizedBox(height: 16),
          const Text(
            'Coming soon: Advanced monthly spending analysis with AI predictions',
            style: TextStyle(color: Colors.grey),
          ),
        ],
      ),
    );
  }

  Widget _buildInsights() {
    final provider = Provider.of<TransactionProvider>(context);
    final transactions = provider.transactions;
    
    final insights = _generateInsights(transactions);

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.lightbulb, color: Colors.amber.shade600),
              const SizedBox(width: 8),
              const Text(
                'AI Insights',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
            ],
          ),
          const SizedBox(height: 16),
          ...insights.map((insight) => Padding(
            padding: const EdgeInsets.symmetric(vertical: 4),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(Icons.arrow_right, color: Colors.blue.shade600, size: 16),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    insight,
                    style: const TextStyle(fontSize: 14),
                  ),
                ),
              ],
            ),
          )).toList(),
        ],
      ),
    );
  }

  Widget _buildEmptyCard(String title, String message) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        children: [
          Text(
            title,
            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),
          Text(
            message,
            style: TextStyle(color: Colors.grey[600]),
          ),
        ],
      ),
    );
  }

  List<String> _generateInsights(List<Transaction> transactions) {
    final insights = <String>[];
    
    if (transactions.isEmpty) {
      insights.add('No transactions found. Start by scanning your SMS messages!');
      return insights;
    }

    final thisMonth = transactions.where((t) => _isThisMonth(t.parsedDate)).toList();
    final lastMonth = transactions.where((t) => _isLastMonth(t.parsedDate)).toList();
    
    final thisMonthSpending = thisMonth.where((t) => t.isDebit).fold(0.0, (sum, t) => sum + t.amount);
    final lastMonthSpending = lastMonth.where((t) => t.isDebit).fold(0.0, (sum, t) => sum + t.amount);
    
    if (lastMonthSpending > 0) {
      final change = ((thisMonthSpending - lastMonthSpending) / lastMonthSpending * 100);
      if (change > 10) {
        insights.add('Your spending increased by ${change.toStringAsFixed(1)}% this month. Consider reviewing your expenses.');
      } else if (change < -10) {
        insights.add('Great job! You reduced spending by ${(-change).toStringAsFixed(1)}% this month.');
      } else {
        insights.add('Your spending is stable compared to last month.');
      }
    }

    final categorySpending = <String, double>{};
    for (final t in thisMonth.where((t) => t.isDebit)) {
      categorySpending[t.category ?? 'Others'] = (categorySpending[t.category ?? 'Others'] ?? 0) + t.amount;
    }
    
    if (categorySpending.isNotEmpty) {
      final topCategory = categorySpending.entries.reduce((a, b) => a.value > b.value ? a : b);
      insights.add('Your highest spending category is ${topCategory.key} (₹${topCategory.value.toStringAsFixed(0)}).');
    }

    final avgTransaction = thisMonth.where((t) => t.isDebit).isNotEmpty 
        ? thisMonthSpending / thisMonth.where((t) => t.isDebit).length
        : 0;
    
    if (avgTransaction > 1000) {
      insights.add('Your average transaction is ₹${avgTransaction.toStringAsFixed(0)}. Consider smaller, more frequent purchases.');
    }

    insights.add('You have ${transactions.length} total transactions tracked by AI.');
    
    return insights;
  }

  bool _isThisMonth(DateTime date) {
    final now = DateTime.now();
    return date.year == now.year && date.month == now.month;
  }

  bool _isLastMonth(DateTime date) {
    final now = DateTime.now();
    final lastMonth = DateTime(now.year, now.month - 1);
    return date.year == lastMonth.year && date.month == lastMonth.month;
  }

  bool _isSameDay(DateTime date1, DateTime date2) {
    return date1.year == date2.year && date1.month == date2.month && date1.day == date2.day;
  }
}
