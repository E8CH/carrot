import '../../../core/api/api_client.dart';
import '../../../core/api/api_endpoints.dart';

class AuthRepository {
  final ApiClient _client;
  const AuthRepository(this._client);

  Future<Map<String, dynamic>> register({
    required String email,
    required String password,
    required String address,
    required String phone,
  }) async {
    final result = await _client.post(
      ApiEndpoints.authRegister,
      body: {
        'email': email,
        'password': password,
        'address': address,
        'phone': phone,
      },
    );
    return result as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> login({
    required String email,
    required String password,
  }) async {
    final result = await _client.post(
      ApiEndpoints.authLogin,
      body: {'email': email, 'password': password},
    );
    return result as Map<String, dynamic>;
  }
}
