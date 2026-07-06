import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

void main() {
  runApp(const ProviderScope(child: RestWellClientApp()));
}

final dioProvider = Provider<Dio>((ref) {
  return Dio(
    BaseOptions(
      baseUrl: const String.fromEnvironment(
        'RESTWELL_API_BASE_URL',
        defaultValue: 'http://localhost:8001',
      ),
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 10),
    ),
  );
});

final clientApiProvider =
    Provider<ClientApi>((ref) => ClientApi(ref.watch(dioProvider)));
final clientControllerProvider =
    ChangeNotifierProvider<ClientController>((ref) {
  return ClientController(ref.watch(clientApiProvider));
});

class RestWellClientApp extends ConsumerWidget {
  const RestWellClientApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(clientControllerProvider).state;
    final branding = state.dashboard?['branding'] as Map<String, dynamic>?;
    final primaryColor = _hexColor(branding?['primary_color'] as String?);
    return MaterialApp(
      title: 'RestWell Client',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: primaryColor),
        useMaterial3: true,
      ),
      home: state.isSignedIn
          ? const ClientDashboardScreen()
          : const ClientLoginScreen(),
    );
  }
}

class ClientApi {
  ClientApi(this._dio);

  final Dio _dio;
  Map<String, dynamic>? _cachedDashboard;

  void setAccessToken(String? token) {
    if (token == null || token.isEmpty) {
      _dio.options.headers.remove('Authorization');
      return;
    }
    _dio.options.headers['Authorization'] = 'Bearer $token';
  }

  Future<void> login(String username, String password) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/auth/token/',
      data: {'username': username, 'password': password},
    );
    setAccessToken(response.data!['access'] as String);
  }

  Future<Map<String, dynamic>> dashboard() async {
    try {
      final response =
          await _dio.get<Map<String, dynamic>>('/api/client/dashboard/');
      _cachedDashboard = response.data!;
      return response.data!;
    } on DioException {
      if (_cachedDashboard != null) {
        return {..._cachedDashboard!, 'offline': true};
      }
      rethrow;
    }
  }

  Future<void> createSupportRequest(String subject, String message) async {
    await _dio.post<Map<String, dynamic>>(
      '/api/client/support-requests/',
      data: {'subject': subject, 'message': message},
    );
  }

  Future<void> markNotificationRead(int id) async {
    await _dio.post<Map<String, dynamic>>(
      '/api/client/notifications/$id/mark-read/',
    );
  }
}

class ClientState {
  const ClientState({
    this.isSignedIn = false,
    this.isLoading = false,
    this.dashboard,
    this.errorMessage,
  });

  final bool isSignedIn;
  final bool isLoading;
  final Map<String, dynamic>? dashboard;
  final String? errorMessage;

  ClientState copyWith({
    bool? isSignedIn,
    bool? isLoading,
    Map<String, dynamic>? dashboard,
    String? errorMessage,
  }) {
    return ClientState(
      isSignedIn: isSignedIn ?? this.isSignedIn,
      isLoading: isLoading ?? this.isLoading,
      dashboard: dashboard ?? this.dashboard,
      errorMessage: errorMessage,
    );
  }
}

class ClientController extends ChangeNotifier {
  ClientController(this._api);

  final ClientApi _api;

  ClientState state = const ClientState();

  Future<void> login(String username, String password) async {
    state = state.copyWith(isLoading: true, errorMessage: null);
    notifyListeners();
    try {
      await _api.login(username, password);
      final dashboard = await _api.dashboard();
      state = ClientState(isSignedIn: true, dashboard: dashboard);
    } on DioException {
      state = const ClientState(
          errorMessage: 'Unable to sign in. Check your details and try again.');
    }
    notifyListeners();
  }

  Future<void> refresh() async {
    state = state.copyWith(isLoading: true, errorMessage: null);
    notifyListeners();
    try {
      final dashboard = await _api.dashboard();
      state = state.copyWith(
          isSignedIn: true, isLoading: false, dashboard: dashboard);
    } on DioException {
      state = state.copyWith(
          isLoading: false, errorMessage: 'Unable to refresh right now.');
    }
    notifyListeners();
  }

