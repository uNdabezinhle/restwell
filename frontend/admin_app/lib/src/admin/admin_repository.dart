import '../api/restwell_api_client.dart';

class DashboardSummary {
  const DashboardSummary({
    required this.operations,
    required this.commercial,
    required this.digital,
  });

  final Map<String, dynamic> operations;
  final Map<String, dynamic> commercial;
  final Map<String, dynamic> digital;

  factory DashboardSummary.fromJson(Map<String, dynamic> json) {
    return DashboardSummary(
      operations: (json['operations'] as Map<String, dynamic>?) ?? const {},
      commercial: (json['commercial'] as Map<String, dynamic>?) ?? const {},
      digital: (json['digital'] as Map<String, dynamic>?) ?? const {},
    );
  }
}

class TenantFeature {
  const TenantFeature({
    required this.id,
    required this.code,
    required this.isEnabled,
  });

  final int id;
  final String code;
  final bool isEnabled;

  factory TenantFeature.fromJson(Map<String, dynamic> json) {
    return TenantFeature(
      id: (json['id'] as int?) ?? 0,
      code: (json['code'] as String?) ?? '',
      isEnabled: (json['is_enabled'] as bool?) ?? true,
    );
  }
}

class AdminRepository {
  const AdminRepository(this._apiClient);

  final RestWellApiClient _apiClient;

  Future<DashboardSummary> fetchDashboardSummary() async {
    final json = await _apiClient.fetchObject('/api/dashboard/summary/');
    return DashboardSummary.fromJson(json);
  }

  Future<List<TenantFeature>> fetchFeatures() async {
    final rows = await _apiClient.fetchList('/api/features/');
    return rows.map(TenantFeature.fromJson).toList();
  }

  Future<List<Map<String, dynamic>>> fetchModuleRows(String path) {
    return _apiClient.fetchList(path);
  }

  Future<Map<String, dynamic>> createRecord(
      String path, Map<String, dynamic> data) {
    return _apiClient.create(path, data);
  }

  Future<Map<String, dynamic>> runWorkflow(String path,
      [Map<String, dynamic>? data]) {
    return _apiClient.post(path, data);
  }

  Future<TenantFeature> updateFeature(int id, bool isEnabled) async {
    final json = await _apiClient.patch('/api/features/$id/', {
      'is_enabled': isEnabled,
    });
    return TenantFeature.fromJson(json);
  }
}
