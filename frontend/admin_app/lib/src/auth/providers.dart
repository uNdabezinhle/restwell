import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../api/restwell_api_client.dart';
import 'auth_controller.dart';
import 'auth_repository.dart';
import 'token_storage.dart';

final dioProvider = Provider<Dio>((ref) {
  return Dio(
    BaseOptions(
      baseUrl: const String.fromEnvironment(
        'RESTWELL_API_BASE_URL',
        defaultValue: 'http://localhost:8000',
      ),
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 10),
    ),
  );
});

final apiClientProvider = Provider<RestWellApiClient>((ref) {
  return RestWellApiClient(ref.watch(dioProvider));
});

final tokenStorageProvider = Provider<TokenStorage>((ref) {
  return InMemoryTokenStorage();
});

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  return AuthRepository(
    apiClient: ref.watch(apiClientProvider),
    tokenStorage: ref.watch(tokenStorageProvider),
  );
});

final authControllerProvider = ChangeNotifierProvider<AuthController>((ref) {
  return AuthController(ref.watch(authRepositoryProvider));
});
