import 'dart:convert';
import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:restwell_admin_app/src/api/restwell_api_client.dart';
import 'package:restwell_admin_app/src/auth/auth_controller.dart';
import 'package:restwell_admin_app/src/auth/auth_repository.dart';
import 'package:restwell_admin_app/src/auth/token_storage.dart';

void main() {
  test('logs in and loads current user through Dio', () async {
    final adapter = StubAdapter({
      'POST /api/auth/token/': StubResponse(200, {
        'access': 'access-token',
        'refresh': 'refresh-token',
      }),
      'GET /api/accounts/me/': StubResponse(200, {
        'id': 1,
        'username': 'director',
        'email': 'director@example.com',
        'role': 'tenant_admin',
        'tenant': 10,
        'tenant_name': 'Dignity Care',
        'branch': 20,
        'branch_name': 'Johannesburg',
      }),
    });
    final controller = buildController(adapter);

    await controller.login(username: 'director', password: 'test-password');

    expect(controller.state.status, AuthStatus.signedIn);
    expect(controller.state.user?.username, 'director');
    expect(adapter.requests.last.headers['Authorization'], 'Bearer access-token');
  });

  test('shows invalid credentials error from Dio failure', () async {
    final adapter = StubAdapter({
      'POST /api/auth/token/': StubResponse(401, {'detail': 'No active account'}),
    });
    final controller = buildController(adapter);

    await controller.login(username: 'director', password: 'wrong');

    expect(controller.state.status, AuthStatus.failure);
    expect(controller.state.errorMessage, 'Invalid username or password.');
  });
}

AuthController buildController(StubAdapter adapter) {
  final dio = Dio(BaseOptions(baseUrl: 'http://restwell.test'));
  dio.httpClientAdapter = adapter;
  final apiClient = RestWellApiClient(dio);
  final repository = AuthRepository(
    apiClient: apiClient,
    tokenStorage: InMemoryTokenStorage(),
  );
  return AuthController(repository);
}

class StubResponse {
  const StubResponse(this.statusCode, this.body);

  final int statusCode;
  final Map<String, dynamic> body;
}

class StubAdapter implements HttpClientAdapter {
  StubAdapter(this.responses);

  final Map<String, StubResponse> responses;
  final List<RequestOptions> requests = [];

  @override
  Future<ResponseBody> fetch(
    RequestOptions options,
    Stream<Uint8List>? requestStream,
    Future<void>? cancelFuture,
  ) async {
    requests.add(options);
    final key = '${options.method} ${options.path}';
    final response = responses[key];
    if (response == null) {
      return ResponseBody.fromString(
        jsonEncode({'detail': 'Not found'}),
        404,
        headers: {
          Headers.contentTypeHeader: [Headers.jsonContentType],
        },
      );
    }

    return ResponseBody.fromString(
      jsonEncode(response.body),
      response.statusCode,
      headers: {
        Headers.contentTypeHeader: [Headers.jsonContentType],
      },
    );
  }

  @override
  void close({bool force = false}) {}
}
