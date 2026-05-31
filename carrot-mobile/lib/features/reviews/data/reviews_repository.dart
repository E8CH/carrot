import '../../../core/api/api_client.dart';
import '../../../core/api/api_endpoints.dart';

class ReviewsRepository {
  final ApiClient _client;
  const ReviewsRepository(this._client);

  Future<Map<String, dynamic>> submitReview({
    required int postId,
    required bool isPositive,
    required List<String> tags,
    String? comment,
  }) async {
    final result = await _client.post(
      ApiEndpoints.reviews,
      body: {
        'post_id': postId,
        'is_positive': isPositive,
        'tags': tags,
        'comment': comment,
      },
    );
    return result as Map<String, dynamic>;
  }
}
