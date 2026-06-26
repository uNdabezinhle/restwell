import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';

import '../api/restwell_api_client.dart';
import 'auth_repository.dart';

enum AuthStatus { signedOut, loading, signedIn, failure }

class AuthState {
  const AuthState({
    required this.status,
    this.user,
    this.errorMessage,
  });

  const AuthState.signedOut() : this(status: AuthStatus.signedOut);

  final AuthStatus status;
  final CurrentUser? user;
  final String? errorMessage;
}

class AuthController extends ChangeNotifier {
  AuthController(this._repository);

  final AuthRepository _repository;

  AuthState state = const AuthState.signedOut();

  Future<void> login({
    required String username,
    required String password,
  }) async {
    state = const AuthState(status: AuthStatus.loading);
    notifyListeners();

    try {
      final user = await _repository.login(username: username, password: password);
      state = AuthState(status: AuthStatus.signedIn, user: user);
    } on DioException {
      state = const AuthState(
        status: AuthStatus.failure,
        errorMessage: 'Invalid username or password.',
      );
    } catch (_) {
      state = const AuthState(
        status: AuthStatus.failure,
        errorMessage: 'Unable to sign in. Please try again.',
      );
    }
    notifyListeners();
  }

  Future<void> signOut() async {
    await _repository.signOut();
    state = const AuthState.signedOut();
    notifyListeners();
  }
}
