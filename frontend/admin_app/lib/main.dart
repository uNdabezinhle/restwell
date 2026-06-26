import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

void main() {
  runApp(const ProviderScope(child: RestWellAdminApp()));
}

class RestWellAdminApp extends StatelessWidget {
  const RestWellAdminApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'RestWell Admin',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF23675A)),
        useMaterial3: true,
      ),
      home: const LoginScreen(),
    );
  }
}

class LoginScreen extends StatelessWidget {
  const LoginScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 420),
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text('RestWell', style: Theme.of(context).textTheme.headlineMedium),
                const SizedBox(height: 8),
                Text('Admin and staff workspace', style: Theme.of(context).textTheme.bodyLarge),
                const SizedBox(height: 24),
                const TextField(decoration: InputDecoration(labelText: 'Email')),
                const SizedBox(height: 12),
                const TextField(obscureText: true, decoration: InputDecoration(labelText: 'Password')),
                const SizedBox(height: 24),
                FilledButton(onPressed: () {}, child: const Text('Sign in')),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
