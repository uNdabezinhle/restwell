import '../api/restwell_api_client.dart';

abstract class TokenStorage {
  Future<void> save(TokenPair tokenPair);
  Future<TokenPair?> read();
  Future<void> clear();
}

class InMemoryTokenStorage implements TokenStorage {
  TokenPair? _tokenPair;

  @override
  Future<void> save(TokenPair tokenPair) async {
    _tokenPair = tokenPair;
  }

  @override
  Future<TokenPair?> read() async => _tokenPair;

  @override
  Future<void> clear() async {
    _tokenPair = null;
  }
}
