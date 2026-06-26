import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../auth/providers.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = ref.watch(authControllerProvider).state.user;

    return Scaffold(
      appBar: AppBar(
        title: const Text('RestWell'),
        actions: [
          TextButton(
            onPressed: () => ref.read(authControllerProvider).signOut(),
            child: const Text('Sign out'),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Text('Welcome, ${user?.username ?? 'user'}', style: Theme.of(context).textTheme.headlineSmall),
          const SizedBox(height: 8),
          Text(user?.tenantName ?? 'Platform workspace'),
          const SizedBox(height: 24),
          const Card(
            child: ListTile(
              title: Text('Sprint 0 Foundation'),
              subtitle: Text('JWT auth, tenant context, and API connectivity are active.'),
            ),
          ),
        ],
      ),
    );
  }
}
