import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:fl_chart/fl_chart.dart';
import '../providers/transaction_provider.dart';

class PredictiveInsightsDashboard extends StatefulWidget {
  const PredictiveInsightsDashboard({Key? key}) : super(key: key);

  @override
  State<PredictiveInsightsDashboard> createState() => _PredictiveInsightsDashboardState();
}

class _PredictiveInsightsDashboardState extends State<PredictiveInsightsDashboard> {
  Map<String, dynamic>? _forecasts;
  Map<String, dynamic>? _insights;
  Map<String, dynamic>? _savingsGoal;
  List<dynamic>? _budgetAlerts;
  bool _isLoading = true;
  bool _modelsTraining = false;

  @override
  void initState() {
    super.initState();
    _loadPredictiveData();
  }

  Future<void> _loadPredictiveData() async {
    setState(() {
      _isLoading = true;
    });

    try {
      final provider = Provider.of<TransactionProvider>(context, listen: false);
      
      // Use offline insights instead of API calls
      final offlineInsights = provider.offlineInsights;
      final totalSpent = provider.totalSpending;
      final dailyAvg = provider.dailyAverageSpending;
      final categorySpending = provider.spendingByCategory;
      
      // Generate offline forecasts
      final monthlyForecast = dailyAvg * 30;
      final weeklyForecast = dailyAvg * 7;
      
      // Build forecast data
      final forecasts = {
        'monthly_forecast': monthlyForecast,
        'weekly_forecast': weeklyForecast,
        'confidence': 0.85,
        'trend': totalSpent > monthlyForecast ? 'increasing' : 'stable',
      };
      
      // Build insights data with actionable recommendations
      final insights = {
        'insights': offlineInsights,
        'recommendations': _generateRecommendations(categorySpending, totalSpent, dailyAvg),
        'budget_status': _getBudgetStatus(totalSpent, monthlyForecast),
      };

      if (mounted) {
        setState(() {
          _forecasts = forecasts;
          _insights = insights;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to load predictions: $e')),
      );
    }
  }

  List<String> _generateRecommendations(Map<String, double> categorySpending, double totalSpent, double dailyAvg) {
    final recommendations = <String>[];
    
    if (totalSpent > 0) {
      // Food spending recommendations
      if (categorySpending['Food & Dining'] != null && categorySpending['Food & Dining']! > totalSpent * 0.3) {
        recommendations.add('🍽️ Consider meal planning to reduce food expenses');
        recommendations.add('🏠 Cook at home more often to save money');
      }
      
      // Transportation recommendations
      if (categorySpending['Transportation'] != null && categorySpending['Transportation']! > totalSpent * 0.25) {
        recommendations.add('🚌 Use public transport or carpooling to reduce costs');
        recommendations.add('🚴 Consider cycling for short distances');
      }
      
      // Education spending insights
      if (categorySpending['Education'] != null) {
        recommendations.add('📚 Great job investing in education!');
        recommendations.add('💡 Look for scholarships and educational discounts');
      }
      
      // General savings recommendations
      if (dailyAvg > 500) {
        recommendations.add('💰 Set up automatic savings of ₹${(dailyAvg * 0.1).toStringAsFixed(0)}/day');
      }
      
      recommendations.add('📊 Track expenses daily for better control');
      recommendations.add('🎯 Set monthly budget limits for each category');
    }
    
    return recommendations.isEmpty ? ['📱 Add more transactions for personalized recommendations'] : recommendations;
  }

  String _getBudgetStatus(double totalSpent, double monthlyForecast) {
    if (totalSpent < monthlyForecast * 0.7) {
      return 'On Track';
    } else if (totalSpent < monthlyForecast) {
      return 'Watch Spending';
    } else {
      return 'Over Budget';
    }
  }

  Future<void> _trainModels() async {
    setState(() {
      _modelsTraining = true;
    });

    try {
      final provider = Provider.of<TransactionProvider>(context, listen: false);
      final result = await provider.apiService.trainPredictionModels();
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Models trained for ${result['categories_trained'].length} categories!'),
          backgroundColor: Colors.green,
        ),
      );
      
      // Reload data after training
      _loadPredictiveData();
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to train models: $e')),
      );
    } finally {
      if (mounted) {
        setState(() {
          _modelsTraining = false;
        });
      }
    }
  }

  Future<void> _createSavingsGoal() async {
    final result = await showDialog<Map<String, double>>(
      context: context,
      builder: (context) => _SavingsGoalDialog(),
    );

    if (result != null) {
      try {
        final provider = Provider.of<TransactionProvider>(context, listen: false);
        final goal = await provider.apiService.createSavingsGoal(
          targetAmount: result['target']!,
          targetMonths: result['months']!.toInt(),
          currentIncome: result['income']!,
          currentExpenses: result['expenses']!,
        );

        if (mounted) {
          setState(() {
            _savingsGoal = goal;
          });
        }

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Savings goal created successfully!'),
            backgroundColor: Colors.green,
          ),
        );
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to create savings goal: $e')),
        );
      }
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
                const Icon(Icons.psychology, color: Colors.deepPurple),
                const SizedBox(width: 8),
                const Text(
                  'AI Predictive Insights',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                IconButton(
                  icon: const Icon(Icons.refresh),
                  onPressed: _loadPredictiveData,
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Train Models Button
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: _modelsTraining ? null : _trainModels,
                icon: _modelsTraining
                    ? const SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.model_training),
                label: Text(_modelsTraining ? 'Training Models...' : 'Train AI Models'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.deepPurple,
                  foregroundColor: Colors.white,
                ),
              ),
            ),
            const SizedBox(height: 20),

            if (_isLoading)
              const Center(
                child: Padding(
                  padding: EdgeInsets.all(32),
                  child: CircularProgressIndicator(),
                ),
              )
            else ...[
              // Financial Insights
              if (_insights != null) _buildFinancialInsights(),
              const SizedBox(height: 20),

              // Spending Forecasts
              if (_forecasts != null) _buildSpendingForecasts(),
              const SizedBox(height: 20),

              // Savings Goal Section
              _buildSavingsGoalSection(),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildFinancialInsights() {
    final insights = _insights!['insights'] as List<String>;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'AI Financial Insights',
          style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
        ),
        const SizedBox(height: 12),
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.blue.withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.blue.withOpacity(0.3)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: insights.map((insight) {
              return Padding(
                padding: const EdgeInsets.symmetric(vertical: 4),
                child: Row(
                  children: [
                    Icon(
                      _getInsightIconFromText(insight),
                      color: Colors.blue,
                      size: 16,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        insight,
                        style: const TextStyle(fontSize: 14),
                      ),
                    ),
                  ],
                ),
              );
            }).toList(),
          ),
        ),
      ],
    );
  }

  IconData _getInsightIconFromText(String insight) {
    if (insight.contains('💰') || insight.contains('spending')) {
      return Icons.trending_up;
    } else if (insight.contains('📊') || insight.contains('average')) {
      return Icons.analytics;
    } else if (insight.contains('🏆') || insight.contains('category')) {
      return Icons.pie_chart;
    } else if (insight.contains('🍽️') || insight.contains('food')) {
      return Icons.restaurant;
    } else if (insight.contains('🚗') || insight.contains('transport')) {
      return Icons.directions_car;
    } else if (insight.contains('📚') || insight.contains('education')) {
      return Icons.school;
    } else if (insight.contains('💚') || insight.contains('balance')) {
      return Icons.account_balance_wallet;
    } else if (insight.contains('⚠️') || insight.contains('budget')) {
      return Icons.warning;
    } else {
      return Icons.lightbulb;
    }
  }

  IconData _getInsightIcon(String key) {
    switch (key.toLowerCase()) {
      case 'spending_trend':
        return Icons.trending_up;
      case 'budget_status':
        return Icons.account_balance_wallet;
      case 'savings_potential':
        return Icons.savings;
      case 'category_analysis':
        return Icons.pie_chart;
      default:
        return Icons.lightbulb;
    }
  }

  Widget _buildSpendingForecasts() {
    if (_forecasts == null) return Container();
    
    final monthlyForecast = _forecasts!['monthly_forecast'] as double?;
    final weeklyForecast = _forecasts!['weekly_forecast'] as double?;

    if (monthlyForecast == null || weeklyForecast == null) {
      return Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.orange.withOpacity(0.1),
          borderRadius: BorderRadius.circular(8),
        ),
        child: const Text(
          'No spending forecasts available. Scan SMS messages to generate predictions.',
          style: TextStyle(color: Colors.orange),
        ),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'AI Spending Forecasts',
          style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
        ),
        const SizedBox(height: 12),
        Container(
          margin: const EdgeInsets.only(bottom: 12),
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
                  Icon(
                    Icons.calendar_month,
                    color: Colors.green,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Monthly Forecast',
                      style: const TextStyle(
                        fontWeight: FontWeight.w600,
                        fontSize: 16,
                      ),
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.green,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      '₹${monthlyForecast!.toStringAsFixed(0)}',
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 12,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                'Expected spending for next 30 days',
                style: TextStyle(
                  color: Colors.grey[600],
                  fontSize: 12,
                ),
              ),
            ],
          ),
        ),
        Container(
          margin: const EdgeInsets.only(bottom: 12),
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.blue.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: Colors.blue.withOpacity(0.3)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    Icons.calendar_today,
                    color: Colors.blue,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Weekly Forecast',
                      style: const TextStyle(
                        fontWeight: FontWeight.w600,
                        fontSize: 16,
                      ),
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.blue,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      '₹${weeklyForecast!.toStringAsFixed(0)}',
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 12,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                'Expected spending for next 7 days',
                style: TextStyle(
                  color: Colors.grey[600],
                  fontSize: 12,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  IconData _getCategoryIcon(String category) {
    switch (category) {
      case 'Food & Dining':
        return Icons.restaurant;
      case 'Shopping':
        return Icons.shopping_bag;
      case 'Transportation':
        return Icons.directions_car;
      case 'Entertainment':
        return Icons.movie;
      case 'Healthcare':
        return Icons.medical_services;
      default:
        return Icons.category;
    }
  }

  Color _getTrendColor(String trend) {
    switch (trend) {
      case 'increasing':
        return Colors.red;
      case 'decreasing':
        return Colors.green;
      case 'stable':
        return Colors.blue;
      default:
        return Colors.grey;
    }
  }

  Widget _buildSavingsGoalSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            const Text(
              'Savings Goals',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
            ),
            const Spacer(),
            TextButton.icon(
              onPressed: _createSavingsGoal,
              icon: const Icon(Icons.add),
              label: const Text('Create Goal'),
            ),
          ],
        ),
        const SizedBox(height: 12),
        
        if (_savingsGoal != null)
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: _savingsGoal!['achievable'] 
                  ? Colors.green.withOpacity(0.1)
                  : Colors.orange.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(
                color: _savingsGoal!['achievable'] 
                    ? Colors.green.withOpacity(0.3)
                    : Colors.orange.withOpacity(0.3),
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(
                      _savingsGoal!['achievable'] 
                          ? Icons.check_circle 
                          : Icons.warning,
                      color: _savingsGoal!['achievable'] 
                          ? Colors.green 
                          : Colors.orange,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      'Target: Rs.${_savingsGoal!['target_amount'].toStringAsFixed(0)}',
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  'Monthly Required: Rs.${_savingsGoal!['monthly_required'].toStringAsFixed(0)}',
                  style: const TextStyle(fontSize: 14),
                ),
                const SizedBox(height: 8),
                Text(
                  _savingsGoal!['recommendation'],
                  style: const TextStyle(fontSize: 14),
                ),
              ],
            ),
          )
        else
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.grey.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Colors.grey.withOpacity(0.3)),
            ),
            child: const Text(
              'No savings goals set. Create a goal to get AI-powered savings recommendations!',
              style: TextStyle(color: Colors.grey),
            ),
          ),
      ],
    );
  }
}

