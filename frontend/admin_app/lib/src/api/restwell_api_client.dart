import 'package:dio/dio.dart';

class TokenPair {
  const TokenPair({required this.access, required this.refresh});

  final String access;
  final String refresh;

  factory TokenPair.fromJson(Map<String, dynamic> json) {
    return TokenPair(
      access: json['access'] as String,
      refresh: json['refresh'] as String,
    );
  }
}

class CurrentUser {
  const CurrentUser({
    required this.id,
    required this.username,
    required this.email,
    required this.role,
    required this.tenant,
    required this.tenantName,
    required this.branch,
    required this.branchName,
  });

  final int id;
  final String username;
  final String email;
  final String role;
  final int? tenant;
  final String? tenantName;
  final int? branch;
  final String? branchName;

  factory CurrentUser.fromJson(Map<String, dynamic> json) {
    return CurrentUser(
      id: json['id'] as int,
      username: json['username'] as String,
      email: (json['email'] as String?) ?? '',
      role: json['role'] as String,
      tenant: json['tenant'] as int?,
      tenantName: json['tenant_name'] as String?,
      branch: json['branch'] as int?,
      branchName: json['branch_name'] as String?,
    );
  }
}

class RestWellApiClient {
  RestWellApiClient(this._dio);

  final Dio _dio;

  void setAccessToken(String? token) {
    if (token == null || token.isEmpty) {
      _dio.options.headers.remove('Authorization');
      return;
    }
    _dio.options.headers['Authorization'] = 'Bearer $token';
  }

  Future<TokenPair> login({
    required String username,
    required String password,
  }) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/auth/token/',
      data: {'username': username, 'password': password},
    );
    return TokenPair.fromJson(response.data!);
  }

  Future<CurrentUser> fetchCurrentUser() async {
    final response = await _dio.get<Map<String, dynamic>>('/api/accounts/me/');
    return CurrentUser.fromJson(response.data!);
  }
}
