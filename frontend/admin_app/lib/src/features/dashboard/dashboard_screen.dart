import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../api/restwell_api_client.dart';
import '../../auth/providers.dart';

class DashboardScreen extends ConsumerStatefulWidget {
  const DashboardScreen({super.key});

  @override
  ConsumerState<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends ConsumerState<DashboardScreen> {
  var _selectedIndex = 0;
  late Future<_DashboardData> _dashboardFuture;

  static const _modules = [
    _ModuleConfig('Overview', Icons.dashboard_outlined, ''),
    _ModuleConfig(
        'Branches', Icons.account_tree_outlined, '/api/tenants/branches/'),
    _ModuleConfig('Cases', Icons.assignment_outlined, '/api/cases/'),
    _ModuleConfig('Deceased', Icons.person_outline, '/api/cases/deceased/'),
    _ModuleConfig(
        'Policies', Icons.verified_user_outlined, '/api/policies/templates/'),
    _ModuleConfig(
        'Financials', Icons.payments_outlined, '/api/financials/invoices/'),
    _ModuleConfig(
        'Inventory', Icons.inventory_2_outlined, '/api/inventory/items/'),
    _ModuleConfig(
        'Scheduling', Icons.event_outlined, '/api/scheduling/events/'),
    _ModuleConfig(
        'Mortuary', Icons.local_hospital_outlined, '/api/mortuary/records/'),
    _ModuleConfig(
        'Routes', Icons.map_outlined, '/api/geolocation/routes/active/'),
    _ModuleConfig(
        'Branding', Icons.palette_outlined, '/api/branding/settings/'),
    _ModuleConfig('Website', Icons.language_outlined, '/api/websites/pages/'),
    _ModuleConfig('Apps', Icons.android_outlined, '/api/branded-apps/configs/'),
    _ModuleConfig(
        'Onboarding', Icons.school_outlined, '/api/onboarding/tasks/'),
    _ModuleConfig(
        'Help', Icons.help_outline, '/api/onboarding/published-articles/'),
  ];

  @override
  void initState() {
    super.initState();
    _dashboardFuture = _loadDashboard();
  }

  Future<_DashboardData> _loadDashboard() async {
    final api = ref.read(apiClientProvider);
    final results = <String, List<Map<String, dynamic>>>{};
    for (final module in _modules.where((module) => module.path.isNotEmpty)) {
      try {
        results[module.title] = await api.fetchList(module.path);
      } on DioException {
        results[module.title] = const [];
      }
    }
    return _DashboardData(results);
  }

  void _refresh() {
    setState(() {
      _dashboardFuture = _loadDashboard();
    });
  }

  Future<void> _createOnboardingTask() async {
    final titleController = TextEditingController();
    final descriptionController = TextEditingController();
    final result = await showDialog<Map<String, String>>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('New onboarding task'),
          content: SizedBox(
            width: 420,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: titleController,
                  decoration: const InputDecoration(labelText: 'Title'),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: descriptionController,
                  maxLines: 3,
                  decoration: const InputDecoration(labelText: 'Description'),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('Cancel')),
            FilledButton(
              onPressed: () {
                final title = titleController.text.trim();
                if (title.isEmpty) {
                  return;
                }
                Navigator.pop(context, {
                  'title': title,
                  'description': descriptionController.text.trim(),
                });
              },
              child: const Text('Create'),
            ),
          ],
        );
      },
    );

    titleController.dispose();
    descriptionController.dispose();
    if (result == null) {
      return;
    }

    await _runAction(
      () => ref.read(apiClientProvider).create('/api/onboarding/tasks/', {
        'title': result['title'],
        'description': result['description'],
        'category': 'platform_setup',
        'is_required': true,
        'sort_order': 10,
      }),
      'Onboarding task created.',
    );
  }

  Future<void> _seedOnboardingTasks() async {
    final api = ref.read(apiClientProvider);
    final tasks = [
      (
        'Confirm tenant profile',
        'Check legal name, branch, and admin users.',
        'platform_setup'
      ),
      (
        'Upload brand assets',
        'Add logo, colors, SMS sender, and support email.',
        'branding'
      ),
      (
        'Create staff users',
        'Invite operational users and assign branches.',
        'users'
      ),
      (
        'Run first case workflow',
        'Create a sample case and complete the service workflow.',
        'training'
      ),
    ];

    await _runAction(() async {
      for (final task in tasks) {
        await api.create('/api/onboarding/tasks/', {
          'title': task.$1,
          'description': task.$2,
          'category': task.$3,
          'is_required': true,
          'sort_order': tasks.indexOf(task) + 1,
        });
      }
      return {};
    }, 'Demo onboarding checklist created.');
  }

  Future<void> _createBranding() async {
    await _runAction(
      () => ref.read(apiClientProvider).create('/api/branding/settings/', {
        'primary_color': '#0F766E',
        'secondary_color': '#2563EB',
        'email_from_name': 'RestWell Demo',
        'sms_sender_name': 'RESTWELL',
        'remove_powered_by': false,
        'is_active': true,
      }),
      'Branding settings created.',
    );
  }

  Future<void> _createWebsiteShell() async {
    await _runAction(
      () => ref.read(apiClientProvider).create('/api/websites/sites/', {
        'name': 'RestWell Demo',
        'subdomain': 'restwell-demo',
        'is_published': true,
      }),
      'Website shell created.',
    );
  }

  Future<void> _completeTask(int id) async {
    await _runAction(
      () => ref
          .read(apiClientProvider)
          .post('/api/onboarding/tasks/$id/complete/'),
      'Task completed.',
    );
  }

  Future<void> _runAction(Future<Map<String, dynamic>> Function() action,
      String successMessage) async {
    try {
      await action();
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text(successMessage)));
      _refresh();
    } on DioException catch (error) {
      if (!mounted) {
        return;
      }
      final message = error.response?.data?.toString() ??
          'The action could not be completed.';
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text(message)));
    }
  }

  @override
  Widget build(BuildContext context) {
    final user = ref.watch(authControllerProvider).state.user;
    final selectedModule = _modules[_selectedIndex];

    return Scaffold(
      appBar: AppBar(
        title: const Text('RestWell Admin'),
        actions: [
          IconButton(
            tooltip: 'Refresh',
            onPressed: _refresh,
            icon: const Icon(Icons.refresh),
          ),
          TextButton.icon(
            onPressed: () => ref.read(authControllerProvider).signOut(),
            icon: const Icon(Icons.logout),
            label: const Text('Sign out'),
          ),
        ],
      ),
      body: Row(
        children: [
          SizedBox(
            width: 224,
            child: ListView.builder(
              padding: const EdgeInsets.all(12),
              itemCount: _modules.length,
              itemBuilder: (context, index) {
                final module = _modules[index];
                return Padding(
                  padding: const EdgeInsets.only(bottom: 4),
                  child: ListTile(
                    selected: _selectedIndex == index,
                    selectedTileColor:
                        Theme.of(context).colorScheme.secondaryContainer,
                    leading: Icon(module.icon),
                    title: Text(module.title,
                        maxLines: 1, overflow: TextOverflow.ellipsis),
                    onTap: () => setState(() => _selectedIndex = index),
                  ),
                );
              },
            ),
          ),
          const VerticalDivider(width: 1),
          Expanded(
            child: FutureBuilder<_DashboardData>(
              future: _dashboardFuture,
              builder: (context, snapshot) {
                if (snapshot.connectionState == ConnectionState.waiting) {
                  return const Center(child: CircularProgressIndicator());
                }
                final data = snapshot.data ?? const _DashboardData({});
                return ListView(
                  padding: const EdgeInsets.all(24),
                  children: [
                    _Header(
                      username: user?.username ?? 'user',
                      tenantName: user?.tenantName ?? 'Platform workspace',
                      branchName: user?.branchName,
                    ),
                    const SizedBox(height: 24),
                    if (_selectedIndex == 0)
                      _Overview(
                        data: data,
                        onCreateTask: _createOnboardingTask,
                        onSeedTasks: _seedOnboardingTasks,
                        onCreateBranding: _createBranding,
                        onCreateWebsite: _createWebsiteShell,
                      )
                    else
                      _ModuleView(
                        module: selectedModule,
                        rows: data.rowsFor(selectedModule.title),
                        onCreateTask: selectedModule.title == 'Onboarding'
                            ? _createOnboardingTask
                            : null,
                        onCreateBranding: selectedModule.title == 'Branding'
                            ? _createBranding
                            : null,
                        onCreateWebsite: selectedModule.title == 'Website'
                            ? _createWebsiteShell
                            : null,
                        onCompleteTask: selectedModule.title == 'Onboarding'
                            ? _completeTask
                            : null,
                      ),
                  ],
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

class _Header extends StatelessWidget {
  const _Header({
    required this.username,
    required this.tenantName,
    required this.branchName,
  });

  final String username;
  final String tenantName;
  final String? branchName;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Welcome, $username',
            style: Theme.of(context).textTheme.headlineSmall),
        const SizedBox(height: 6),
        Text(
          branchName == null ? tenantName : '$tenantName - $branchName',
          style: Theme.of(context).textTheme.bodyLarge,
        ),
      ],
    );
  }
}

class _Overview extends StatelessWidget {
  const _Overview({
    required this.data,
    required this.onCreateTask,
    required this.onSeedTasks,
    required this.onCreateBranding,
    required this.onCreateWebsite,
  });

  final _DashboardData data;
  final VoidCallback onCreateTask;
  final VoidCallback onSeedTasks;
  final VoidCallback onCreateBranding;
  final VoidCallback onCreateWebsite;

  @override
  Widget build(BuildContext context) {
    final countTiles = [
      ('Branches', Icons.account_tree_outlined),
      ('Cases', Icons.assignment_outlined),
      ('Policies', Icons.verified_user_outlined),
      ('Financials', Icons.payments_outlined),
      ('Inventory', Icons.inventory_2_outlined),
      ('Scheduling', Icons.event_outlined),
      ('Mortuary', Icons.local_hospital_outlined),
      ('Onboarding', Icons.school_outlined),
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Wrap(
          spacing: 12,
          runSpacing: 12,
          children: [
            for (final tile in countTiles)
              SizedBox(
                width: 190,
                child: Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Icon(tile.$2),
                        const SizedBox(height: 14),
                        Text('${data.rowsFor(tile.$1).length}',
                            style: Theme.of(context).textTheme.headlineMedium),
                        Text(tile.$1),
                      ],
                    ),
                  ),
                ),
              ),
          ],
        ),
        const SizedBox(height: 24),
        Text('Quick actions', style: Theme.of(context).textTheme.titleLarge),
        const SizedBox(height: 12),
        Wrap(
          spacing: 12,
          runSpacing: 12,
          children: [
            FilledButton.icon(
              onPressed: onCreateTask,
              icon: const Icon(Icons.add_task),
              label: const Text('Add onboarding task'),
            ),
            OutlinedButton.icon(
              onPressed: onSeedTasks,
              icon: const Icon(Icons.playlist_add_check),
              label: const Text('Seed checklist'),
            ),
            OutlinedButton.icon(
              onPressed: onCreateBranding,
              icon: const Icon(Icons.palette_outlined),
              label: const Text('Create branding'),
            ),
            OutlinedButton.icon(
              onPressed: onCreateWebsite,
              icon: const Icon(Icons.language_outlined),
              label: const Text('Create website shell'),
            ),
          ],
        ),
      ],
    );
  }
}

