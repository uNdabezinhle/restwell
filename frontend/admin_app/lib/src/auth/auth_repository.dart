import '../api/restwell_api_client.dart';
import 'token_storage.dart';

class AuthRepository {
  AuthRepository({
    required RestWellApiClient apiClient,
    required TokenStorage tokenStorage,
  })  : _apiClient = apiClient,
        _tokenStorage = tokenStorage;

  final RestWellApiClient _apiClient;
  final TokenStorage _tokenStorage;

  Future<CurrentUser> login({
    required String username,
    required String password,
  }) async {
    final tokenPair = await _apiClient.login(username: username, password: password);
    await _tokenStorage.save(tokenPair);
    _apiClient.setAccessToken(tokenPair.access);
    return _apiClient.fetchCurrentUser();
  }

  Future<void> signOut() async {
    await _tokenStorage.clear();
    _apiClient.setAccessToken(null);
  }
}
