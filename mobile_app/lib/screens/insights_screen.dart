import 'package:flutter/material.dart';
import '../widgets/predictive_insights_dashboard.dart';

class InsightsScreen extends StatelessWidget {
  const InsightsScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'AI Insights & Predictions',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        backgroundColor: Theme.of(context).colorScheme.primaryContainer,
        elevation: 0,
      ),
      body: const SingleChildScrollView(
        child: PredictiveInsightsDashboard(),
      ),
    );
  }
}