class _ModuleView extends StatelessWidget {
  const _ModuleView({
    required this.module,
    required this.rows,
    this.onCreateTask,
    this.onCreateBranding,
    this.onCreateWebsite,
    this.onCompleteTask,
  });

  final _ModuleConfig module;
  final List<Map<String, dynamic>> rows;
  final VoidCallback? onCreateTask;
  final VoidCallback? onCreateBranding;
  final VoidCallback? onCreateWebsite;
  final Future<void> Function(int id)? onCompleteTask;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(module.icon),
            const SizedBox(width: 10),
            Expanded(
                child: Text(module.title,
                    style: Theme.of(context).textTheme.headlineSmall)),
            if (onCreateTask != null)
              FilledButton.icon(
                onPressed: onCreateTask,
                icon: const Icon(Icons.add),
                label: const Text('New task'),
              ),
            if (onCreateBranding != null)
              FilledButton.icon(
                onPressed: onCreateBranding,
                icon: const Icon(Icons.add),
                label: const Text('Create settings'),
              ),
            if (onCreateWebsite != null)
              FilledButton.icon(
                onPressed: onCreateWebsite,
                icon: const Icon(Icons.add),
                label: const Text('Create site'),
              ),
          ],
        ),
        const SizedBox(height: 16),
        if (rows.isEmpty)
          const _EmptyState()
        else
          for (final row in rows)
            Card(
              child: ListTile(
                leading: CircleAvatar(child: Text(_rowInitial(row))),
                title: Text(_rowTitle(row),
                    maxLines: 1, overflow: TextOverflow.ellipsis),
                subtitle: Text(_rowSubtitle(row),
                    maxLines: 2, overflow: TextOverflow.ellipsis),
                trailing: _rowTrailing(row, onCompleteTask),
              ),
            ),
      ],
    );
  }

  Widget? _rowTrailing(
      Map<String, dynamic> row, Future<void> Function(int id)? onCompleteTask) {
    if (onCompleteTask == null) {
      return null;
    }
    final completed =
        row['is_completed'] == true || row['completed_at'] != null;
    if (completed) {
      return const Icon(Icons.check_circle, color: Colors.green);
    }
    final id = row['id'];
    if (id is! int) {
      return null;
    }
    return IconButton(
      tooltip: 'Complete task',
      onPressed: () => onCompleteTask(id),
      icon: const Icon(Icons.check_circle_outline),
    );
  }
}

