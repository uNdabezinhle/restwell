import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter/services.dart';

import '../../admin/admin_repository.dart';
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
    _ModuleConfig('Branches', Icons.account_tree_outlined,
        '/api/tenants/branches/', null, true),
    _ModuleConfig(
        'Users', Icons.people_outline, '/api/accounts/users/', null, true),
    _ModuleConfig('Cases', Icons.assignment_outlined, '/api/cases/'),
    _ModuleConfig('Deceased', Icons.person_outline, '/api/cases/deceased/'),
    _ModuleConfig(
        'Family Members', Icons.groups_outlined, '/api/cases/family-members/'),
    _ModuleConfig(
        'Policies', Icons.verified_user_outlined, '/api/policies/templates/'),
    _ModuleConfig(
        'Financials', Icons.payments_outlined, '/api/financials/invoices/'),
    _ModuleConfig(
        'Inventory', Icons.inventory_2_outlined, '/api/inventory/items/'),
    _ModuleConfig(
        'Scheduling', Icons.event_outlined, '/api/scheduling/events/'),
    _ModuleConfig('Mortuary', Icons.local_hospital_outlined,
        '/api/mortuary/records/', 'mortuary'),
    _ModuleConfig('Routes', Icons.map_outlined,
        '/api/geolocation/routes/active/', 'geolocation'),
    _ModuleConfig('Branding', Icons.palette_outlined, '/api/branding/settings/',
        null, true),
    _ModuleConfig('Website', Icons.language_outlined, '/api/websites/pages/',
        'website_builder', true),
    _ModuleConfig('Apps', Icons.android_outlined, '/api/branded-apps/configs/',
        'branded_apps', true),
    _ModuleConfig('Notifications', Icons.notifications_outlined,
        '/api/notifications/messages/', 'notifications', true),
    _ModuleConfig('Support', Icons.support_agent_outlined,
        '/api/client/support-requests/', null, true),
    _ModuleConfig('Onboarding', Icons.school_outlined, '/api/onboarding/tasks/',
        null, true),
    _ModuleConfig('Help', Icons.help_outline,
        '/api/onboarding/published-articles/', null, true),
    _ModuleConfig('Audit Logs', Icons.history, '/api/audit-logs/', null, true),
  ];

  @override
  void initState() {
    super.initState();
    _dashboardFuture = _loadDashboard();
  }

  Future<_DashboardData> _loadDashboard() async {
    final repository = ref.read(adminRepositoryProvider);
    final summary = await repository.fetchDashboardSummary();
    final features = await repository.fetchFeatures();
    final results = <String, List<Map<String, dynamic>>>{};
    final user = ref.read(authControllerProvider).state.user;
    for (final module in _modules.where((module) =>
        module.path.isNotEmpty &&
        _moduleEnabledForUser(module, features, user?.role))) {
      try {
        results[module.title] = await repository.fetchModuleRows(module.path);
      } on DioException {
        results[module.title] = const [];
      }
    }
    if (_moduleEnabledForUser(
        const _ModuleConfig(
            '', Icons.language_outlined, '', 'website_builder', true),
        features,
        user?.role)) {
      try {
        results['Website Sites'] =
            await repository.fetchModuleRows('/api/websites/sites/');
      } on DioException {
        results['Website Sites'] = const [];
      }
    }
    return _DashboardData(
      rows: results,
      summary: summary,
      features: features,
    );
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
      () => ref
          .read(adminRepositoryProvider)
          .createRecord('/api/onboarding/tasks/', {
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
    final repository = ref.read(adminRepositoryProvider);
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
        await repository.createRecord('/api/onboarding/tasks/', {
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
      () => ref
          .read(adminRepositoryProvider)
          .createRecord('/api/branding/settings/', {
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
      () => ref
          .read(adminRepositoryProvider)
          .createRecord('/api/websites/sites/', {
        'name': 'RestWell Demo',
        'subdomain': 'restwell-demo',
        'is_published': true,
      }),
      'Website shell created.',
    );
  }

  Future<void> _toggleFeature(TenantFeature feature, bool isEnabled) async {
    if (feature.id == 0) {
      _showMessage('This feature cannot be changed from the workspace.');
      return;
    }
    await _runAction(
      () async {
        final updated = await ref
            .read(adminRepositoryProvider)
            .updateFeature(feature.id, isEnabled);
        return {
          'id': updated.id,
          'code': updated.code,
          'is_enabled': updated.isEnabled,
        };
      },
      isEnabled ? 'Feature enabled.' : 'Feature disabled.',
    );
  }

  Future<void> _createCaseIntake(_DashboardData data, String suffix) async {
    final branch = _firstId(data.rowsFor('Branches'));
    if (branch == null) {
      _showMessage('Create a branch first.');
      return;
    }

    final referenceController = TextEditingController(text: 'CASE-$suffix');
    final deceasedFirstController = TextEditingController();
    final deceasedLastController = TextEditingController();
    final placeOfDeathController = TextEditingController();
    final serviceDateController = TextEditingController(text: _dateOffset(7));
    final familyFirstController = TextEditingController();
    final familyLastController = TextEditingController();
    final relationshipController = TextEditingController(text: 'Next of kin');
    final phoneController = TextEditingController();
    final emailController = TextEditingController();
    final notesController = TextEditingController();

    final result = await showDialog<Map<String, dynamic>>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('Case intake'),
          content: SizedBox(
            width: 520,
            child: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  TextField(
                    controller: referenceController,
                    decoration: const InputDecoration(labelText: 'Reference'),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: deceasedFirstController,
                    decoration:
                        const InputDecoration(labelText: 'Deceased first name'),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: deceasedLastController,
                    decoration:
                        const InputDecoration(labelText: 'Deceased last name'),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: placeOfDeathController,
                    decoration:
                        const InputDecoration(labelText: 'Place of death'),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: serviceDateController,
                    decoration: const InputDecoration(
                        labelText: 'Service date', hintText: 'YYYY-MM-DD'),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: familyFirstController,
                    decoration:
                        const InputDecoration(labelText: 'Family first name'),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: familyLastController,
                    decoration:
                        const InputDecoration(labelText: 'Family last name'),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: relationshipController,
                    decoration:
                        const InputDecoration(labelText: 'Relationship'),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: phoneController,
                    decoration: const InputDecoration(labelText: 'Phone'),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: emailController,
                    decoration: const InputDecoration(labelText: 'Email'),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: notesController,
                    maxLines: 3,
                    decoration: const InputDecoration(labelText: 'Notes'),
                  ),
                ],
              ),
            ),
          ),
          actions: [
            TextButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('Cancel')),
            FilledButton(
              onPressed: () {
                if (referenceController.text.trim().isEmpty ||
                    deceasedFirstController.text.trim().isEmpty ||
                    deceasedLastController.text.trim().isEmpty) {
                  return;
                }
                Navigator.pop(context, {
                  'branch': branch,
                  'reference': referenceController.text.trim(),
                  'service_date': serviceDateController.text.trim(),
                  'notes': notesController.text.trim(),
                  'deceased': {
                    'first_name': deceasedFirstController.text.trim(),
                    'last_name': deceasedLastController.text.trim(),
                    'place_of_death': placeOfDeathController.text.trim(),
                  },
                  'family_member': {
                    'first_name': familyFirstController.text.trim(),
                    'last_name': familyLastController.text.trim(),
                    'relationship': relationshipController.text.trim(),
                    'phone': phoneController.text.trim(),
                    'email': emailController.text.trim(),
                    'is_next_of_kin': true,
                  },
                });
              },
              child: const Text('Create case'),
            ),
          ],
        );
      },
    );

    referenceController.dispose();
    deceasedFirstController.dispose();
    deceasedLastController.dispose();
    placeOfDeathController.dispose();
    serviceDateController.dispose();
    familyFirstController.dispose();
    familyLastController.dispose();
    relationshipController.dispose();
    phoneController.dispose();
    emailController.dispose();
    notesController.dispose();

    if (result == null) {
      return;
    }
    await _runAction(
      () => ref
          .read(adminRepositoryProvider)
          .runWorkflow('/api/cases/intake/', result),
      'Case intake completed.',
    );
  }

  Future<void> _createModuleRecord(
      String moduleTitle, _DashboardData data) async {
    final repository = ref.read(adminRepositoryProvider);
    final user = ref.read(authControllerProvider).state.user;
    final tenant = user?.tenant;
    final branch = _firstId(data.rowsFor('Branches'));
    final caseId = _firstId(data.rowsFor('Cases'));
    final deceased = _firstId(data.rowsFor('Deceased'));
    final familyMember = _firstId(data.rowsFor('Family Members'));
    final suffix =
        DateTime.now().millisecondsSinceEpoch.toString().substring(8);

    Future<Map<String, dynamic>> create(
        String path, Map<String, dynamic> payload) {
      return repository.createRecord(path, payload);
    }

    switch (moduleTitle) {
      case 'Branches':
        if (tenant == null) {
          _showMessage('Tenant context is required.');
          return;
        }
        await _runAction(
          () => create('/api/tenants/branches/', {
            'tenant': tenant,
            'name': 'Demo Branch $suffix',
            'code': 'BR$suffix',
            'province': 'Gauteng',
            'city': 'Johannesburg',
            'is_active': true,
          }),
          'Branch created.',
        );
        return;
      case 'Users':
        if (branch == null) {
          _showMessage('Create a branch first.');
          return;
        }
        await _runAction(
          () => create('/api/accounts/users/', {
            'username': 'staff$suffix@restwell.local',
            'email': 'staff$suffix@restwell.local',
            'first_name': 'Demo',
            'last_name': 'Staff $suffix',
            'role': 'staff',
            'branch': branch,
            'password': 'RestWell123!',
            'is_active': true,
          }),
          'Staff user created.',
        );
        return;
      case 'Family Members':
        if (caseId == null) {
          _showMessage('Create a case first.');
          return;
        }
        await _runAction(
          () => create('/api/cases/family-members/', {
            'case': caseId,
            'first_name': 'Family',
            'last_name': 'Contact $suffix',
            'relationship': 'Next of kin',
            'phone': '+2711000$suffix',
            'email': 'family$suffix@example.com',
            'is_next_of_kin': true,
          }),
          'Family member created.',
        );
        return;
      case 'Deceased':
        if (branch == null) {
          _showMessage('Create a branch first.');
          return;
        }
        await _runAction(
          () => create('/api/cases/deceased/', {
            'branch': branch,
            'first_name': 'Demo',
            'last_name': 'Person $suffix',
            'place_of_death': 'Johannesburg',
          }),
          'Deceased record created.',
        );
        return;
      case 'Cases':
        await _createCaseIntake(data, suffix);
        return;
      case 'Policies':
        final underwriter = await create('/api/policies/underwriters/', {
          'name': 'Demo Underwriter $suffix',
          'registration_number': 'UW-$suffix',
          'is_active': true,
        });
        final template = await create('/api/policies/templates/', {
          'underwriter': underwriter['id'],
          'name': 'Demo Cover $suffix',
          'cover_amount': '25000.00',
          'premium_amount': '150.00',
          'billing_frequency': 'monthly',
          'is_active': true,
        });
        if (familyMember == null) {
          _showMessage(
              'Policy template created. Add a family member to enroll a policy.');
          _refresh();
          return;
        }
        await _runAction(
          () => create('/api/policies/enrollments/', {
            'policy_template': template['id'],
            'family_member': familyMember,
            'policy_number': 'POL-$suffix',
            'status': 'active',
            'start_date': _dateOffset(0),
          }),
          'Policy template and enrollment created.',
        );
        return;
      case 'Financials':
        if (branch == null) {
          _showMessage('Create a branch first.');
          return;
        }
        final invoice = await create('/api/financials/invoices/', {
          'branch': branch,
          'case': caseId,
          'invoice_number': 'INV-$suffix',
          'customer_name': 'Demo Customer',
          'customer_email': 'family@example.com',
          'issue_date': _dateOffset(0),
          'due_date': _dateOffset(7),
          'status': 'issued',
        });
        await _runAction(
          () => create('/api/financials/line-items/', {
            'invoice': invoice['id'],
            'description': 'Demo funeral service',
            'quantity': '1.00',
            'unit_price': '8500.00',
          }),
          'Invoice created.',
        );
        return;
      case 'Inventory':
        if (branch == null) {
          _showMessage('Create a branch first.');
          return;
        }
        await _runAction(
          () => create('/api/inventory/items/', {
            'branch': branch,
            'name': 'Demo Item $suffix',
            'sku': 'SKU-$suffix',
            'category': 'General',
            'reorder_level': '2.00',
            'unit_cost': '100.00',
            'is_active': true,
          }),
          'Inventory item created.',
        );
        return;
      case 'Scheduling':
        if (branch == null) {
          _showMessage('Create a branch first.');
          return;
        }
        final resource = await create('/api/scheduling/resources/', {
          'branch': branch,
          'name': 'Demo Vehicle $suffix',
          'resource_type': 'vehicle',
          'is_active': true,
        });
        await _runAction(
          () => create('/api/scheduling/events/', {
            'branch': branch,
            'case': caseId,
            'title': 'Demo Service $suffix',
            'event_type': 'funeral_service',
            'starts_at': _dateTimeOffset(2),
            'ends_at': _dateTimeOffset(2, hours: 2),
            'location': 'Johannesburg Chapel',
            'resources': [resource['id']],
          }),
          'Calendar event created.',
        );
        return;
      case 'Mortuary':
        if (branch == null || deceased == null) {
          _showMessage('Create a branch and deceased record first.');
          return;
        }
        await _runAction(
          () => create('/api/mortuary/records/', {
            'branch': branch,
            'case': caseId,
            'deceased': deceased,
            'intake_reference': 'MOR-$suffix',
            'storage_location': 'Cold Room A',
            'storage_unit': 'A-$suffix',
            'intake_at': _dateTimeOffset(0),
          }),
          'Mortuary intake created.',
        );
        return;
      case 'Routes':
        if (branch == null) {
          _showMessage('Create a branch first.');
          return;
        }
        await _runAction(
          () => create('/api/geolocation/routes/', {
            'branch': branch,
            'case': caseId,
            'name': 'Demo Route $suffix',
            'status': 'active',
            'origin': 'Hospital',
            'destination': 'RestWell',
          }),
          'Route created.',
        );
        return;
      case 'Website':
        await _createWebsitePage(data, suffix);
        return;
      case 'Apps':
        await _runAction(
          () => create('/api/branded-apps/configs/', {
            'app_name': 'RestWell Demo',
            'package_name': 'za.co.restwell.demo$suffix',
            'primary_color': '#0F766E',
            'secondary_color': '#2563EB',
            'support_email': 'support@restwell.local',
            'privacy_policy_url': 'https://example.com/privacy',
            'version_name': '1.0.0',
            'version_code': 1,
            'is_active': true,
          }),
          'Android app config created.',
        );
        return;
      case 'Notifications':
        if (user == null) {
          _showMessage('User context is required.');
          return;
        }
        await _runAction(
          () => create('/api/notifications/messages/', {
            'recipient_user': user.id,
            'channel': 'in_app',
            'subject': 'Demo notification $suffix',
            'body': 'This is a local demo notification.',
          }),
          'Notification created.',
        );
        return;
      case 'Onboarding':
        await _createOnboardingTask();
        return;
      case 'Help':
        await _runAction(
          () => create('/api/onboarding/articles/', {
            'slug': 'demo-help-$suffix',
            'title': 'Demo Help $suffix',
            'summary': 'Quick local help article.',
            'body':
                'Use this article to guide staff through the demo workflow.',
            'category': 'getting-started',
            'audience': 'all',
            'is_published': true,
          }),
          'Help article created.',
        );
        return;
    }
  }

  Future<void> _createWebsitePage(_DashboardData data, String suffix) async {
    final repository = ref.read(adminRepositoryProvider);
    Future<Map<String, dynamic>> create(
        String path, Map<String, dynamic> payload) {
      return repository.createRecord(path, payload);
    }

    int? siteId;
    final sites = data.rowsFor('Website Sites');
    final pages = data.rowsFor('Website');
    if (sites.isNotEmpty && sites.first['id'] is int) {
      siteId = sites.first['id'] as int;
    } else if (pages.isNotEmpty && pages.first['site'] is int) {
      siteId = pages.first['site'] as int;
    } else {
      try {
        final site = await create('/api/websites/sites/', {
          'name': 'RestWell Demo',
          'subdomain': 'restwell-demo-$suffix',
          'is_published': true,
        });
        siteId = site['id'] as int;
      } on DioException catch (error) {
        _showMessage(error.response?.data?.toString() ??
            'Website site already exists. Refresh and try again.');
        return;
      }
    }

    final page = await create('/api/websites/pages/', {
      'site': siteId,
      'slug': 'demo-page-$suffix',
      'title': 'Demo Page $suffix',
      'page_type': 'custom',
      'content': {'headline': 'Demo Page $suffix'},
      'sort_order': 10,
      'is_published': false,
    });
    await _runAction(
      () => create('/api/websites/blocks/', {
        'page': page['id'],
        'block_type': 'hero',
        'content': {
          'headline': 'Dignified care',
          'body': 'Created from the admin workspace.',
        },
        'sort_order': 1,
        'is_visible': true,
      }),
      'Website page and block created.',
    );
  }

  Future<void> _completeTask(int id) async {
    await _runAction(
      () => ref
          .read(adminRepositoryProvider)
          .runWorkflow('/api/onboarding/tasks/$id/complete/'),
      'Task completed.',
    );
  }

  Future<void> _runModuleWorkflow(
      String moduleTitle, Map<String, dynamic> row) async {
    final id = row['id'];
    if (id is! int) {
      return;
    }
    switch (moduleTitle) {
      case 'Cases':
        await _runAction(
          () => ref.read(adminRepositoryProvider).runWorkflow(
            '/api/cases/$id/advance-status/',
            {'status': 'completed'},
          ),
          'Case marked completed.',
        );
        return;
      case 'Financials':
        final amount = row['balance_due']?.toString() ??
            row['total_amount']?.toString() ??
            '0.00';
        await _runAction(
          () => ref.read(adminRepositoryProvider).runWorkflow(
            '/api/financials/invoices/$id/record-payment/',
            {'amount': amount, 'method': 'cash'},
          ),
          'Payment recorded.',
        );
        return;
      case 'Inventory':
        await _runAction(
          () => ref.read(adminRepositoryProvider).runWorkflow(
            '/api/inventory/items/$id/adjust-stock/',
            {
              'quantity': '1.00',
              'transaction_type': 'stock_in',
              'note': 'Admin quick adjustment'
            },
          ),
          'Stock adjusted.',
        );
        return;
      case 'Mortuary':
        await _runAction(
          () => ref
              .read(adminRepositoryProvider)
              .runWorkflow('/api/mortuary/records/$id/release/'),
          'Mortuary record released.',
        );
        return;
      case 'Routes':
        await _runAction(
          () => ref.read(adminRepositoryProvider).runWorkflow(
            '/api/geolocation/routes/$id/log-location/',
            {
              'latitude': '-26.204100',
              'longitude': '28.047300',
              'accuracy_meters': '12.50',
              'recorded_at': _dateTimeOffset(0),
              'note': 'Admin workspace location check-in',
            },
          ),
          'Location logged.',
        );
        return;
      case 'Apps':
        await _runAction(
          () => ref.read(adminRepositoryProvider).runWorkflow(
            '/api/branded-apps/configs/$id/request-build/',
            {'git_ref': 'feature/milestone-4-functional-application'},
          ),
          'Android build requested.',
        );
        return;
      case 'Website':
        await _runAction(
          () => ref
              .read(adminRepositoryProvider)
              .runWorkflow('/api/websites/pages/$id/publish/'),
          'Website page published.',
        );
        return;
      case 'Notifications':
        await _runAction(
          () => ref
              .read(adminRepositoryProvider)
              .runWorkflow('/api/notifications/messages/$id/send/'),
          'Notification sent.',
        );
        return;
      case 'Support':
        await _runAction(
          () => ref
              .read(adminRepositoryProvider)
              .runWorkflow('/api/client/support-requests/$id/resolve/'),
          'Support request resolved.',
        );
        return;
    }
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

  void _showMessage(String message) {
    ScaffoldMessenger.of(context)
        .showSnackBar(SnackBar(content: Text(message)));
  }

  @override
  Widget build(BuildContext context) {
    final user = ref.watch(authControllerProvider).state.user;

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
      body: FutureBuilder<_DashboardData>(
        future: _dashboardFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          final data = snapshot.data ?? _DashboardData.empty();
          final modules = _visibleModules(data, user?.role);
          final selectedIndex =
              _selectedIndex >= modules.length ? 0 : _selectedIndex;
          final selectedModule = modules[selectedIndex];

          return Row(
            children: [
              SizedBox(
                width: 224,
                child: ListView.builder(
                  padding: const EdgeInsets.all(12),
                  itemCount: modules.length,
                  itemBuilder: (context, index) {
                    final module = modules[index];
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 4),
                      child: ListTile(
                        selected: selectedIndex == index,
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
                child: ListView(
                  padding: const EdgeInsets.all(24),
                  children: [
                    _Header(
                      username: user?.username ?? 'user',
                      tenantName: user?.tenantName ?? 'Platform workspace',
                      branchName: user?.branchName,
                    ),
                    const SizedBox(height: 24),
                    if (selectedModule.title == 'Overview')
                      _Overview(
                        data: data,
                        onCreateTask: _createOnboardingTask,
                        onSeedTasks: _seedOnboardingTasks,
                        onCreateBranding: _createBranding,
                        onCreateWebsite: _createWebsiteShell,
                        onToggleFeature: _toggleFeature,
                        isTenantAdmin: _isTenantAdminRole(user?.role),
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
                        onRunWorkflow: _runModuleWorkflow,
                        onCreateRecord: () =>
                            _createModuleRecord(selectedModule.title, data),
                      ),
                  ],
                ),
              ),
            ],
          );
        },
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
    required this.onToggleFeature,
    required this.isTenantAdmin,
  });

  final _DashboardData data;
  final VoidCallback onCreateTask;
  final VoidCallback onSeedTasks;
  final VoidCallback onCreateBranding;
  final VoidCallback onCreateWebsite;
  final Future<void> Function(TenantFeature feature, bool isEnabled)
      onToggleFeature;
  final bool isTenantAdmin;

  @override
  Widget build(BuildContext context) {
    final countTiles = [
      (
        'Branches',
        Icons.account_tree_outlined,
        data.rowsFor('Branches').length
      ),
      (
        'Cases',
        Icons.assignment_outlined,
        data.summary.operations['cases'] ?? 0
      ),
      (
        'Policies',
        Icons.verified_user_outlined,
        data.summary.commercial['policy_templates'] ?? 0
      ),
      (
        'Financials',
        Icons.payments_outlined,
        data.summary.commercial['invoices'] ?? 0
      ),
      (
        'Inventory',
        Icons.inventory_2_outlined,
        data.summary.commercial['inventory_items'] ?? 0
      ),
      (
        'Scheduling',
        Icons.event_outlined,
        data.summary.operations['scheduled_events'] ?? 0
      ),
      (
        'Mortuary',
        Icons.local_hospital_outlined,
        data.summary.operations['mortuary_records'] ?? 0
      ),
      (
        'Onboarding',
        Icons.school_outlined,
        data.summary.digital['onboarding_open'] ?? 0
      ),
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
                        Text('${tile.$3}',
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
        Text('Enabled modules', style: Theme.of(context).textTheme.titleLarge),
        const SizedBox(height: 12),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            for (final feature in data.features)
              SizedBox(
                width: 260,
                child: isTenantAdmin
                    ? SwitchListTile(
                        value: feature.isEnabled,
                        dense: true,
                        contentPadding:
                            const EdgeInsets.symmetric(horizontal: 12),
                        secondary: Icon(
                          feature.isEnabled ? Icons.check_circle : Icons.block,
                          color: feature.isEnabled ? Colors.green : Colors.red,
                        ),
                        title: Text(feature.code.replaceAll('_', ' ')),
                        onChanged: (value) => onToggleFeature(feature, value),
                      )
                    : ListTile(
                        dense: true,
                        contentPadding:
                            const EdgeInsets.symmetric(horizontal: 12),
                        leading: Icon(
                          feature.isEnabled ? Icons.check_circle : Icons.block,
                          color: feature.isEnabled ? Colors.green : Colors.red,
                        ),
                        title: Text(feature.code.replaceAll('_', ' ')),
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
            if (isTenantAdmin)
              FilledButton.icon(
                onPressed: onCreateTask,
                icon: const Icon(Icons.add_task),
                label: const Text('Add onboarding task'),
              ),
            if (isTenantAdmin)
              OutlinedButton.icon(
                onPressed: onSeedTasks,
                icon: const Icon(Icons.playlist_add_check),
                label: const Text('Seed checklist'),
              ),
            if (isTenantAdmin)
              OutlinedButton.icon(
                onPressed: onCreateBranding,
                icon: const Icon(Icons.palette_outlined),
                label: const Text('Create branding'),
              ),
            if (isTenantAdmin && data.featureEnabled('website_builder'))
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
    required this.onRunWorkflow,
    required this.onCreateRecord,
  });

  final _ModuleConfig module;
  final List<Map<String, dynamic>> rows;
  final VoidCallback? onCreateTask;
  final VoidCallback? onCreateBranding;
  final VoidCallback? onCreateWebsite;
  final Future<void> Function(int id)? onCompleteTask;
  final Future<void> Function(String moduleTitle, Map<String, dynamic> row)
      onRunWorkflow;
  final Future<void> Function() onCreateRecord;

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
            if (_canCreate(module.title))
              FilledButton.icon(
                onPressed: () => onCreateRecord(),
                icon: const Icon(Icons.add),
                label: const Text('New record'),
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
                trailing: _rowTrailing(context, row),
              ),
            ),
      ],
    );
  }

  Widget? _rowTrailing(BuildContext context, Map<String, dynamic> row) {
    final workflowLabel = _workflowLabel(module.title, row);
    final publicUrl = module.title == 'Website'
        ? (row['public_html_url'] as String? ?? '')
        : '';
    if (onCompleteTask == null && workflowLabel == null && publicUrl.isEmpty) {
      return null;
    }
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        if (onCompleteTask != null) _completeTaskButton(row),
        if (workflowLabel != null)
          TextButton(
            onPressed: () => onRunWorkflow(module.title, row),
            child: Text(workflowLabel),
          ),
        if (publicUrl.isNotEmpty)
          TextButton(
            onPressed: () async {
              await Clipboard.setData(ClipboardData(text: publicUrl));
              if (context.mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Public page link copied.')),
                );
              }
            },
            child: const Text('Copy link'),
          ),
      ],
    );
  }

  Widget _completeTaskButton(Map<String, dynamic> row) {
    final completed =
        row['is_completed'] == true || row['completed_at'] != null;
    if (completed) {
      return const Icon(Icons.check_circle, color: Colors.green);
    }
    final id = row['id'];
    if (id is! int) {
      return const SizedBox.shrink();
    }
    return IconButton(
      tooltip: 'Complete task',
      onPressed: () => onCompleteTask!(id),
      icon: const Icon(Icons.check_circle_outline),
    );
  }
}

