import '../../../core/api/api_client.dart';
import '../../../core/api/api_endpoints.dart';

class ChatsRepository {
  final ApiClient _client;
  const ChatsRepository(this._client);

  Future<Map<String, dynamic>> getUnreadCount() async {
    final result = await _client.get(ApiEndpoints.chatsUnreadCount);
    return result as Map<String, dynamic>;
  }

  Future<void> markAsRead(String roomId) async {
    try {
      await _client.patch(ApiEndpoints.chatRead(roomId));
    } catch (_) {}
  }

  Future<List<Map<String, dynamic>>> getChatRooms() async {
    final result = await _client.get(ApiEndpoints.chats);
    return (result as List).cast<Map<String, dynamic>>();
  }

  Future<Map<String, dynamic>> createOrGetRoom(int postId) async {
    final result = await _client.post(
      ApiEndpoints.chats,
      body: {'post_id': postId},
    );
    return result as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> sendMessage(
    String roomId,
    String message,
    int postId,
  ) async {
    final result = await _client.post(
      '${ApiEndpoints.chats}$roomId/messages',
      body: {'message': message, 'post_id': postId},
    );
    return result as Map<String, dynamic>;
  }

  Future<List<Map<String, dynamic>>> getMessages(
    String roomId, {
    int? afterId,
  }) async {
    final result = await _client.get(
      '${ApiEndpoints.chats}$roomId/messages',
      queryParams: afterId != null ? {'after': afterId.toString()} : null,
    );
    return (result as List).cast<Map<String, dynamic>>();
  }
}