class _EmptyState extends StatelessWidget {
  const _EmptyState();

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        border: Border.all(color: Theme.of(context).colorScheme.outlineVariant),
        borderRadius: BorderRadius.circular(8),
      ),
      child: const Text(
          'No records yet. Use the available actions or backend APIs to add data.'),
    );
  }
}

String _rowInitial(Map<String, dynamic> row) {
  final title = _rowTitle(row);
  return title.isEmpty ? '?' : title.substring(0, 1).toUpperCase();
}

String _rowTitle(Map<String, dynamic> row) {
  for (final key in [
    'title',
    'name',
    'reference',
    'intake_reference',
    'app_name',
    'username',
    'slug'
  ]) {
    final value = row[key];
    if (value is String && value.trim().isNotEmpty) {
      return value;
    }
  }
  final first = row['first_name'];
  final last = row['last_name'];
  if (first is String || last is String) {
    return '${first ?? ''} ${last ?? ''}'.trim();
  }
  return 'Record #${row['id'] ?? '-'}';
}

String _rowSubtitle(Map<String, dynamic> row) {
  final parts = <String>[];
  for (final key in [
    'status',
    'category',
    'role',
    'branch_name',
    'storage_location',
    'storage_unit',
    'package_name',
    'page_type',
    'email_from_name',
    'created_at',
    'updated_at',
  ]) {
    final value = row[key];
    if (value != null && value.toString().trim().isNotEmpty) {
      parts.add('${_labelFor(key)}: $value');
    }
  }
  if (parts.isEmpty) {
    return 'ID: ${row['id'] ?? '-'}';
  }
  return parts.take(3).join(' - ');
}

String _labelFor(String key) {
  return key.replaceAll('_', ' ');
}

class _DashboardData {
  const _DashboardData(this.rows);

  final Map<String, List<Map<String, dynamic>>> rows;

  List<Map<String, dynamic>> rowsFor(String title) {
    return rows[title] ?? const [];
  }
}

class _ModuleConfig {
  const _ModuleConfig(this.title, this.icon, this.path);

  final String title;
  final IconData icon;
  final String path;
}