bool _canCreate(String moduleTitle) {
  return {
    'Branches',
    'Users',
    'Cases',
    'Deceased',
    'Family Members',
    'Policies',
    'Financials',
    'Inventory',
    'Scheduling',
    'Mortuary',
    'Routes',
    'Website',
    'Apps',
    'Notifications',
    'Onboarding',
    'Help',
  }.contains(moduleTitle);
}

List<_ModuleConfig> _visibleModules(_DashboardData data, String? role) {
  return _DashboardScreenState._modules
      .where((module) => _moduleEnabledForUser(module, data.features, role))
      .toList(growable: false);
}

bool _moduleEnabledForUser(
    _ModuleConfig module, List<TenantFeature> features, String? role) {
  if (module.adminOnly && !_isTenantAdminRole(role)) {
    return false;
  }
  return _moduleEnabledByFeatures(module, features);
}

bool _isTenantAdminRole(String? role) {
  return role == 'tenant_admin' || role == 'super_admin';
}

bool _moduleEnabledByFeatures(
    _ModuleConfig module, List<TenantFeature> features) {
  final featureCode = module.featureCode;
  if (featureCode == null) {
    return true;
  }
  final matchingFeatures =
      features.where((feature) => feature.code == featureCode);
  if (matchingFeatures.isEmpty) {
    return true;
  }
  return matchingFeatures.any((feature) => feature.isEnabled);
}

