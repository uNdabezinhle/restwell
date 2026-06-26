import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'src/auth/auth_controller.dart';
import 'src/auth/providers.dart';
import 'src/features/auth/login_screen.dart';
import 'src/features/dashboard/dashboard_screen.dart';

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
      home: const AuthGate(),
    );
  }
}

class AuthGate extends ConsumerWidget {
  const AuthGate({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final status = ref.watch(authControllerProvider).state.status;
    if (status == AuthStatus.signedIn) {
      return const DashboardScreen();
    }
    return const LoginScreen();
  }
}