class _SavingsGoalDialog extends StatefulWidget {
  @override
  State<_SavingsGoalDialog> createState() => _SavingsGoalDialogState();
}

class _SavingsGoalDialogState extends State<_SavingsGoalDialog> {
  final _targetController = TextEditingController();
  final _monthsController = TextEditingController();
  final _incomeController = TextEditingController();
  final _expensesController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Create Savings Goal'),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: _targetController,
              decoration: const InputDecoration(
                labelText: 'Target Amount (Rs.)',
                prefixIcon: Icon(Icons.savings),
              ),
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _monthsController,
              decoration: const InputDecoration(
                labelText: 'Target Months',
                prefixIcon: Icon(Icons.calendar_month),
              ),
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _incomeController,
              decoration: const InputDecoration(
                labelText: 'Monthly Income (Rs.)',
                prefixIcon: Icon(Icons.account_balance_wallet),
              ),
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _expensesController,
              decoration: const InputDecoration(
                labelText: 'Monthly Expenses (Rs.)',
                prefixIcon: Icon(Icons.money_off),
              ),
              keyboardType: TextInputType.number,
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: () {
            final target = double.tryParse(_targetController.text);
            final months = double.tryParse(_monthsController.text);
            final income = double.tryParse(_incomeController.text);
            final expenses = double.tryParse(_expensesController.text);

            if (target != null && months != null && income != null && expenses != null) {
              Navigator.of(context).pop({
                'target': target,
                'months': months,
                'income': income,
                'expenses': expenses,
              });
            }
          },
          child: const Text('Create Goal'),
        ),
      ],
    );
  }

  @override
  void dispose() {
    _targetController.dispose();
    _monthsController.dispose();
    _incomeController.dispose();
    _expensesController.dispose();
    super.dispose();
  }
}
