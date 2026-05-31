import '../../../core/api/api_client.dart';
import '../../../core/api/api_endpoints.dart';

class PostsRepository {
  final ApiClient _client;
  const PostsRepository(this._client);

  Future<Map<String, dynamic>> getPosts({int page = 1, int size = 20}) async {
    final result = await _client.get(
      ApiEndpoints.posts,
      queryParams: {'page': '$page', 'size': '$size'},
    );
    return result as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> getUploadUrl() async {
    final result = await _client.post(ApiEndpoints.postsUploadUrl);
    return result as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> createPost({
    required String title,
    required String description,
    int? price,
    bool isFree = false,
    String? tradePlace,
    required List<String> photos,
  }) async {
    final result = await _client.post(
      ApiEndpoints.posts,
      body: {
        'title': title,
        'description': description,
        'price': price,
        'is_free': isFree,
        'trade_place': tradePlace,
        'photos': photos,
      },
    );
    return result as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> getPost(int id) async {
    final result = await _client.get(ApiEndpoints.postDetail(id));
    return result as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> updatePost(int id, Map<String, dynamic> body) async {
    final result = await _client.patch(ApiEndpoints.postDetail(id), body: body);
    return result as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> changeStatus(int id, String status) async {
    final result = await _client.patch(
      ApiEndpoints.postStatus(id),
      body: {'status': status},
    );
    return result as Map<String, dynamic>;
  }

  Future<List<String>> getPostBuyers(int id) async {
    final result = await _client.get(ApiEndpoints.postBuyers(id));
    final data = result as Map<String, dynamic>;
    final buyers = (data['buyers'] as List?) ?? [];
    return buyers
        .map((b) => (b as Map<String, dynamic>)['buyer_email'] as String)
        .toList();
  }

  Future<Map<String, dynamic>> completePost(int id, String buyerEmail) async {
    final result = await _client.patch(
      ApiEndpoints.postComplete(id),
      body: {'buyer_email': buyerEmail},
    );
    return result as Map<String, dynamic>;
  }

  Future<void> deletePost(int id) async {
    try {
      await _client.delete(ApiEndpoints.postDetail(id));
    } on FormatException {
      // 204 No Content — 빈 body로 인한 FormatException 무시
    }
  }

  Future<Map<String, dynamic>> toggleLike(int id) async {
    final result = await _client.post(ApiEndpoints.postLike(id));
    return result as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>?> getDraft() async {
    try {
      final result = await _client.get(ApiEndpoints.postsDraft);
      return result as Map<String, dynamic>;
    } on ApiException catch (e) {
      if (e.statusCode == 404) return null;
      rethrow;
    }
  }

  Future<Map<String, dynamic>> saveDraft({
    required String title,
    required String description,
    int? price,
    bool isFree = false,
    String? tradePlace,
    List<String> photos = const [],
  }) async {
    final result = await _client.post(
      ApiEndpoints.postsDraft,
      body: {
        'title': title,
        'description': description,
        'price': price,
        'is_free': isFree,
        'trade_place': tradePlace,
        'photos': photos,
      },
    );
    return result as Map<String, dynamic>;
  }
}
