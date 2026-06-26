import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

void main() {
  runApp(const ProviderScope(child: RestWellClientApp()));
}

class RestWellClientApp extends StatelessWidget {
  const RestWellClientApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'RestWell Client',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF7A4F2A)),
        useMaterial3: true,
      ),
      home: const ClientHomeScreen(),
    );
  }
}

class ClientHomeScreen extends StatelessWidget {
  const ClientHomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('RestWell')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: const [
          Text('Family services', style: TextStyle(fontSize: 28, fontWeight: FontWeight.w600)),
          SizedBox(height: 16),
          Card(child: ListTile(title: Text('Policies'), subtitle: Text('View cover and beneficiaries'))),
          Card(child: ListTile(title: Text('Memorials'), subtitle: Text('Access service and tribute details'))),
          Card(child: ListTile(title: Text('Support'), subtitle: Text('Contact your funeral provider'))),
        ],
      ),
    );
  }
}
