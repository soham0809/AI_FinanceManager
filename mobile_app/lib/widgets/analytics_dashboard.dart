import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:fl_chart/fl_chart.dart';
import '../providers/transaction_provider.dart';

class AnalyticsDashboard extends StatefulWidget {
  const AnalyticsDashboard({Key? key}) : super(key: key);

  @override
  State<AnalyticsDashboard> createState() => _AnalyticsDashboardState();
}

class _AnalyticsDashboardState extends State<AnalyticsDashboard> {
  Map<String, dynamic>? _categoryData;
  Map<String, dynamic>? _monthlyTrends;
  Map<String, dynamic>? _insights;
  Map<String, dynamic>? _topVendors;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    // Defer the data loading to after the build phase
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadAnalyticsData();
    });
  }
  
  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    // Defer the data loading to after the build phase
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadAnalyticsData();
    });
  }

  Future<void> _loadAnalyticsData() async {
    setState(() {
      _isLoading = true;
    });

    try {
      final provider = Provider.of<TransactionProvider>(context, listen: false);
      
      // First fetch latest transactions from backend
      await provider.fetchTransactions();
      
      // Check if we have transactions
      if (provider.transactions.isEmpty) {
        setState(() {
          _isLoading = false;
          _categoryData = {'categories': [], 'total_spending': 0.0};
          _monthlyTrends = {'monthly_trends': []};
          _insights = {'total_spending': 0.0, 'net_balance': 0.0, 'average_transaction': 0.0, 'total_transactions': 0};
          _topVendors = {'top_vendors': []};
        });
        return;
      }
      
      // Try to load from backend API first, fallback to offline data
      Map<String, dynamic>? categoryData;
      Map<String, dynamic>? monthlyTrends;
      Map<String, dynamic>? insights;
      Map<String, dynamic>? topVendors;
      
      try {
        // Attempt API calls
        final responses = await Future.wait([
          provider.apiService.getAnalytics('/v1/analytics/spending-by-category'),
          provider.apiService.getAnalytics('/v1/analytics/monthly-trends'),
          provider.apiService.getAnalytics('/v1/analytics/insights'),
          provider.apiService.getAnalytics('/v1/analytics/top-vendors'),
        ]);
        
        categoryData = responses[0];
        monthlyTrends = responses[1];
        insights = responses[2];
        topVendors = responses[3];
        
        // Transform category data for charts
        if (categoryData?['success'] == true && categoryData?['categories'] != null) {
          final categories = categoryData!['categories'] as List;
          final categoryList = categories.map((cat) => [cat[0], cat[1]]).toList();
          categoryData = {
            'categories': categoryList,
            'total_spending': categoryData['total_spending'] ?? 0.0,
          };
        }
        
      } catch (apiError) {
        print('API call failed, using offline data: $apiError');
        
        // Fallback to offline analytics - calculate from current transactions only
        // This prevents overwriting with dummy data
        final categorySpending = <String, double>{};
        final vendorSpending = <String, Map<String, dynamic>>{};
        double totalSpent = 0.0;
        double totalIncome = 0.0;
        
        // Process each transaction to build analytics data
        for (final transaction in provider.transactions) {
          if (transaction.isDebit) {
            final category = transaction.category ?? 'Others';
            categorySpending[category] = (categorySpending[category] ?? 0.0) + transaction.amount;
            totalSpent += transaction.amount;
            
            // Track vendor spending
            final vendor = transaction.vendor;
            if (!vendorSpending.containsKey(vendor)) {
              vendorSpending[vendor] = {
                'total_spending': 0.0, 
                'transaction_count': 0, 
                'vendor': vendor,
                'last_transaction': transaction.date
              };
            }
            vendorSpending[vendor]!['total_spending'] += transaction.amount;
            vendorSpending[vendor]!['transaction_count']++;
          } else if (transaction.isCredit) {
            totalIncome += transaction.amount;
          }
        }
        
        final transactionCount = provider.transactions.length;
        
        // Convert category spending to sorted list for chart
        final topCategories = categorySpending.entries.toList()
          ..sort((a, b) => b.value.compareTo(a.value));
        final categoryList = topCategories.map((entry) => [entry.key, entry.value]).toList();
        
        categoryData = {
          'categories': categoryList,
          'total_spending': totalSpent,
        };
        
        // Build insights data
        insights = {
          'total_spending': totalSpent,
          'total_income': totalIncome,
          'net_balance': totalIncome - totalSpent,
          'average_transaction': transactionCount > 0 ? totalSpent / transactionCount : 0.0,
          'total_transactions': transactionCount,
        };
        
        final topVendorsList = vendorSpending.values.toList()
          ..sort((a, b) => b['total_spending'].compareTo(a['total_spending']));

        topVendors = {'top_vendors': topVendorsList.take(5).toList()};
        monthlyTrends = {'monthly_trends': []};
      }

      setState(() {
        _categoryData = categoryData;
        _monthlyTrends = monthlyTrends;
        _insights = insights;
        _topVendors = topVendors;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to load analytics: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<TransactionProvider>(
      builder: (context, provider, child) {
        return Card(
          margin: const EdgeInsets.all(16),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(Icons.analytics, color: Colors.blue),
                    const SizedBox(width: 8),
                    const Text(
                      'Analytics Dashboard',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const Spacer(),
                    IconButton(
                      icon: const Icon(Icons.refresh),
                      onPressed: _loadAnalyticsData,
                    ),
                  ],
                ),
                const SizedBox(height: 16),

                if (_isLoading)
                  const Center(
                    child: Padding(
                      padding: EdgeInsets.all(32),
                      child: CircularProgressIndicator(),
                    ),
                  )
                else ...[
                  // Insights Cards
                  if (_insights != null) _buildInsightsCards(),
                  const SizedBox(height: 20),

                  // Category Spending Pie Chart
                  if (_categoryData != null) _buildCategoryPieChart(),
                  const SizedBox(height: 20),

                  // Monthly Trends Line Chart
                  if (_monthlyTrends != null) _buildMonthlyTrendsChart(),
                  const SizedBox(height: 20),

                  // Top Vendors
                  if (_topVendors != null) _buildTopVendors(),
                ],
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildInsightsCards() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Quick Insights',
          style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: _buildInsightCard(
                'Total Spent',
                'Rs.${(_insights?['total_spending'] ?? 0.0).toStringAsFixed(0)}',
                Icons.trending_down,
                Colors.red,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildInsightCard(
                'Net Balance',
                'Rs.${(_insights?['net_balance'] ?? 0.0).toStringAsFixed(0)}',
                Icons.account_balance_wallet,
                (_insights?['net_balance'] ?? 0.0) >= 0 ? Colors.green : Colors.red,
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: _buildInsightCard(
                'Avg Transaction',
                'Rs.${(_insights?['average_transaction'] ?? 0.0).toStringAsFixed(0)}',
                Icons.receipt,
                Colors.blue,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildInsightCard(
                'Transactions',
                '${_insights?['total_transactions'] ?? 0}',
                Icons.list_alt,
                Colors.purple,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildInsightCard(String title, String value, IconData icon, Color color) {
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
              Expanded(
                child: Text(
                  title,
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[600],
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCategoryPieChart() {
    final categories = (_categoryData?['categories'] as List<dynamic>?) ?? [];
    if (categories.isEmpty) {
      return const Center(child: Text('No spending data available'));
    }

    final colors = [
      Colors.blue,
      Colors.red,
      Colors.green,
      Colors.orange,
      Colors.purple,
      Colors.teal,
      Colors.pink,
      Colors.indigo,
      Colors.amber,
      Colors.cyan,
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Spending by Category',
          style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
        ),
        const SizedBox(height: 16),
        SizedBox(
          height: 250,
          child: Row(
            children: [
              Expanded(
                flex: 3,
                child: PieChart(
                  PieChartData(
                    sections: categories.asMap().entries.map((entry) {
                      final index = entry.key;
                      final category = entry.value;
                      final totalSpending = (_categoryData?['total_spending'] ?? 1.0);
                      final percentage = (category[1] / totalSpending) * 100;
                      
                      return PieChartSectionData(
                        color: colors[index % colors.length],
                        value: category[1].toDouble(),
                        title: '${percentage.toStringAsFixed(1)}%',
                        radius: 80,
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
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: categories.asMap().entries.map((entry) {
                    final index = entry.key;
                    final category = entry.value;
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
                                  category[0],
                                  style: const TextStyle(
                                    fontSize: 12,
                                    fontWeight: FontWeight.w500,
                                  ),
                                ),
                                Text(
                                  'Rs.${category[1].toStringAsFixed(0)}',
                                  style: TextStyle(
                                    fontSize: 11,
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
    );
  }

  Widget _buildMonthlyTrendsChart() {
    final monthlyData = (_monthlyTrends?['monthly_trends'] as List<dynamic>?) ?? [];
    if (monthlyData.isEmpty) {
      return const Center(child: Text('No monthly trend data available'));
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Monthly Spending Trends',
          style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
        ),
        const SizedBox(height: 16),
        SizedBox(
          height: 200,
          child: LineChart(
            LineChartData(
              gridData: FlGridData(show: true),
              titlesData: FlTitlesData(
                leftTitles: AxisTitles(
                  sideTitles: SideTitles(
                    showTitles: true,
                    reservedSize: 60,
                    getTitlesWidget: (value, meta) {
                      return Text(
                        'Rs.${(value / 1000).toStringAsFixed(0)}K',
                        style: const TextStyle(fontSize: 10),
                      );
                    },
                  ),
                ),
                bottomTitles: AxisTitles(
                  sideTitles: SideTitles(
                    showTitles: true,
                    getTitlesWidget: (value, meta) {
                      final index = value.toInt();
                      if (index >= 0 && index < monthlyData.length) {
                        return Text(
                          monthlyData[index]['month_name'] ?? '',
                          style: const TextStyle(fontSize: 10),
                        );
                      }
                      return const Text('');
                    },
                  ),
                ),
                topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
              ),
              borderData: FlBorderData(show: true),
              lineBarsData: [
                LineChartBarData(
                  spots: monthlyData.asMap().entries.map((entry) {
                    return FlSpot(
                      entry.key.toDouble(),
                      (entry.value['total_spending'] ?? 0.0).toDouble(),
                    );
                  }).toList(),
                  isCurved: true,
                  color: Colors.blue,
                  barWidth: 3,
                  dotData: FlDotData(show: true),
                  belowBarData: BarAreaData(
                    show: true,
                    color: Colors.blue.withOpacity(0.1),
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildTopVendors() {
    final vendors = (_topVendors?['top_vendors'] as List<dynamic>?) ?? [];
    if (vendors.isEmpty) {
      return const Center(child: Text('No vendor data available'));
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Top Spending Vendors',
          style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
        ),
        const SizedBox(height: 12),
        ...vendors.map((vendor) {
          return Container(
            margin: const EdgeInsets.only(bottom: 8),
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.grey[50],
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Colors.grey[300]!),
            ),
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        vendor['vendor'] ?? 'Unknown',
                        style: const TextStyle(
                          fontWeight: FontWeight.w500,
                          fontSize: 14,
                        ),
                      ),
                      Text(
                        '${vendor['transaction_count'] ?? 0} transactions',
                        style: TextStyle(
                          color: Colors.grey[600],
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ),
                Text(
                  'Rs.${(vendor['total_spending'] ?? 0.0).toStringAsFixed(0)}',
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 14,
                    color: Colors.red,
                  ),
                ),
              ],
            ),
          );
        }).toList(),
      ],
    );
  }
}