  Future<void> submitSupport(String subject, String message) async {
    state = state.copyWith(isLoading: true, errorMessage: null);
    notifyListeners();
    try {
      await _api.createSupportRequest(subject, message);
      await refresh();
    } on DioException {
      state = state.copyWith(
          isLoading: false, errorMessage: 'Support request could not be sent.');
      notifyListeners();
    }
  }

  Future<void> markNotificationRead(int id) async {
    state = state.copyWith(isLoading: true, errorMessage: null);
    notifyListeners();
    try {
      await _api.markNotificationRead(id);
      await refresh();
    } on DioException {
      state = state.copyWith(
          isLoading: false, errorMessage: 'Notification could not be updated.');
      notifyListeners();
    }
  }

  void signOut() {
    _api.setAccessToken(null);
    state = const ClientState();
    notifyListeners();
  }
}

class ClientLoginScreen extends ConsumerStatefulWidget {
  const ClientLoginScreen({super.key});

  @override
  ConsumerState<ClientLoginScreen> createState() => _ClientLoginScreenState();
}

class _ClientLoginScreenState extends ConsumerState<ClientLoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _usernameController =
      TextEditingController(text: 'family@restwell.local');
  final _passwordController = TextEditingController(text: 'RestWell123!');

  @override
  void dispose() {
    _usernameController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(clientControllerProvider).state;
    return Scaffold(
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 420),
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Form(
              key: _formKey,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Text('RestWell',
                      style: Theme.of(context).textTheme.headlineMedium),
                  const SizedBox(height: 8),
                  const Text('Family portal'),
                  const SizedBox(height: 24),
                  TextFormField(
                    controller: _usernameController,
                    decoration: const InputDecoration(labelText: 'Username'),
                    validator: (value) => value == null || value.trim().isEmpty
                        ? 'Enter your username.'
                        : null,
                  ),
                  const SizedBox(height: 12),
                  TextFormField(
                    controller: _passwordController,
                    obscureText: true,
                    decoration: const InputDecoration(labelText: 'Password'),
                    validator: (value) => value == null || value.isEmpty
                        ? 'Enter your password.'
                        : null,
                  ),
                  if (state.errorMessage != null) ...[
                    const SizedBox(height: 12),
                    Text(state.errorMessage!,
                        style: TextStyle(
                            color: Theme.of(context).colorScheme.error)),
                  ],
                  const SizedBox(height: 24),
                  FilledButton(
                    onPressed: state.isLoading
                        ? null
                        : () {
                            if (!_formKey.currentState!.validate()) {
                              return;
                            }
                            ref.read(clientControllerProvider).login(
                                  _usernameController.text.trim(),
                                  _passwordController.text,
                                );
                          },
                    child: Text(state.isLoading ? 'Signing in...' : 'Sign in'),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class ClientDashboardScreen extends ConsumerWidget {
  const ClientDashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final controller = ref.read(clientControllerProvider);
    final state = ref.watch(clientControllerProvider).state;
    final dashboard = state.dashboard ?? const {};
    final tenant = dashboard['tenant'] as Map<String, dynamic>?;

    return Scaffold(
      appBar: AppBar(
        title: Text((tenant?['name'] as String?) ?? 'RestWell'),
        actions: [
          IconButton(
            tooltip: 'Refresh',
            onPressed: controller.refresh,
            icon: const Icon(Icons.refresh),
          ),
          IconButton(
            tooltip: 'Sign out',
            onPressed: controller.signOut,
            icon: const Icon(Icons.logout),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: controller.refresh,
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: [
            if (dashboard['offline'] == true)
              const Card(
                child: ListTile(
                  leading: Icon(Icons.cloud_off),
                  title: Text('Offline view'),
                  subtitle: Text(
                      'Showing the last loaded portal data. New requests need a connection.'),
                ),
              ),
            _Section(
                title: 'Family',
                rows: dashboard['family_members'] as List<dynamic>? ?? const [],
                titleKey: 'name',
                subtitleKey: 'relationship'),
            _Section(
                title: 'Cases',
                rows: dashboard['cases'] as List<dynamic>? ?? const [],
                titleKey: 'reference',
                subtitleKey: 'deceased'),
            _Section(
                title: 'Policies',
                rows: dashboard['policies'] as List<dynamic>? ?? const [],
                titleKey: 'policy_number',
                subtitleKey: 'template'),
            _Section(
                title: 'Services',
                rows: dashboard['events'] as List<dynamic>? ?? const [],
                titleKey: 'title',
                subtitleKey: 'location'),
            _NotificationSection(
                rows: dashboard['notifications'] as List<dynamic>? ?? const []),
            _Section(
                title: 'Support requests',
                rows:
                    dashboard['support_requests'] as List<dynamic>? ?? const [],
                titleKey: 'subject',
                subtitleKey: 'status'),
            const SizedBox(height: 12),
            FilledButton.icon(
              onPressed: () => _showSupportDialog(context, ref),
              icon: const Icon(Icons.support_agent),
              label: const Text('Contact support'),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _showSupportDialog(BuildContext context, WidgetRef ref) async {
    final subjectController = TextEditingController();
    final messageController = TextEditingController();
    final result = await showDialog<(String, String)>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('Contact support'),
          content: SizedBox(
            width: 420,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                    controller: subjectController,
                    decoration: const InputDecoration(labelText: 'Subject')),
                const SizedBox(height: 12),
                TextField(
                    controller: messageController,
                    decoration: const InputDecoration(labelText: 'Message'),
                    maxLines: 4),
              ],
            ),
          ),
          actions: [
            TextButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('Cancel')),
            FilledButton(
              onPressed: () {
                if (subjectController.text.trim().isEmpty ||
                    messageController.text.trim().isEmpty) {
                  return;
                }
                Navigator.pop(context, (
                  subjectController.text.trim(),
                  messageController.text.trim()
                ));
              },
              child: const Text('Send'),
            ),
          ],
        );
      },
    );
    subjectController.dispose();
    messageController.dispose();
    if (result == null) {
      return;
    }
    await ref
        .read(clientControllerProvider)
        .submitSupport(result.$1, result.$2);
  }
}

class _NotificationSection extends ConsumerWidget {
  const _NotificationSection({required this.rows});

  final List<dynamic> rows;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(top: 18, bottom: 8),
          child: Text('Notifications',
              style: Theme.of(context).textTheme.titleLarge),
        ),
        if (rows.isEmpty)
          const Card(child: ListTile(title: Text('No records yet.')))
        else
          for (final row in rows.cast<Map<String, dynamic>>())
            Card(
              child: ListTile(
                title: Text((row['subject'] ?? 'Notification').toString()),
                subtitle: Text((row['body'] ?? '').toString()),
                trailing: row['status'] == 'read'
                    ? const Icon(Icons.done, color: Colors.green)
                    : TextButton(
                        onPressed: row['id'] is int
                            ? () => ref
                                .read(clientControllerProvider)
                                .markNotificationRead(row['id'] as int)
                            : null,
                        child: const Text('Mark read'),
                      ),
              ),
            ),
      ],
    );
  }
}

class _Section extends StatelessWidget {
  const _Section({
    required this.title,
    required this.rows,
    required this.titleKey,
    required this.subtitleKey,
  });

  final String title;
  final List<dynamic> rows;
  final String titleKey;
  final String subtitleKey;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(top: 18, bottom: 8),
          child: Text(title, style: Theme.of(context).textTheme.titleLarge),
        ),
        if (rows.isEmpty)
          const Card(child: ListTile(title: Text('No records yet.')))
        else
          for (final row in rows.cast<Map<String, dynamic>>())
            Card(
              child: ListTile(
                title: Text((row[titleKey] ?? 'Record').toString()),
                subtitle: Text((row[subtitleKey] ?? '').toString()),
              ),
            ),
      ],
    );
  }
}

Color _hexColor(String? value) {
  if (value == null || !RegExp(r'^#[0-9A-Fa-f]{6}$').hasMatch(value)) {
    return const Color(0xFF0F766E);
  }
  return Color(int.parse(value.substring(1), radix: 16) + 0xFF000000);
}
