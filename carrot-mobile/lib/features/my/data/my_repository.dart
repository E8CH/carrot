import '../../../core/api/api_client.dart';
import '../../../core/api/api_endpoints.dart';

class MyRepository {
  final ApiClient _client;
  const MyRepository(this._client);

  Future<Map<String, dynamic>> getMe() async {
    final result = await _client.get(ApiEndpoints.usersMe);
    return result as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> getMyPosts({String? status}) async {
    final result = await _client.get(
      ApiEndpoints.usersMePosts,
      queryParams: status != null ? {'status': status} : null,
    );
    return result as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> getMyPurchases() async {
    final result = await _client.get(ApiEndpoints.usersMePurchases);
    return result as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> getMyLikes() async {
    final result = await _client.get(ApiEndpoints.usersMeLikes);
    return result as Map<String, dynamic>;
  }
}
