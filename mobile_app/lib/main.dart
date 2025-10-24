import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'providers/transaction_provider.dart';
import 'services/api_service.dart';
import 'services/auth_service.dart';
import 'screens/main_navigation.dart';
import 'screens/auth/login_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await AuthService.initialize();
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(
          create: (context) => TransactionProvider(ApiService()),
        ),
      ],
      child: MaterialApp(
        title: 'AI Financial Co-Pilot',
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
          useMaterial3: true,
        ),
        home: AuthService.isLoggedIn ? const MainNavigation() : const LoginScreen(),
        debugShowCheckedModeBanner: false,
      ),
    );
  }
}