int? _firstId(List<Map<String, dynamic>> rows) {
  if (rows.isEmpty || rows.first['id'] is! int) {
    return null;
  }
  return rows.first['id'] as int;
}

String _dateOffset(int days) {
  return DateTime.now()
      .add(Duration(days: days))
      .toIso8601String()
      .substring(0, 10);
}

String _dateTimeOffset(int days, {int hours = 0}) {
  return DateTime.now()
      .add(Duration(days: days, hours: hours))
      .toUtc()
      .toIso8601String();
}

String? _workflowLabel(String moduleTitle, Map<String, dynamic> row) {
  switch (moduleTitle) {
    case 'Cases':
      return row['status'] == 'completed' ? null : 'Complete';
    case 'Financials':
      return row['status'] == 'paid' ? null : 'Record payment';
    case 'Inventory':
      return 'Stock +1';
    case 'Mortuary':
      return row['status'] == 'released' ? null : 'Release';
    case 'Routes':
      return 'Log location';
    case 'Apps':
      return 'Request build';
    case 'Website':
      return row['is_published'] == true ? null : 'Publish';
    case 'Notifications':
      return row['status'] == 'sent' ? null : 'Send';
    case 'Support':
      return row['status'] == 'resolved' ? null : 'Resolve';
  }
  return null;
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
    'subject',
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
    'message',
    'branch_name',
    'storage_location',
    'storage_unit',
    'package_name',
    'page_type',
    'public_html_url',
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
  const _DashboardData({
    required this.rows,
    required this.summary,
    required this.features,
  });

  factory _DashboardData.empty() {
    return const _DashboardData(
      rows: {},
      summary: DashboardSummary(operations: {}, commercial: {}, digital: {}),
      features: [],
    );
  }

  final Map<String, List<Map<String, dynamic>>> rows;
  final DashboardSummary summary;
  final List<TenantFeature> features;

  List<Map<String, dynamic>> rowsFor(String title) {
    return rows[title] ?? const [];
  }

  bool featureEnabled(String featureCode) {
    final matchingFeatures =
        features.where((feature) => feature.code == featureCode);
    if (matchingFeatures.isEmpty) {
      return true;
    }
    return matchingFeatures.any((feature) => feature.isEnabled);
  }
}

class _ModuleConfig {
  const _ModuleConfig(this.title, this.icon, this.path,
      [this.featureCode, this.adminOnly = false]);

  final String title;
  final IconData icon;
  final String path;
  final String? featureCode;
  final bool adminOnly;
}
